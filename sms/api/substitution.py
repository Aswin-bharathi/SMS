"""
Staff Substitution workflow.
"""
import json
import frappe
from frappe import _
from frappe.utils import getdate, nowdate


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════
def _is_admin_or_hod(user=None):
    user = user or frappe.session.user
    if user == "Administrator":
        return True
    roles = frappe.get_roles(user)
    return any(r in roles for r in ("System Manager", "SMS Admin", "SMS HOD"))


# ════════════════════════════════════════════════════════════════════════════
# Find available faculty for a date+hour
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_available_faculty(date, hour, department=None, exclude=None):
    """
    Return faculty who are FREE at the given date+hour.
    Excludes anyone who is teaching another class at the same time.
    """
    if not date or not hour:
        frappe.throw(_("Date and Hour are required"))

    target_date = getdate(date)
    day_name = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"][target_date.weekday()]

    # Get all SMS Staff users
    candidates = frappe.db.sql("""
        SELECT u.name, u.full_name
        FROM `tabUser` u
        INNER JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = 'SMS Staff'
          AND u.enabled = 1
        ORDER BY u.full_name
    """, as_dict=True)

    # Find who is teaching at that day+hour
    busy_users = set(frappe.db.sql_list("""
        SELECT DISTINCT ts.faculty
        FROM `tabTimetable Slot` ts
        INNER JOIN `tabTimetable` tt ON tt.name = ts.parent
        WHERE ts.day = %(day)s
          AND ts.hour = %(hour)s
          AND ts.faculty IS NOT NULL
          AND tt.is_active = 1
    """, {"day": day_name, "hour": hour}))

    # Also exclude those already substituting at this date+hour
    busy_users.update(frappe.db.sql_list("""
        SELECT substitute_faculty
        FROM `tabStaff Substitution`
        WHERE date = %(date)s
          AND hour = %(hour)s
          AND status = 'Approved'
    """, {"date": target_date, "hour": hour}))

    if exclude:
        busy_users.add(exclude)

    available = [c for c in candidates if c.name not in busy_users]

    # Filter by department if specified
    if department:
        # Get faculty from same department via Subject Faculty Map
        dept_faculty = set(frappe.db.sql_list("""
            SELECT DISTINCT sfm.faculty
            FROM `tabSubject Faculty Map` sfm
            INNER JOIN `tabSubject` s ON s.name = sfm.subject
            WHERE s.department = %(dept)s
        """, {"dept": department}))
        if dept_faculty:
            available = [a for a in available if a.name in dept_faculty]

    return {
        "date":        str(target_date),
        "day":         day_name,
        "hour":        hour,
        "available":   available,
        "busy_count":  len(busy_users),
    }


# ════════════════════════════════════════════════════════════════════════════
# CRUD
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def request_substitution(data):
    """
    A faculty requests substitution for one of their classes.
    HOD/Admin can request on behalf of any faculty.
    """
    if isinstance(data, str):
        data = json.loads(data)

    required = ["date", "hour", "timetable_slot", "substitute_faculty"]
    for r in required:
        if not data.get(r):
            frappe.throw(_("{0} is required").format(r.replace("_", " ").title()))

    # Get original faculty from the slot
    original = frappe.db.get_value(
        "Timetable Slot", data["timetable_slot"], "faculty"
    )
    if not original:
        frappe.throw(_("Slot has no assigned faculty"))

    # Get batch from parent timetable
    parent_tt = frappe.db.get_value(
        "Timetable Slot", data["timetable_slot"], "parent"
    )
    batch = frappe.db.get_value("Timetable", parent_tt, "batch")

    # Check authorization
    user = frappe.session.user
    if not _is_admin_or_hod(user) and user != original:
        frappe.throw(_("You can only request substitution for your own classes"))

    # Prevent duplicate requests
    existing = frappe.db.exists("Staff Substitution", {
        "date": data["date"],
        "hour": data["hour"],
        "timetable_slot": data["timetable_slot"],
        "status": ["in", ["Pending", "Approved"]],
    })
    if existing:
        frappe.throw(_("A substitution request already exists for this slot/date"))

    doc = frappe.get_doc({
        "doctype":            "Staff Substitution",
        "date":               data["date"],
        "hour":               data["hour"],
        "timetable_slot":     data["timetable_slot"],
        "batch":              batch,
        "original_faculty":   original,
        "substitute_faculty": data["substitute_faculty"],
        "reason":             data.get("reason", ""),
        "status":             "Approved" if _is_admin_or_hod(user) else "Pending",
        "requested_by":       user,
        "approved_by":        user if _is_admin_or_hod(user) else None,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "status": doc.status, "message": "Substitution requested"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def approve_substitution(name):
    """HOD/Admin approves a pending substitution."""
    if not _is_admin_or_hod():
        frappe.throw(_("Only HOD/Admin can approve substitutions"))

    doc = frappe.get_doc("Staff Substitution", name)
    if doc.status != "Pending":
        frappe.throw(_("Only Pending substitutions can be approved"))

    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Substitution approved"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def reject_substitution(name, reason=""):
    if not _is_admin_or_hod():
        frappe.throw(_("Only HOD/Admin can reject substitutions"))

    doc = frappe.get_doc("Staff Substitution", name)
    doc.status = "Rejected"
    doc.approved_by = frappe.session.user
    if reason:
        doc.reason = (doc.reason or "") + f"\n\n[REJECTED]: {reason}"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Substitution rejected"}


@frappe.whitelist(allow_guest=True)
def list_substitutions(status=None, faculty=None, from_date=None, to_date=None):
    """List substitution requests."""
    filters = {}
    if status:
        filters["status"] = status
    if faculty:
        filters["original_faculty"] = faculty
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]

    rows = frappe.get_all(
        "Staff Substitution",
        filters=filters,
        fields=["name", "date", "hour", "batch", "timetable_slot",
                "original_faculty", "substitute_faculty",
                "reason", "status", "requested_by", "approved_by", "creation"],
        order_by="date desc, hour asc",
        limit_page_length=0,
    )

    # Enrich
    for r in rows:
        for field in ["original_faculty", "substitute_faculty",
                      "requested_by", "approved_by"]:
            email = r.get(field)
            if email:
                r[field + "_name"] = frappe.db.get_value("User", email, "full_name") or email
        if r.get("timetable_slot"):
            slot_subj = frappe.db.get_value(
                "Timetable Slot", r["timetable_slot"], "subject"
            )
            if slot_subj:
                r["subject"] = slot_subj
                r["subject_name"] = frappe.db.get_value(
                    "Subject", slot_subj, "subject_name"
                )

    return rows
