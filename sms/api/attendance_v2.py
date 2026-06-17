"""
NEW attendance API — hour-based with subject/faculty audit trail.
"""
import json
import frappe
from frappe import _
from frappe.utils import getdate, nowdate, get_datetime, now, time_diff_in_hours, now_datetime


# ════════════════════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════════════════════
EDIT_WINDOW_HOURS = 24   # Faculty can edit within 24h; admin anytime


# ════════════════════════════════════════════════════════════════════════════
# Permission helpers
# ════════════════════════════════════════════════════════════════════════════
def _is_admin(user=None):
    user = user or frappe.session.user
    if user == "Administrator":
        return True
    roles = frappe.get_roles(user)
    return "System Manager" in roles or "SMS Admin" in roles


def _hour_has_started(date_str, hour_label):
    """
    Check if the class hour has started yet on the given date.
    You can't mark attendance for a class that hasn't begun!
    """
    target_date = getdate(date_str)
    today = getdate(nowdate())

    # Past date → hour has definitely started/ended
    if target_date < today:
        return True

    # Future date → hour hasn't started
    if target_date > today:
        return False

    # Same day → check if current time >= hour start time
    hour_doc = frappe.db.get_value(
        "Hour Slot", hour_label,
        ["start_time", "end_time"], as_dict=True,
    )
    if not hour_doc:
        return False

    current_dt = now_datetime()
    from datetime import datetime, time
    # Compose start datetime
    if isinstance(hour_doc.start_time, str):
        # Time as string like "10:00:00"
        h, m, s = map(int, hour_doc.start_time.split(":"))
        start_dt = datetime.combine(target_date, time(h, m, s))
    else:
        # Time object or timedelta
        try:
            total_seconds = int(hour_doc.start_time.total_seconds())
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            start_dt = datetime.combine(target_date, time(h, m))
        except AttributeError:
            start_dt = datetime.combine(target_date, hour_doc.start_time)

    return current_dt >= start_dt


def _can_mark_for_slot(slot_id, date_str=None, user=None):
    """
    Returns (allowed: bool, reason: str)
    Allowed if:
      - Admin (always)
      - OR (faculty of the slot AND no active substitution AND hour has started AND batch not archived)
      - OR (approved substitute on that date)
    """
    user = user or frappe.session.user

    # Admins bypass everything
    if _is_admin(user):
        return True, "admin"

    slot = frappe.db.get_value(
        "Timetable Slot", slot_id,
        ["faculty", "parent", "hour"], as_dict=True,
    )
    if not slot:
        return False, "slot_not_found"

    # Check batch status
    batch_name = frappe.db.get_value("Timetable", slot.parent, "batch")
    batch_status = frappe.db.get_value("Batch", batch_name, "status")
    if batch_status in ("Archived", "Graduated"):
        return False, "batch_archived"

    # Check if hour has started (can't mark for future classes)
    if date_str:
        if not _hour_has_started(date_str, slot.hour):
            return False, "hour_not_started"

    # Check substitution
    if date_str:
        sub = frappe.db.get_value(
            "Staff Substitution",
            {
                "timetable_slot": slot_id,
                "date": date_str,
                "status": "Approved",
            },
            ["substitute_faculty", "original_faculty"],
            as_dict=True,
        )
        if sub:
            # Only substitute can mark
            if sub.substitute_faculty == user:
                return True, "substitute_faculty"
            elif sub.original_faculty == user:
                return False, "substituted_to_another"
            else:
                return False, "not_authorized"

    # No substitution → original faculty
    if slot.faculty == user:
        return True, "original_faculty"

    return False, "not_authorized"


def _can_edit(att_doc, user=None):
    """
    Edit window check.
    - Admin: anytime
    - Faculty: within 24h of marked_at
    - If record never edited (marked_at empty), allow
    """
    user = user or frappe.session.user
    if _is_admin(user):
        return True
    if not att_doc.marked_at:
        return True
    hours = time_diff_in_hours(now(), att_doc.marked_at)
    return hours <= EDIT_WINDOW_HOURS


def _can_edit_for_date(date_str, user=None):
    """
    Strict check: for an existing attendance record, can this user edit it on this date?
    - Admin: always
    - Faculty: only if date is today OR yesterday (within 24h)
    """
    user = user or frappe.session.user
    if _is_admin(user):
        return True

    target = getdate(date_str)
    today = getdate(nowdate())
    diff_days = (today - target).days

    # Today: always editable (within hour-bounds checked elsewhere)
    if diff_days == 0:
        return True
    # Yesterday: editable
    if diff_days == 1:
        return True
    # Older: not editable for faculty
    return False

