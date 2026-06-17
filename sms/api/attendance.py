"""
Attendance management — class-in-charge based.
"""
import json
import frappe
from frappe import _
from frappe.utils import nowdate, getdate


# ════════════════════════════════════════════════════════════════════════════
# Helper: auto-detect the date column name
# ════════════════════════════════════════════════════════════════════════════
def _date_column():
    """Auto-detect the date column on Student Attendance."""
    for candidate in ("date", "attendance_date", "att_date"):
        if frappe.db.has_column("Student Attendance", candidate):
            return candidate
    return "date"


# ════════════════════════════════════════════════════════════════════════════
# Permission helper
# ════════════════════════════════════════════════════════════════════════════
def _user_can_mark_batch(batch):
    """
    True if current user is Administrator, System Manager,
    or the class in-charge of this batch.
    """
    user = frappe.session.user
    roles = frappe.get_roles(user)

    if user == "Administrator" or "System Manager" in roles:
        return True

    incharge = frappe.db.get_value("Batch", batch, "class_in_charge")
    return incharge == user


@frappe.whitelist(allow_guest=True)
def can_mark_batch(batch):
    """Frontend uses this to show/hide the 'Mark Attendance' button."""
    return {"allowed": _user_can_mark_batch(batch)}


# ════════════════════════════════════════════════════════════════════════════
# Roster: students of a batch + existing attendance for given date/hour
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_batch_roster(batch, date=None, hour=None):
    """Return students of the batch with their attendance prefilled."""
    if not batch:
        return []

    students = frappe.get_all(
        "Student",
        filters={"batch": batch, "status": "Active"},
        fields=["name", "student_id", "roll_number", "full_name"],
        order_by="roll_number asc",
        limit_page_length=0,
    )

    existing = {}
    if date and hour:
        dc = _date_column()
        rows = frappe.get_all(
            "Student Attendance",
            filters={"batch": batch, dc: date, "hour": hour},
            fields=["name", "student", "status", "remarks"],
        )
        existing = {r.student: r for r in rows}

    for s in students:
        rec = existing.get(s["name"])
        s["status"] = rec["status"] if rec else "Present"
        s["remarks"] = rec["remarks"] if rec else ""
        s["attendance_id"] = rec["name"] if rec else None

    return students


# ════════════════════════════════════════════════════════════════════════════
# Bulk mark / update attendance
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def mark_attendance_bulk(batch, date, hour, records):
    """
    records = [{student, status, remarks}, ...]
    Only the class-in-charge (or admin) may call this.
    """
    if isinstance(records, str):
        records = json.loads(records)

    if not _user_can_mark_batch(batch):
        frappe.throw(
            _("You are not authorized to mark attendance for this batch.")
        )

    if not date or not hour:
        frappe.throw(_("Date and Hour are required."))

    department = frappe.db.get_value("Batch", batch, "department")
    user = frappe.session.user
    dc = _date_column()

    created, updated = 0, 0

    for r in records:
        student = r.get("student")
        if not student:
            continue

        existing = frappe.db.exists("Student Attendance", {
            "student": student,
            dc: date,
            "hour": hour,
        })

        if existing:
            doc = frappe.get_doc("Student Attendance", existing)
            doc.status = r.get("status", "Present")
            doc.remarks = r.get("remarks", "")
            doc.marked_by = user
            doc.batch = batch
            doc.department = department
            doc.save(ignore_permissions=True)
            updated += 1
        else:
            new_doc = {
                "doctype": "Student Attendance",
                "student": student,
                "department": department,
                "batch": batch,
                "hour": hour,
                "status": r.get("status", "Present"),
                "remarks": r.get("remarks", ""),
                "marked_by": user,
            }
            new_doc[dc] = date
            frappe.get_doc(new_doc).insert(ignore_permissions=True)
            created += 1

    frappe.db.commit()
    return {
        "message": _("Attendance saved successfully."),
        "created": created,
        "updated": updated,
        "total": created + updated,
    }


# ════════════════════════════════════════════════════════════════════════════
# Reports
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_attendance_records(
    department=None, batch=None, student=None,
    from_date=None, to_date=None, status=None,
):
    """Listing of attendance rows for the table view."""
    filters = {}
    if department:
        filters["department"] = department
    if batch:
        filters["batch"] = batch
    if student:
        filters["student"] = student
    if status:
        filters["status"] = status

    dc = _date_column()
    if from_date and to_date:
        filters[dc] = ["between", [from_date, to_date]]
    elif from_date:
        filters[dc] = [">=", from_date]
    elif to_date:
        filters[dc] = ["<=", to_date]

    rows = frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=[
            "name", "student", "department", "batch",
            dc, "hour", "status", "remarks", "marked_by",
            "creation", "modified",
        ],
        order_by=f"{dc} desc, hour asc",
        limit_page_length=0,
    )

    # Enrich with student name & roll number
    student_ids = list({r["student"] for r in rows if r.get("student")})
    student_map = {}
    if student_ids:
        students = frappe.get_all(
            "Student",
            filters={"name": ["in", student_ids]},
            fields=["name", "full_name", "roll_number"],
            limit_page_length=0,
        )
        student_map = {s["name"]: s for s in students}

    for r in rows:
        s = student_map.get(r["student"], {})
        r["student_name"] = s.get("full_name") or r["student"]
        r["roll_number"] = s.get("roll_number") or ""
        # Normalize the date field name for the frontend
        if dc != "date" and dc in r:
            r["date"] = r[dc]

    return rows


@frappe.whitelist(allow_guest=True)
def get_attendance_summary(
    department=None, batch=None, from_date=None, to_date=None,
):
    """Per-student attendance percentages."""
    filters = {}
    if department:
        filters["department"] = department
    if batch:
        filters["batch"] = batch

    dc = _date_column()
    if from_date and to_date:
        filters[dc] = ["between", [from_date, to_date]]

    rows = frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=["student", "status"],
        limit_page_length=0,
    )

    summary = {}
    for r in rows:
        s = summary.setdefault(r["student"], {
            "Present": 0,
            "Absent": 0,
            "Late": 0,
            "On Leave": 0,
            "total": 0,
        })
        s[r["status"]] = s.get(r["status"], 0) + 1
        s["total"] += 1

    result = []
    for sid, data in summary.items():
        s = frappe.db.get_value(
            "Student", sid,
            ["full_name", "roll_number", "department", "batch"],
            as_dict=True,
        ) or {}
        present = data["Present"] + data["Late"]
        data["student"] = sid
        data["student_name"] = s.get("full_name") or sid
        data["roll_number"] = s.get("roll_number") or ""
        data["department"] = s.get("department") or ""
        data["batch"] = s.get("batch") or ""
        data["percentage"] = round((present / data["total"]) * 100, 2) if data["total"] else 0
        result.append(data)

    result.sort(key=lambda x: (x["department"], x["batch"], x["roll_number"]))
    return result


# ════════════════════════════════════════════════════════════════════════════
# Student portal — view own attendance
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_my_attendance(from_date=None, to_date=None):
    """Logged-in student views their own attendance."""
    user = frappe.session.user
    if user in ("Guest", "Administrator"):
        return []

    student = frappe.db.get_value("Student", {"user": user}, "name")
    if not student:
        return []

    return get_attendance_records(
        student=student,
        from_date=from_date,
        to_date=to_date,
    )
