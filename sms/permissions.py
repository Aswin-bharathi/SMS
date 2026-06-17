
"""
Row-level security based on roles:
- Administrator / System Manager: full access
- Staff (class-in-charge): only their batches
- Student: only own records
"""
import frappe


def _is_admin(user):
    if user == "Administrator":
        return True
    roles = frappe.get_roles(user)
    return "System Manager" in roles or "SMS Admin" in roles


def _staff_batches(user):
    """All batch names where this user is class in-charge."""
    return frappe.get_all(
        "Batch",
        filters={"class_in_charge": user, "is_active": 1},
        pluck="name",
    )


def _student_record(user):
    """Student doc name for the logged-in user (if any)."""
    return frappe.db.get_value("Student", {"user": user}, "name")


def _sql_in_list(items):
    """Safely quote a list for SQL IN()."""
    if not items:
        return "''"
    return ",".join(frappe.db.escape(i) for i in items)


# ════════════════════════════════════════════════════════════════════════════
# Student
# ════════════════════════════════════════════════════════════════════════════
def student_query(user):
    if _is_admin(user):
        return ""

    roles = frappe.get_roles(user)

    # Student sees only themselves
    if "SMS Student" in roles:
        own = _student_record(user)
        if not own:
            return "1=0"
        return f"`tabStudent`.name = {frappe.db.escape(own)}"

    # Staff sees students of their batches
    if "SMS Staff" in roles:
        batches = _staff_batches(user)
        if not batches:
            return "1=0"
        return f"`tabStudent`.batch IN ({_sql_in_list(batches)})"

    return "1=0"


# ════════════════════════════════════════════════════════════════════════════
# Student Attendance
# ════════════════════════════════════════════════════════════════════════════
def attendance_query(user):
    if _is_admin(user):
        return ""

    roles = frappe.get_roles(user)

    if "SMS Student" in roles:
        own = _student_record(user)
        if not own:
            return "1=0"
        return f"`tabStudent Attendance`.student = {frappe.db.escape(own)}"

    if "SMS Staff" in roles:
        batches = _staff_batches(user)
        if not batches:
            return "1=0"
        return f"`tabStudent Attendance`.batch IN ({_sql_in_list(batches)})"

    return "1=0"


# ════════════════════════════════════════════════════════════════════════════
# Student Fee
# ════════════════════════════════════════════════════════════════════════════
def student_fee_query(user):
    if _is_admin(user):
        return ""

    roles = frappe.get_roles(user)

    if "SMS Student" in roles:
        own = _student_record(user)
        if not own:
            return "1=0"
        return f"`tabStudent Fee`.student = {frappe.db.escape(own)}"

    if "SMS Staff" in roles:
        batches = _staff_batches(user)
        if not batches:
            return "1=0"
        return f"`tabStudent Fee`.batch IN ({_sql_in_list(batches)})"

    return "1=0"


# ════════════════════════════════════════════════════════════════════════════
# Batch (staff sees only their own)
# ════════════════════════════════════════════════════════════════════════════
def batch_query(user):
    if _is_admin(user):
        return ""

    roles = frappe.get_roles(user)

    if "SMS Staff" in roles:
        return f"`tabBatch`.class_in_charge = {frappe.db.escape(user)}"

    if "SMS Student" in roles:
        own = _student_record(user)
        if not own:
            return "1=0"
        student_batch = frappe.db.get_value("Student", own, "batch")
        if not student_batch:
            return "1=0"
        return f"`tabBatch`.name = {frappe.db.escape(student_batch)}"

    return ""  # default Frappe permissions