# ════════════════════════════════════════════════════════════════════════════
# Roster + marking
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_marking_screen(timetable_slot, date):
    """
    All info needed to render the attendance marking screen.
    Returns rich state including:
      - can_mark / can_edit flags
      - is_first_time_marking (no existing records)
      - hour_has_started flag
      - time_until_hour_starts (if not yet started)
    """
    if not frappe.db.exists("Timetable Slot", timetable_slot):
        frappe.throw(_("Timetable slot not found"))

    target_date = getdate(date or nowdate())
    today = getdate(nowdate())

    # Get slot info
    slot = frappe.db.get_value(
        "Timetable Slot", timetable_slot,
        ["name", "day", "hour", "subject", "faculty", "room", "is_lab", "parent"],
        as_dict=True,
    )

    # Get timetable + batch
    timetable = frappe.db.get_value(
        "Timetable", slot.parent,
        ["name", "batch", "semester", "is_active"],
        as_dict=True,
    )

    # Enrich slot
    slot["hour_details"] = frappe.db.get_value(
        "Hour Slot", slot.hour,
        ["start_time", "end_time", "hour_number"],
        as_dict=True,
    ) or {}
    if slot.subject:
        slot["subject_name"] = frappe.db.get_value(
            "Subject", slot.subject, "subject_name"
        )
    if slot.faculty:
        slot["faculty_name"] = frappe.db.get_value(
            "User", slot.faculty, "full_name"
        )

    batch = frappe.db.get_value(
        "Batch", timetable.batch,
        ["name", "batch_year", "department", "year_level",
         "current_semester", "status", "class_in_charge"],
        as_dict=True,
    ) or {}

    # Check substitution
    sub = frappe.db.get_value(
        "Staff Substitution",
        {"timetable_slot": timetable_slot, "date": target_date, "status": "Approved"},
        ["name", "original_faculty", "substitute_faculty", "reason"],
        as_dict=True,
    )
    if sub:
        sub["substitute_name"] = frappe.db.get_value(
            "User", sub["substitute_faculty"], "full_name"
        )
        effective_faculty = sub["substitute_faculty"]
    else:
        effective_faculty = slot.faculty

    # Get students
    students = frappe.get_all(
        "Student",
        filters={"batch": timetable.batch, "status": "Active"},
        fields=["name", "student_id", "roll_number", "full_name"],
        order_by="roll_number asc",
        limit_page_length=0,
    )

    # Existing attendance for this slot+date
    existing = {}
    rows = frappe.get_all(
        "Student Attendance",
        filters={"timetable_slot": timetable_slot, "date": target_date},
        fields=["name", "student", "status", "remarks", "marked_at",
                "last_edited_at", "edit_count", "marked_by", "last_edited_by"],
        limit_page_length=0,
    )
    for r in rows:
        existing[r["student"]] = r

    for s in students:
        rec = existing.get(s["name"])
        s["status"]  = rec["status"]  if rec else "Present"
        s["remarks"] = rec["remarks"] if rec else ""
        s["attendance_id"] = rec["name"] if rec else None
        s["already_marked"] = bool(rec)
        s["marked_at"] = str(rec["marked_at"]) if rec and rec.get("marked_at") else None
        s["edit_count"] = rec.get("edit_count", 0) if rec else 0

    # Determine state
    is_first_time = len(existing) == 0
    can_mark, reason = _can_mark_for_slot(timetable_slot, str(target_date))

    # Additional check for existing records on past dates
    can_edit_existing = _can_edit_for_date(str(target_date))
    if not is_first_time and not can_edit_existing and not _is_admin():
        can_mark = False
        reason = "edit_window_expired"

    # Hour timing info
    hour_started = _hour_has_started(str(target_date), slot.hour)

    return {
        "slot":         slot,
        "timetable":    timetable,
        "batch":        batch,
        "students":     students,
        "substitution": sub,
        "effective_faculty": effective_faculty,
        "can_mark":     can_mark,
        "reason":       reason,
        "is_archived":  batch.get("status") in ("Archived", "Graduated"),
        "is_first_time_marking": is_first_time,
        "hour_has_started": hour_started,
        "already_marked_count": len(existing),
        "date":         str(target_date),
        "is_today":     target_date == today,
        "is_past":      target_date < today,
        "is_future":    target_date > today,
        "days_ago":     (today - target_date).days,
    }
