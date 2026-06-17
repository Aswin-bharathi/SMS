"""
Timetable management.
"""
import json
import frappe
from frappe import _
from frappe.utils import getdate, nowdate


# ════════════════════════════════════════════════════════════════════════════
# Day-of-week helper
# ════════════════════════════════════════════════════════════════════════════
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _day_name(date_str):
    """Convert a date string to day name (Monday, Tuesday, etc.)"""
    return DAYS[getdate(date_str).weekday()]


# ════════════════════════════════════════════════════════════════════════════
# READ
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def list_timetables(batch=None, is_active=None):
    """List timetables, optionally filtered by batch."""
    filters = {}
    if batch:
        filters["batch"] = batch
    if is_active is not None:
        filters["is_active"] = int(is_active)

    tables = frappe.get_all(
        "Timetable",
        filters=filters,
        fields=[
            "name", "batch", "semester", "academic_year",
            "effective_from", "effective_to", "is_active",
            "created_by_hod",
        ],
        order_by="modified desc",
        limit_page_length=0,
    )

    # Add slot count + department
    for tt in tables:
        tt["slot_count"] = frappe.db.count("Timetable Slot", {"parent": tt["name"]})
        batch_doc = frappe.db.get_value(
            "Batch", tt["batch"],
            ["department", "batch_year", "current_semester"],
            as_dict=True,
        ) or {}
        tt["department"] = batch_doc.get("department")
        tt["batch_year"] = batch_doc.get("batch_year")

    return tables


@frappe.whitelist(allow_guest=True)
def get_timetable_grid(batch, semester=None):
    """
    Returns the timetable as a 2D grid:
    {
      days: [Monday, Tuesday, ...],
      hours: [{label, start, end, is_break}, ...],
      grid: { "Monday": { "Hour 1": {subject, faculty, room, is_lab}, ... } }
    }
    """
    if not batch:
        return {"days": [], "hours": [], "grid": {}}

    filters = {"batch": batch, "is_active": 1}
    if semester:
        filters["semester"] = semester

    tt_name = frappe.db.get_value("Timetable", filters, "name")
    if not tt_name:
        return {"days": [], "hours": [], "grid": {}, "timetable": None}

    hours = frappe.get_all(
        "Hour Slot",
        fields=["name", "hour_label", "start_time", "end_time", "is_break", "hour_number"],
        order_by="display_order asc",
        limit_page_length=0,
    )

    slots = frappe.get_all(
        "Timetable Slot",
        filters={"parent": tt_name},
        fields=["name", "day", "hour", "subject", "faculty", "room", "is_lab", "notes"],
        limit_page_length=0,
    )

    # Build grid: day → hour → slot
    grid = {day: {} for day in DAYS[:6]}  # Mon-Sat

    # Enrich each slot with display names
    for s in slots:
        if s["faculty"]:
            s["faculty_name"] = frappe.db.get_value("User", s["faculty"], "full_name") or s["faculty"]
        if s["subject"]:
            s["subject_name"] = frappe.db.get_value("Subject", s["subject"], "subject_name") or s["subject"]
        grid[s["day"]][s["hour"]] = s

    return {
        "timetable": tt_name,
        "batch": batch,
        "semester": semester,
        "days": DAYS[:6],
        "hours": hours,
        "grid": grid,
    }


