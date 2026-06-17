"""
Hierarchy navigation: Department → Batch → Students
"""
import frappe
from frappe import _
from frappe.utils import add_days, nowdate


# ════════════════════════════════════════════════════════════════════════════
# Department tree
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_department_tree():
    """Return all departments with nested batches and student counts."""
    departments = frappe.get_all(
        "Department",
        fields=["name", "department_name", "department_code", "is_active"],
        order_by="department_name asc",
        limit_page_length=0,
    )

    for dept in departments:
        batches = frappe.get_all(
            "Batch",
            filters={"department": dept["name"], "is_active": 1},
           fields=[
				"name", "batch_year", "program", "class_in_charge",
				"current_semester", "total_semesters", "academic_year",
				"status",   # ← ADD
			],
            order_by="batch_year desc",
            limit_page_length=0,
        )

        for b in batches:
            b["student_count"] = frappe.db.count("Student", {
                "batch": b["name"],
                "status": "Active",
            })

        dept["batches"]       = batches
        dept["batch_count"]   = len(batches)
        dept["student_count"] = sum(b["student_count"] for b in batches)

    return departments


# ════════════════════════════════════════════════════════════════════════════
# Batches under a department
# (named differently to avoid collision with meta.get_batches)
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_batches_under_dept(department=None, include_inactive=0):
    """List batches, optionally filtered by department."""
    filters = {}
    if not int(include_inactive or 0):
        filters["is_active"] = 1
    if department:
        filters["department"] = department

    batches = frappe.get_all(
        "Batch",
        filters=filters,
        fields=[
			"name", "department", "batch_year", "program",
			"class_in_charge", "current_semester", "total_semesters",
			"academic_year", "is_active", "status",   # ← ADD status
		],
        order_by="department asc, batch_year desc",
        limit_page_length=0,
    )

    for b in batches:
        b["student_count"] = frappe.db.count("Student", {
            "batch": b["name"], "status": "Active",
        })
        if b.get("class_in_charge"):
            b["class_in_charge_name"] = frappe.db.get_value(
                "User", b["class_in_charge"], "full_name"
            )

    return batches


# ════════════════════════════════════════════════════════════════════════════
# Batch detail
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_batch_detail(batch):
    """Full details of one batch including students and summary stats."""
    if not batch or not frappe.db.exists("Batch", batch):
        frappe.throw(_("Batch not found"))

    b = frappe.get_doc("Batch", batch).as_dict()

    if b.get("class_in_charge"):
        b["class_in_charge_name"] = frappe.db.get_value(
            "User", b["class_in_charge"], "full_name"
        )

    b["students"] = frappe.get_all(
        "Student",
        filters={"batch": batch},
        fields=[
            "name", "student_id", "roll_number", "full_name", "email",
            "gender", "status", "semester", "user",
        ],
        order_by="roll_number asc",
        limit_page_length=0,
    )
    b["student_count"] = len(b["students"])

    # ─── Attendance summary (last 30 days) ─────────────────────────────────
    # Auto-detect the date column (could be 'date' or 'attendance_date')
    date_col = None
    for candidate in ("date", "attendance_date", "att_date"):
        if frappe.db.has_column("Student Attendance", candidate):
            date_col = candidate
            break

    b["attendance_summary"] = {}
    if date_col:
        from_date = add_days(nowdate(), -30)
        att = frappe.db.sql(f"""
            SELECT status, COUNT(*) AS count
            FROM `tabStudent Attendance`
            WHERE batch=%s AND `{date_col}` >= %s
            GROUP BY status
        """, (batch, from_date), as_dict=True)
        b["attendance_summary"] = {a["status"]: a["count"] for a in att}

    # ─── Fee summary ───────────────────────────────────────────────────────
    fees = frappe.db.sql("""
        SELECT
            COALESCE(SUM(total_amount), 0)       AS total,
            COALESCE(SUM(paid_amount), 0)        AS paid,
            COALESCE(SUM(outstanding_amount), 0) AS outstanding,
            COUNT(*)                             AS count
        FROM `tabStudent Fee`
        WHERE batch=%s
    """, (batch,), as_dict=True)
    b["fee_summary"] = fees[0] if fees else {}

    return b

# ════════════════════════════════════════════════════════════════════════════
# Students under a batch
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_students_by_batch(batch, status=None):
    """List students in a batch."""
    if not batch:
        return []
    filters = {"batch": batch}
    if status:
        filters["status"] = status

    return frappe.get_all(
        "Student",
        filters=filters,
        fields=[
            "name", "student_id", "roll_number", "full_name", "email",
            "gender", "department", "batch", "status", "semester", "user",
        ],
        order_by="roll_number asc",
        limit_page_length=0,
    )


# ════════════════════════════════════════════════════════════════════════════
# Validation hooks (called from hooks.py)
# ════════════════════════════════════════════════════════════════════════════
def validate_unique_roll_number(doc, method=None):
    """Roll number must be unique within a department."""
    if not doc.roll_number or not doc.department:
        return

    existing = frappe.db.exists("Student", {
        "department":  doc.department,
        "roll_number": doc.roll_number,
        "name":        ["!=", doc.name],
    })
    if existing:
        frappe.throw(
            _("Roll number {0} already exists in {1} (student: {2})")
            .format(doc.roll_number, doc.department, existing)
        )


def sync_department_from_batch(doc, method=None):
    """When student saved with a batch, sync department & semester from batch."""
    if doc.batch and frappe.db.exists("Batch", doc.batch):
        batch_data = frappe.db.get_value(
            "Batch", doc.batch,
            ["department", "current_semester"],
            as_dict=True,
        )
        if batch_data:
            if not doc.department:
                doc.department = batch_data.department
            if not doc.semester:
                doc.semester = batch_data.current_semester


# ════════════════════════════════════════════════════════════════════════════
# Dashboard counts
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_overview_counts():
    """Top-level dashboard counts."""
    return {
        "departments":         frappe.db.count("Department",  {"is_active": 1}),
        "batches":             frappe.db.count("Batch",       {"is_active": 1}),
        "students":            frappe.db.count("Student",     {"status": "Active"}),
        "fee_records":         frappe.db.count("Student Fee"),
        "attendance_records":  frappe.db.count("Student Attendance"),
    }

def normalize_student_id(doc, method=None):
    """
    Standardize student_id to uppercase, strip whitespace.
    Detect duplicate emails and warn.
    """
    if doc.student_id:
        normalized = doc.student_id.strip().upper()
        if normalized != doc.student_id:
            doc.student_id = normalized

    # Warn on duplicate email (allow but log)
    if doc.email:
        existing = frappe.db.get_value(
            "Student",
            {"email": doc.email, "name": ["!=", doc.name]},
            ["name", "full_name"],
            as_dict=True,
        )
        if existing:
            frappe.msgprint(
                f"⚠️ Email {doc.email} is also used by student {existing.name} ({existing.full_name}).",
                indicator="orange",
                alert=True,
            )