@frappe.whitelist(allow_guest=True, methods=["POST"])
def save_attendance(timetable_slot, date, records):
    """
    Bulk-save attendance for a slot+date.
    records: [{ student, status, remarks }, ...]
    """
    if isinstance(records, str):
        records = json.loads(records)

    # Pass date to permission check (validates hour-has-started etc.)
    can_mark, reason = _can_mark_for_slot(timetable_slot, str(date))
    if not can_mark:
        error_messages = {
            "slot_not_found":         "Class not found.",
            "batch_archived":         "This batch is archived — no attendance can be marked.",
            "hour_not_started":       "Cannot mark attendance — class hour has not started yet.",
            "substituted_to_another": "You've been substituted out of this class today.",
            "not_authorized":         "You are not authorized to mark this class.",
            "edit_window_expired":    "Edit window has expired (24 hours).",
        }
        frappe.throw(_(error_messages.get(reason, "Cannot mark attendance.")))

    target_date = getdate(date)
    today = getdate(nowdate())

    # Strict: faculty cannot mark for future dates ever
    if target_date > today and not _is_admin():
        frappe.throw(_("Cannot mark attendance for future dates."))

    slot = frappe.db.get_value(
        "Timetable Slot", timetable_slot,
        ["hour", "subject", "faculty", "parent"], as_dict=True,
    )
    batch = frappe.db.get_value("Timetable", slot.parent, "batch")
    department = frappe.db.get_value("Batch", batch, "department")

    sub = frappe.db.get_value(
        "Staff Substitution",
        {"timetable_slot": timetable_slot, "date": target_date, "status": "Approved"},
        ["name", "substitute_faculty"],
        as_dict=True,
    )
    effective_faculty = sub["substitute_faculty"] if sub else slot.faculty

    user = frappe.session.user
    now_dt = get_datetime()
    created, updated, errors = 0, 0, []

    for rec in records:
        student = rec.get("student")
        status  = rec.get("status", "Present")
        remarks = rec.get("remarks", "")

        if not student:
            continue

        existing_name = frappe.db.exists("Student Attendance", {
            "student": student,
            "date": target_date,
            "hour": slot.hour,
        })

        try:
            if existing_name:
                doc = frappe.get_doc("Student Attendance", existing_name)
                if not _can_edit(doc):
                    errors.append({
                        "student": student,
                        "error": "Edit window expired",
                    })
                    continue
                doc.status = status
                doc.remarks = remarks
                doc.last_edited_by = user
                doc.last_edited_at = now_dt
                doc.edit_count = (doc.edit_count or 0) + 1
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                doc = frappe.get_doc({
                    "doctype":        "Student Attendance",
                    "student":        student,
                    "batch":          batch,
                    "department":     department,
                    "date":           target_date,
                    "hour":           slot.hour,
                    "subject":        slot.subject,
                    "faculty":        effective_faculty,
                    "timetable_slot": timetable_slot,
                    "substitution":   sub["name"] if sub else None,
                    "status":         status,
                    "remarks":        remarks,
                    "marked_by":      user,
                    "marked_at":      now_dt,
                    "edit_count":     0,
                })
                doc.insert(ignore_permissions=True)
                created += 1
        except Exception as e:
            errors.append({"student": student, "error": str(e)})

    frappe.db.commit()
    return {
        "message":   _("Attendance saved"),
        "created":   created,
        "updated":   updated,
        "total":     created + updated,
        "errors":    errors,
    }
# ════════════════════════════════════════════════════════════════════════════
# History / reports
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_batch_attendance_history(batch, from_date=None, to_date=None,
                                  subject=None, student=None):
    """All attendance records for a batch, filterable."""
    filters = {"batch": batch}
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]
    if subject:
        filters["subject"] = subject
    if student:
        filters["student"] = student

    rows = frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=["name", "student", "date", "hour", "subject", "faculty",
                "status", "remarks", "marked_by", "marked_at",
                "last_edited_by", "last_edited_at", "edit_count", "substitution"],
        order_by="date desc, hour asc",
        limit_page_length=0,
    )

    # Enrich with display names
    sid_set = list({r["student"] for r in rows if r.get("student")})
    student_map = {}
    if sid_set:
        for s in frappe.get_all("Student",
            filters={"name": ["in", sid_set]},
            fields=["name", "full_name", "roll_number"],
            limit_page_length=0):
            student_map[s["name"]] = s

    for r in rows:
        s = student_map.get(r["student"], {})
        r["student_name"] = s.get("full_name") or r["student"]
        r["roll_number"]  = s.get("roll_number") or ""
        if r.get("subject"):
            r["subject_name"] = frappe.db.get_value(
                "Subject", r["subject"], "subject_name"
            )
        if r.get("faculty"):
            r["faculty_name"] = frappe.db.get_value(
                "User", r["faculty"], "full_name"
            )

    return rows


@frappe.whitelist(allow_guest=True)
def get_student_attendance_percentage(student, from_date=None, to_date=None):
    """Per-subject attendance percentage for one student."""
    filters = {"student": student}
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]

    rows = frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=["subject", "status"],
        limit_page_length=0,
    )

    by_subject = {}
    for r in rows:
        sub = r["subject"] or "Unknown"
        s = by_subject.setdefault(sub, {
            "Present": 0, "Absent": 0, "Late": 0, "On Leave": 0, "total": 0,
        })
        s[r["status"]] = s.get(r["status"], 0) + 1
        s["total"] += 1

    result = []
    for sub_code, counts in by_subject.items():
        present = counts["Present"] + counts["Late"]
        percentage = round((present / counts["total"]) * 100, 2) if counts["total"] else 0
        sub_name = frappe.db.get_value("Subject", sub_code, "subject_name") or sub_code
        result.append({
            "subject":      sub_code,
            "subject_name": sub_name,
            "present":      counts["Present"],
            "absent":       counts["Absent"],
            "late":         counts["Late"],
            "on_leave":     counts["On Leave"],
            "total":        counts["total"],
            "percentage":   percentage,
        })
    result.sort(key=lambda x: x["subject_name"])
    return result
