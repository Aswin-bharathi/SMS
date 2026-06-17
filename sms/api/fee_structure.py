"""
Fee Structure automation:
- When a structure is created, auto-create Student Fee for every student in the batch.
- When a new student joins a batch, auto-create fees from all active structures.
- When a structure is updated, sync amounts to unpaid fees.
"""
import frappe
from frappe import _
from frappe.utils import flt, nowdate, getdate


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════
def _compute_status(total, paid, due_date=None):
    total, paid = flt(total), flt(paid)
    if paid <= 0:
        status = "Unpaid"
    elif paid >= total:
        return "Paid"
    else:
        status = "Partially Paid"
    if due_date:
        try:
            if getdate(due_date) < getdate(nowdate()):
                status = "Overdue"
        except Exception:
            pass
    return status


# ════════════════════════════════════════════════════════════════════════════
# Hooks (called from hooks.py)
# ════════════════════════════════════════════════════════════════════════════
def auto_assign_to_batch(doc, method=None):
    """
    After a Program Fee Structure is created:
    create a Student Fee record for every active student in the linked batch.
    """
    if not getattr(doc, "is_active", 0):
        return
    if not getattr(doc, "batch", None):
        # Structure not linked to a specific batch — skip auto-assign
        return

    students = frappe.get_all(
        "Student",
        filters={"batch": doc.batch, "status": "Active"},
        fields=["name", "full_name", "program"],
    )

    created = 0
    for s in students:
        # Avoid duplicates
        if frappe.db.exists("Student Fee", {
            "student": s.name,
            "fee_structure": doc.name,
        }):
            continue

        amount = flt(doc.amount)
        fee = frappe.get_doc({
            "doctype":            "Student Fee",
            "student":            s.name,
            "student_name":       s.full_name,
            "program":            s.program or "",
            "department":         getattr(doc, "department", ""),
            "batch":              doc.batch,
            "semester":           getattr(doc, "semester", ""),
            "academic_year":      getattr(doc, "academic_year", ""),
            "fee_type":           doc.fee_type,
            "fee_structure":      doc.name,
            "due_date":           getattr(doc, "due_date", None),
            "total_amount":       amount,
            "paid_amount":        0,
            "outstanding_amount": amount,
            "payment_status":     _compute_status(amount, 0, getattr(doc, "due_date", None)),
        })
        fee.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    if created:
        frappe.msgprint(
            _("Auto-assigned this fee to {0} student(s) in batch {1}.")
            .format(created, doc.batch)
        )


def sync_batch_fees(doc, method=None):
    """
    When an existing Program Fee Structure is updated:
    push amount / due-date changes to its UNPAID Student Fees.
    """
    fees = frappe.get_all(
        "Student Fee",
        filters={
            "fee_structure": doc.name,
            "payment_status": ["in", ["Unpaid", "Overdue", "Partially Paid"]],
        },
        fields=["name", "paid_amount"],
    )
    for f in fees:
        fdoc = frappe.get_doc("Student Fee", f["name"])
        new_total = flt(doc.amount)
        paid      = flt(fdoc.paid_amount or 0)

        fdoc.total_amount       = new_total
        fdoc.outstanding_amount = max(new_total - paid, 0)
        fdoc.due_date           = getattr(doc, "due_date", fdoc.due_date)
        fdoc.payment_status     = _compute_status(new_total, paid, fdoc.due_date)
        fdoc.save(ignore_permissions=True)
    frappe.db.commit()


def assign_existing_fees_to_new_student(doc, method=None):
    """
    When a new Student is added to a batch:
    auto-create Student Fees from all active structures linked to that batch.
    """
    if not doc.batch:
        return

    structures = frappe.get_all(
        "Program Fee Structure",
        filters={"batch": doc.batch, "is_active": 1},
        fields=[
            "name", "department", "fee_type", "amount",
            "academic_year", "semester", "due_date",
        ],
    )

    for s in structures:
        if frappe.db.exists("Student Fee", {
            "student": doc.name,
            "fee_structure": s["name"],
        }):
            continue

        amount = flt(s["amount"])
        frappe.get_doc({
            "doctype":            "Student Fee",
            "student":            doc.name,
            "student_name":       doc.full_name,
            "program":            doc.program or "",
            "department":         s.get("department") or doc.department,
            "batch":              doc.batch,
            "semester":           s.get("semester") or "",
            "academic_year":      s.get("academic_year") or "",
            "fee_type":           s["fee_type"],
            "fee_structure":      s["name"],
            "due_date":           s.get("due_date"),
            "total_amount":       amount,
            "paid_amount":        0,
            "outstanding_amount": amount,
            "payment_status":     _compute_status(amount, 0, s.get("due_date")),
        }).insert(ignore_permissions=True)

    frappe.db.commit()


# ════════════════════════════════════════════════════════════════════════════
# Whitelisted API endpoints
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_structures_for_batch(batch):
    """All active fee structures for a given batch."""
    if not batch:
        return []
    return frappe.get_all(
        "Program Fee Structure",
        filters={"batch": batch, "is_active": 1},
        fields=[
            "name", "department", "batch", "fee_type",
            "amount", "academic_year", "semester", "due_date",
        ],
        order_by="fee_type asc",
        limit_page_length=0,
    )


@frappe.whitelist(allow_guest=True, methods=["POST"])
def reassign_structure(structure_name):
    """
    Manually re-trigger auto-assign for a structure
    (useful after fixing data).
    """
    doc = frappe.get_doc("Program Fee Structure", structure_name)
    auto_assign_to_batch(doc)
    return {"message": _("Re-assignment complete")}


@frappe.whitelist(allow_guest=True)
def get_fees_by_batch(batch):
    if not batch:
        return []
    return frappe.get_all(
        "Student Fee",
        filters={"batch": batch},
        fields=[
            "name", "student", "student_name", "fee_type",
            "semester", "academic_year", "due_date",
            "total_amount", "paid_amount", "outstanding_amount",
            "payment_status", "fee_structure",
            "installment_label",   # ← ADD THIS
        ],
        order_by="student asc, fee_type asc, due_date asc",
        limit_page_length=0,
    )
