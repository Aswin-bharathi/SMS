import json
import frappe
from frappe import _
from frappe.utils import nowdate, getdate, flt


# ─── helpers ────────────────────────────────────────────────────────────────
def _parse(data):
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            return {}
    return data or {}


def _compute_status(total, paid, due_date_str=None):
    total, paid = flt(total), flt(paid)
    if paid <= 0:
        status = "Unpaid"
    elif paid >= total:
        return "Paid"
    else:
        status = "Partially Paid"

    if due_date_str:
        try:
            if getdate(due_date_str) < getdate(nowdate()):
                status = "Overdue"
        except Exception:
            pass
    return status


# ─── Read ───────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_fees(student=None, status=None, semester=None, academic_year=None):
    filters = {}
    if student:        filters["student"]        = student
    if status:         filters["payment_status"] = status
    if semester:       filters["semester"]       = semester
    if academic_year:  filters["academic_year"]  = academic_year

    desired = [
        "name", "student", "student_name", "program",
        "semester", "academic_year", "fee_type",
        "due_date", "total_amount", "paid_amount", "outstanding_amount",
        "payment_status", "payment_date", "payment_method",
        "transaction_id", "remarks",
    ]
    meta = frappe.get_meta("Student Fee")
    available = {f.fieldname for f in meta.fields}
    fields = [f for f in desired if f == "name" or f in available]

    fees = frappe.get_all(
        "Student Fee",
        filters=filters,
        fields=fields,
        order_by="due_date desc",
        limit_page_length=0,
    )

    # Auto-mark overdue
    today = getdate(nowdate())
    overdue_ids = []
    for fee in fees:
        if (
            fee.get("payment_status") in ("Unpaid", "Partially Paid")
            and fee.get("due_date")
            and getdate(fee["due_date"]) < today
        ):
            fee["payment_status"] = "Overdue"
            overdue_ids.append(fee["name"])

    if overdue_ids:
        frappe.db.sql(
            "UPDATE `tabStudent Fee` SET payment_status='Overdue' WHERE name IN %(n)s",
            {"n": tuple(overdue_ids)},
        )
        frappe.db.commit()

    return fees


# ─── Create ─────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_fee(data):
    data = _parse(data)

    if not data.get("student"):
        frappe.throw(_("Student is required."))
    if not data.get("due_date"):
        frappe.throw(_("Due date is required."))

    total = flt(data.get("total_amount"))
    paid  = flt(data.get("paid_amount"))
    if paid > total:
        paid = total

    payload = {
        "doctype":            "Student Fee",
        "student":            data.get("student"),
        "student_name":       data.get("student_name", ""),
        "program":            data.get("program", ""),
        "academic_year":      data.get("academic_year", ""),
        "fee_type":           data.get("fee_type", "Tuition Fee"),
        "due_date":           data.get("due_date"),
        "total_amount":       total,
        "paid_amount":        paid,
        "outstanding_amount": total - paid,
        "payment_status":     _compute_status(total, paid, data.get("due_date")),
        "payment_date":       data.get("payment_date") or None,
        "payment_method":     data.get("payment_method", ""),
        "transaction_id":     data.get("transaction_id", ""),
        "remarks":            data.get("remarks", ""),
    }

    if frappe.db.has_column("Student Fee", "semester"):
        payload["semester"] = data.get("semester", "")

    doc = frappe.get_doc(payload)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": "Fee created successfully"}


# ─── Update ─────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_fee(fee_name, data):
    data = _parse(data)
    doc = frappe.get_doc("Student Fee", fee_name)

    total = flt(data.get("total_amount", doc.total_amount))
    paid  = flt(data.get("paid_amount",  doc.paid_amount))
    if paid > total:
        paid = total
    due_date = data.get("due_date", doc.due_date)

    updates = {
        "student":            data.get("student",         doc.student),
        "student_name":       data.get("student_name",    doc.student_name),
        "program":            data.get("program",         doc.program),
        "academic_year":      data.get("academic_year",   doc.academic_year),
        "fee_type":           data.get("fee_type",        doc.fee_type),
        "due_date":           due_date,
        "total_amount":       total,
        "paid_amount":        paid,
        "outstanding_amount": total - paid,
        "payment_status":     _compute_status(total, paid, str(due_date) if due_date else None),
        "payment_date":       data.get("payment_date")    or doc.payment_date,
        "payment_method":     data.get("payment_method",  doc.payment_method),
        "transaction_id":     data.get("transaction_id",  doc.transaction_id),
        "remarks":            data.get("remarks",         doc.remarks),
    }
    if frappe.db.has_column("Student Fee", "semester"):
        updates["semester"] = data.get("semester", getattr(doc, "semester", ""))

    doc.update(updates)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Fee updated successfully"}