@frappe.whitelist(allow_guest=True)
def get_my_classes_today(date=None, user=None):
    """
    Return all classes assigned to current user for the given date.
    Considers active substitutions.
    """
    if not user:
        user = frappe.session.user

    if user in ("Guest", "Administrator"):
        return {"date": date or nowdate(), "day": None, "classes": []}

    target_date = date or nowdate()
    day = _day_name(target_date)

    # Get all timetable slots where this user is the faculty
    own_slots = frappe.db.sql("""
        SELECT
            ts.name             AS slot_id,
            ts.day              AS day,
            ts.hour             AS hour,
            ts.subject          AS subject,
            ts.faculty          AS original_faculty,
            ts.room             AS room,
            ts.is_lab           AS is_lab,
            tt.name             AS timetable,
            tt.batch            AS batch,
            tt.semester         AS semester
        FROM `tabTimetable Slot` ts
        INNER JOIN `tabTimetable` tt ON tt.name = ts.parent
        WHERE ts.day = %(day)s
          AND ts.faculty = %(user)s
          AND tt.is_active = 1
        ORDER BY ts.hour
    """, {"day": day, "user": user}, as_dict=True)

    # Get slots where someone else asked this user to substitute
    sub_slots = frappe.db.sql("""
        SELECT
            ts.name             AS slot_id,
            ts.day              AS day,
            ts.hour             AS hour,
            ts.subject          AS subject,
            ts.faculty          AS original_faculty,
            ts.room             AS room,
            ts.is_lab           AS is_lab,
            tt.name             AS timetable,
            tt.batch            AS batch,
            tt.semester         AS semester,
            sub.name            AS substitution_id,
            sub.reason          AS sub_reason
        FROM `tabStaff Substitution` sub
        INNER JOIN `tabTimetable Slot` ts ON ts.name = sub.timetable_slot
        INNER JOIN `tabTimetable` tt ON tt.name = ts.parent
        WHERE sub.date = %(date)s
          AND sub.substitute_faculty = %(user)s
          AND sub.status = 'Approved'
    """, {"date": target_date, "user": user}, as_dict=True)

    # Mark slots where this user has been REPLACED by a substitute
    replaced_slot_ids = frappe.db.sql("""
        SELECT timetable_slot
        FROM `tabStaff Substitution`
        WHERE date = %(date)s
          AND original_faculty = %(user)s
          AND status = 'Approved'
    """, {"date": target_date, "user": user}, pluck="timetable_slot")

    # Filter out own_slots that have been substituted away
    own_slots = [s for s in own_slots if s["slot_id"] not in replaced_slot_ids]

    # Enrich both lists
    def enrich(slot, is_substitute=False):
        slot["is_substitute"] = is_substitute
        slot["hour_details"] = frappe.db.get_value(
            "Hour Slot", slot["hour"],
            ["start_time", "end_time", "hour_number"],
            as_dict=True,
        ) or {}
        if slot.get("subject"):
            slot["subject_name"] = frappe.db.get_value(
                "Subject", slot["subject"], "subject_name"
            ) or slot["subject"]
        slot["batch_details"] = frappe.db.get_value(
            "Batch", slot["batch"],
            ["department", "batch_year", "year_level", "status"],
            as_dict=True,
        ) or {}
        # Has attendance been marked yet?
        slot["attendance_marked"] = frappe.db.count(
            "Student Attendance",
            {"timetable_slot": slot["slot_id"], "date": target_date},
        )
        slot["student_count"] = frappe.db.count(
            "Student", {"batch": slot["batch"], "status": "Active"}
        )
        return slot

    classes = [enrich(s) for s in own_slots]
    classes += [enrich(s, is_substitute=True) for s in sub_slots]

    # Sort by hour number
    classes.sort(key=lambda x: x.get("hour_details", {}).get("hour_number") or 0)

    return {
        "date": str(target_date),
        "day": day,
        "user": user,
        "classes": classes,
        "total": len(classes),
    }


# ════════════════════════════════════════════════════════════════════════════
# CREATE / UPDATE / DELETE
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_timetable(data):
    """HOD creates a new timetable for a batch + semester."""
    if isinstance(data, str):
        data = json.loads(data)

    if not data.get("batch"):
        frappe.throw(_("Batch is required"))
    if not data.get("semester"):
        frappe.throw(_("Semester is required"))

    # Check for duplicate
    existing = frappe.db.exists("Timetable", {
        "batch": data["batch"],
        "semester": data["semester"],
    })
    if existing:
        frappe.throw(_(
            "Timetable already exists for this batch and semester: {0}"
        ).format(existing))

    doc = frappe.get_doc({
        "doctype":        "Timetable",
        "batch":          data["batch"],
        "semester":       data["semester"],
        "academic_year":  data.get("academic_year"),
        "effective_from": data.get("effective_from"),
        "effective_to":   data.get("effective_to"),
        "is_active":      1 if data.get("is_active", 1) else 0,
        "created_by_hod": frappe.session.user,
        "slots":          data.get("slots", []),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": "Timetable created"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_timetable_slot(slot_id, data):
    """Update a single timetable slot (called from grid editor)."""
    if isinstance(data, str):
        data = json.loads(data)

    if not frappe.db.exists("Timetable Slot", slot_id):
        frappe.throw(_("Slot not found"))

    fields = ["subject", "faculty", "room", "is_lab", "notes"]
    for f in fields:
        if f in data:
            frappe.db.set_value("Timetable Slot", slot_id, f, data[f])

    frappe.db.commit()
    return {"message": "Slot updated"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def add_slot_to_timetable(timetable, slot_data):
    """Add a new slot to an existing timetable."""
    if isinstance(slot_data, str):
        slot_data = json.loads(slot_data)

    tt = frappe.get_doc("Timetable", timetable)
    tt.append("slots", {
        "day":     slot_data["day"],
        "hour":    slot_data["hour"],
        "subject": slot_data.get("subject"),
        "faculty": slot_data.get("faculty"),
        "room":    slot_data.get("room"),
        "is_lab":  1 if slot_data.get("is_lab") else 0,
        "notes":   slot_data.get("notes"),
    })
    tt.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Slot added", "slot_name": tt.slots[-1].name}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def remove_slot(slot_id):
    """Remove a slot from its parent timetable."""
    frappe.delete_doc("Timetable Slot", slot_id, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Slot removed"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def delete_timetable(name):
    """Delete an entire timetable."""
    # Check if any attendance has been marked against this timetable's slots
    slot_ids = frappe.get_all("Timetable Slot",
        filters={"parent": name}, pluck="name")
    if slot_ids:
        used = frappe.db.count("Student Attendance",
            {"timetable_slot": ["in", slot_ids]})
        if used > 0:
            frappe.throw(_(
                "Cannot delete — {0} attendance record(s) reference this timetable. "
                "Deactivate it instead."
            ).format(used))

    frappe.delete_doc("Timetable", name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Timetable deleted"}
