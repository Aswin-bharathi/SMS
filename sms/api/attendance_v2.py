"""
NEW attendance API — hour-based with subject/faculty audit trail.
Fixed version: timedelta handling, timezone-safe date checks, edit window.
"""
import json
from datetime import datetime, time as dt_time, date as dt_date

import frappe
from frappe import _
from frappe.utils import (
    getdate, nowdate, get_datetime, now,
    time_diff_in_hours, now_datetime,
)


# ════════════════════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════════════════════
EDIT_WINDOW_HOURS = 24   # Faculty can edit within 24h of marking; admin anytime


# ════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ════════════════════════════════════════════════════════════════════════════
def _to_time(raw) -> dt_time:
    """
    Safely convert MariaDB time values to Python time objects.

    MariaDB returns Time fields as timedelta (e.g. datetime.timedelta(seconds=36000)
    for 10:00:00). Handle all three possible types:
      - str        "10:00:00"
      - timedelta  datetime.timedelta(seconds=36000)
      - time       datetime.time(10, 0)
    """
    if raw is None:
        return dt_time(0, 0)

    # Already a time object
    if isinstance(raw, dt_time):
        return raw

    # String like "10:00:00" or "10:00"
    if isinstance(raw, str):
        parts = raw.strip().split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return dt_time(h, m, s)

    # timedelta (most common from MariaDB)
    try:
        total = int(raw.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        # Clamp — timedelta can exceed 24h for weird data
        h = min(h, 23)
        return dt_time(h, m, s)
    except AttributeError:
        pass

    # Last resort
    return dt_time(0, 0)


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

    Returns:
        True  — class has started or is in the past
        False — class is in the future (or date is future)
    """
    target_date = getdate(date_str)
    today       = getdate(nowdate())

    # Past date → hour has definitely started/ended
    if target_date < today:
        return True

    # Future date → hour hasn't started
    if target_date > today:
        return False

    # Same day → check current time vs hour start time
    hour_doc = frappe.db.get_value(
        "Hour Slot", hour_label,
        ["start_time", "end_time", "hour_number"],
        as_dict=True,
    )
    if not hour_doc:
        # Unknown slot — allow (fail open)
        return True

    start_t  = _to_time(hour_doc.start_time)
    start_dt = datetime.combine(target_date, start_t)
    current  = now_datetime()          # already a datetime from frappe.utils

    # Ensure both are naive (no tzinfo) for comparison
    if hasattr(current, "tzinfo") and current.tzinfo is not None:
        current = current.replace(tzinfo=None)

    return current >= start_dt


def _hour_end_datetime(date_str, hour_label):
    """Return the datetime when this hour ends. Used for edit-window calc."""
    target_date = getdate(date_str)
    hour_doc = frappe.db.get_value(
        "Hour Slot", hour_label,
        ["end_time"],
        as_dict=True,
    )
    if not hour_doc:
        # Assume 1h after midnight if unknown
        return datetime.combine(target_date, dt_time(0, 0))

    end_t = _to_time(hour_doc.end_time)
    return datetime.combine(target_date, end_t)


def _can_mark_for_slot(slot_id, date_str=None, user=None):
    """
    Returns (allowed: bool, reason: str)

    Allowed if:
      - Admin (always)
      - Faculty of the slot + hour has started + batch not archived
      - Approved substitute on that date
    """
    user = user or frappe.session.user

    if _is_admin(user):
        return True, "admin"

    slot = frappe.db.get_value(
        "Timetable Slot", slot_id,
        ["faculty", "parent", "hour"], as_dict=True,
    )
    if not slot:
        return False, "slot_not_found"

    # Check batch status
    batch_name   = frappe.db.get_value("Timetable", slot.parent, "batch")
    batch_status = frappe.db.get_value("Batch", batch_name, "status")
    if batch_status in ("Archived", "Graduated"):
        return False, "batch_archived"

    # Hour must have started before marking
    if date_str:
        if not _hour_has_started(date_str, slot.hour):
            return False, "hour_not_started"

    # Check substitution
    if date_str:
        sub = frappe.db.get_value(
            "Staff Substitution",
            {
                "timetable_slot": slot_id,
                "date":           date_str,
                "status":         "Approved",
            },
            ["substitute_faculty", "original_faculty"],
            as_dict=True,
        )
        if sub:
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
    Per-record edit check.
    - Admin: always
    - Faculty: within EDIT_WINDOW_HOURS of marked_at
    """
    user = user or frappe.session.user
    if _is_admin(user):
        return True
    if not att_doc.marked_at:
        return True
    hours = time_diff_in_hours(now(), att_doc.marked_at)
    return hours <= EDIT_WINDOW_HOURS


def _can_edit_for_date(date_str, hour_label=None, user=None):
    """
    Time-aware edit window check for faculty.

    Edit window = EDIT_WINDOW_HOURS after the hour ENDS.
    So if Hour 1 ends at 11:00 on Day X, faculty can edit until 11:00 on Day X+1.

    Args:
        date_str:   The attendance date
        hour_label: The Hour Slot name (for precise end-time calc)
        user:       Defaults to session user

    Returns:
        True if editable, False if locked
    """
    user = user or frappe.session.user
    if _is_admin(user):
        return True

    target = getdate(date_str)
    today  = getdate(nowdate())

    # Future dates — cannot edit (shouldn't exist, but guard anyway)
    if target > today:
        return False

    diff_days = (today - target).days

    # More than 2 days ago — definitely outside 24h window
    if diff_days > 1:
        return False

    # Same day — always editable (hour has started, edit window open)
    if diff_days == 0:
        return True

    # Yesterday — need precise time check
    # Edit window expires EDIT_WINDOW_HOURS after the hour ended
    if diff_days == 1 and hour_label:
        hour_end = _hour_end_datetime(date_str, hour_label)
        deadline = datetime.combine(
            hour_end.date(),
            hour_end.time(),
        )
        # Add EDIT_WINDOW_HOURS
        from datetime import timedelta
        deadline = deadline + timedelta(hours=EDIT_WINDOW_HOURS)

        current = now_datetime()
        if hasattr(current, "tzinfo") and current.tzinfo is not None:
            current = current.replace(tzinfo=None)

        return current <= deadline

    # Yesterday but no hour_label — fall back to permissive
    if diff_days == 1:
        return True

    return False


# ════════════════════════════════════════════════════════════════════════════
# Roster + marking
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_marking_screen(timetable_slot, date):
    """
    All info needed to render the attendance marking screen.

    Returns rich state dict including:
      - can_mark / reason
      - mode: "first_time" | "update" | "read_only"
      - is_first_time_marking
      - hour_has_started
      - edit_window_open (bool)
      - students list with existing status pre-filled
    """
    if not frappe.db.exists("Timetable Slot", timetable_slot):
        frappe.throw(_("Timetable slot not found: {}").format(timetable_slot))

    # Always use server's current date — never trust client-passed "today"
    today       = getdate(nowdate())
    target_date = getdate(date) if date else today

    # ── Slot info ──────────────────────────────────────────────────────────
    slot = frappe.db.get_value(
        "Timetable Slot", timetable_slot,
        ["name", "day", "hour", "subject", "faculty",
         "room", "is_lab", "parent"],
        as_dict=True,
    )

    # ── Timetable + batch ──────────────────────────────────────────────────
    timetable = frappe.db.get_value(
        "Timetable", slot.parent,
        ["name", "batch", "semester", "is_active"],
        as_dict=True,
    )

    # ── Enrich slot display fields ─────────────────────────────────────────
    hour_doc = frappe.db.get_value(
        "Hour Slot", slot.hour,
        ["start_time", "end_time", "hour_number"],
        as_dict=True,
    ) or {}

    # Convert to serializable strings for JSON response
    if hour_doc:
        hour_doc["start_time"] = str(_to_time(hour_doc.get("start_time")))[:5]
        hour_doc["end_time"]   = str(_to_time(hour_doc.get("end_time")))[:5]

    slot["hour_details"] = hour_doc

    if slot.subject:
        slot["subject_name"] = frappe.db.get_value(
            "Subject", slot.subject, "subject_name"
        )
    if slot.faculty:
        slot["faculty_name"] = frappe.db.get_value(
            "User", slot.faculty, "full_name"
        )

    # ── Batch info ─────────────────────────────────────────────────────────
    batch = frappe.db.get_value(
        "Batch", timetable.batch,
        ["name", "batch_year", "department", "year_level",
         "current_semester", "status", "class_in_charge"],
        as_dict=True,
    ) or {}

    # ── Substitution check ─────────────────────────────────────────────────
    sub = frappe.db.get_value(
        "Staff Substitution",
        {
            "timetable_slot": timetable_slot,
            "date":           target_date,
            "status":         "Approved",
        },
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

    # ── Students roster ────────────────────────────────────────────────────
    students = frappe.get_all(
        "Student",
        filters={"batch": timetable.batch, "status": "Active"},
        fields=["name", "student_id", "roll_number", "full_name"],
        order_by="roll_number asc",
        limit_page_length=0,
    )

    # ── Existing attendance ────────────────────────────────────────────────
    existing = {}
    rows = frappe.get_all(
        "Student Attendance",
        filters={
            "timetable_slot": timetable_slot,
            "date":           target_date,
        },
        fields=["name", "student", "status", "remarks",
                "marked_at", "last_edited_at", "edit_count",
                "marked_by", "last_edited_by"],
        limit_page_length=0,
    )
    for r in rows:
        existing[r["student"]] = r

    # Merge into student list
    for s in students:
        rec = existing.get(s["name"])
        s["status"]         = rec["status"]   if rec else "Present"
        s["remarks"]        = rec["remarks"]  if rec else ""
        s["attendance_id"]  = rec["name"]     if rec else None
        s["already_marked"] = bool(rec)
        s["marked_at"]      = str(rec["marked_at"]) if rec and rec.get("marked_at") else None
        s["edit_count"]     = rec.get("edit_count", 0) if rec else 0

    # ── State computation ──────────────────────────────────────────────────
    is_first_time  = len(existing) == 0
    hour_started   = _hour_has_started(str(target_date), slot.hour)
    is_archived    = batch.get("status") in ("Archived", "Graduated")
    is_today       = target_date == today
    is_past        = target_date < today
    is_future      = target_date > today
    days_ago       = (today - target_date).days

    # Edit window: time-aware for yesterday, open for today
    edit_window_open = _can_edit_for_date(str(target_date), slot.hour)

    # Permission
    can_mark, reason = _can_mark_for_slot(
        timetable_slot, str(target_date)
    )

    # Override: if records exist but edit window closed → read-only for faculty
    if not is_first_time and not edit_window_open and not _is_admin():
        can_mark = False
        reason   = "edit_window_expired"

    # Determine mode
    if is_archived or is_future or (not hour_started and is_today):
        mode = "read_only"
    elif is_first_time and can_mark:
        mode = "first_time"
    elif not is_first_time and can_mark:
        mode = "update"
    else:
        mode = "read_only"

    return {
        # Slot + context
        "slot":              slot,
        "timetable":         timetable,
        "batch":             batch,
        "students":          students,
        "substitution":      sub,
        "effective_faculty": effective_faculty,

        # Permission
        "can_mark":          can_mark,
        "reason":            reason,
        "mode":              mode,          # "first_time" | "update" | "read_only"

        # State flags
        "is_archived":            is_archived,
        "is_first_time_marking":  is_first_time,
        "hour_has_started":       hour_started,
        "edit_window_open":       edit_window_open,
        "already_marked_count":   len(existing),

        # Date helpers
        "date":     str(target_date),
        "is_today": is_today,
        "is_past":  is_past,
        "is_future": is_future,
        "days_ago": days_ago,
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
def save_attendance(timetable_slot, date, records):
    """
    Bulk-save attendance for a slot + date.
    records: [{ student, status, remarks }, ...]
    """
    if isinstance(records, str):
        records = json.loads(records)

    can_mark, reason = _can_mark_for_slot(timetable_slot, str(date))
    if not can_mark:
        error_messages = {
            "slot_not_found":         "Class slot not found.",
            "batch_archived":         "This batch is archived — no attendance can be marked.",
            "hour_not_started":       "Cannot mark attendance — class hour has not started yet.",
            "substituted_to_another": "You have been substituted out of this class today.",
            "not_authorized":         "You are not authorised to mark this class.",
            "edit_window_expired":    "Edit window has expired (24 hours).",
        }
        frappe.throw(_(error_messages.get(reason, "Cannot mark attendance.")))

    target_date = getdate(date)
    today       = getdate(nowdate())

    # Strict: faculty cannot mark future dates
    if target_date > today and not _is_admin():
        frappe.throw(_("Cannot mark attendance for future dates."))

    slot = frappe.db.get_value(
        "Timetable Slot", timetable_slot,
        ["hour", "subject", "faculty", "parent"], as_dict=True,
    )
    batch      = frappe.db.get_value("Timetable", slot.parent, "batch")
    department = frappe.db.get_value("Batch", batch, "department")

    sub = frappe.db.get_value(
        "Staff Substitution",
        {
            "timetable_slot": timetable_slot,
            "date":           target_date,
            "status":         "Approved",
        },
        ["name", "substitute_faculty"],
        as_dict=True,
    )
    effective_faculty = sub["substitute_faculty"] if sub else slot.faculty

    user    = frappe.session.user
    now_dt  = get_datetime()
    created, updated, errors = 0, 0, []

    for rec in records:
        student = rec.get("student")
        status  = rec.get("status", "Present")
        remarks = rec.get("remarks", "")

        if not student:
            continue

        existing_name = frappe.db.exists("Student Attendance", {
            "student": student,
            "date":    target_date,
            "hour":    slot.hour,
        })

        try:
            if existing_name:
                doc = frappe.get_doc("Student Attendance", existing_name)
                if not _can_edit(doc):
                    errors.append({
                        "student": student,
                        "error":   "Edit window expired for this record",
                    })
                    continue
                doc.status         = status
                doc.remarks        = remarks
                doc.last_edited_by = user
                doc.last_edited_at = now_dt
                doc.edit_count     = (doc.edit_count or 0) + 1
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
        "message": _("Attendance saved"),
        "created": created,
        "updated": updated,
        "total":   created + updated,
        "errors":  errors,
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

    sid_set = list({r["student"] for r in rows if r.get("student")})
    student_map = {}
    if sid_set:
        for s in frappe.get_all(
            "Student",
            filters={"name": ["in", sid_set]},
            fields=["name", "full_name", "roll_number"],
            limit_page_length=0,
        ):
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
        present    = counts["Present"] + counts["Late"]
        percentage = round((present / counts["total"]) * 100, 2) if counts["total"] else 0
        sub_name   = frappe.db.get_value("Subject", sub_code, "subject_name") or sub_code
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