# ─── Delete ─────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True, methods=["POST"])
def delete_fee(fee_name, force=0):
    doc = frappe.get_doc("Student Fee", fee_name)
    if flt(doc.paid_amount) > 0 and not int(force or 0):
        frappe.throw(_("Cannot delete a fee with payments. Pass force=1 to override."))
    frappe.delete_doc("Student Fee", fee_name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Fee deleted"}


# ─── Record Payment ─────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True, methods=["POST"])
def record_payment(fee_name, amount, payment_date, payment_method, transaction_id=""):
    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Payment amount must be greater than zero."))

    doc = frappe.get_doc("Student Fee", fee_name)
    total    = flt(doc.total_amount)
    new_paid = min(flt(doc.paid_amount) + amount, total)

    doc.paid_amount        = new_paid
    doc.outstanding_amount = total - new_paid
    doc.payment_status     = _compute_status(total, new_paid, str(doc.due_date) if doc.due_date else None)
    doc.payment_date       = payment_date or nowdate()
    doc.payment_method     = payment_method or doc.payment_method
    if transaction_id:
        doc.transaction_id = transaction_id

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {
        "message":        "Payment recorded",
        "payment_status": doc.payment_status,
        "paid_amount":    doc.paid_amount,
        "outstanding":    doc.outstanding_amount,
    }


# ─── Bulk assign by semester ───────────────────────────────────────────────
@frappe.whitelist(allow_guest=True, methods=["POST"])
def bulk_assign_fees(data):
    data = _parse(data)
    semester      = data.get("semester")
    fee_type      = data.get("fee_type")
    academic_year = data.get("academic_year", "")
    due_date      = data.get("due_date")
    override_amt  = data.get("override_amount")
    override_amt  = flt(override_amt) if override_amt not in (None, "", "null") else None

    if not semester or not due_date:
        frappe.throw(_("Semester and Due Date are required."))
    if not fee_type:
        frappe.throw(_("Fee Type is required."))

    students = frappe.get_all(
        "Student",
        filters={"status": "Active"},
        fields=["name", "full_name", "program"],
    )

    fee_struct_dt = "Program Fee Structure"
    has_sem_struct = frappe.db.has_column(fee_struct_dt, "semester")
    has_sem_fee    = frappe.db.has_column("Student Fee", "semester")

    created, skipped, failed = 0, 0, []

    for s in students:
        try:
            f = {"program": s.program, "fee_type": fee_type, "is_active": 1}
            if has_sem_struct:
                f["semester"] = semester

            struct = frappe.db.get_value(
                fee_struct_dt, f, ["name", "amount"], as_dict=True
            )

            if not struct and override_amt is None:
                skipped += 1
                continue

            amount = override_amt if override_amt is not None else flt(struct.amount)

            dup = {
                "student": s.name,
                "fee_type": fee_type,
                "academic_year": academic_year,
            }
            if has_sem_fee:
                dup["semester"] = semester
            if frappe.db.exists("Student Fee", dup):
                skipped += 1
                continue

            payload = {
                "doctype":            "Student Fee",
                "student":            s.name,
                "student_name":       s.full_name,
                "program":            s.program,
                "academic_year":      academic_year,
                "fee_type":           fee_type,
                "due_date":           due_date,
                "total_amount":       amount,
                "paid_amount":        0,
                "outstanding_amount": amount,
                "payment_status":     _compute_status(amount, 0, due_date),
            }
            if has_sem_fee:
                payload["semester"] = semester

            frappe.get_doc(payload).insert(ignore_permissions=True)
            created += 1
        except Exception as e:
            failed.append({"student": s.name, "error": str(e)})
            frappe.log_error(title="Bulk Fee Assign", message=frappe.get_traceback())

    frappe.db.commit()
    return {
        "message": f"Created {created}. Skipped {skipped}. Failed {len(failed)}.",
        "created": created,
        "skipped": skipped,
        "failed":  failed,
    }
