import frappe
import json


def _apply_student_defaults(data):
    student = data.get("student")
    if not student:
        return data

    student_row = frappe.get_value(
        "Student",
        student,
        ["full_name", "program", "academic_year", "batch"],
        as_dict=True,
    )
    if not student_row:
        return data

    data.setdefault("student_name", student_row.full_name)
    data.setdefault("program", student_row.program)
    data.setdefault("academic_year", student_row.academic_year)
    return data


def _apply_fee_structure(data):
    program = data.get("program")
    fee_type = data.get("fee_type")
    if not program or not fee_type:
        return data

    amount = frappe.db.get_value(
        "Program Fee Structure",
        {
            "program": program,
            "fee_type": fee_type,
            "is_active": 1,
        },
        "amount",
    )
    if amount is not None:
        data["total_amount"] = float(amount)
    return data


@frappe.whitelist(allow_guest=True)
def get_fees(student=None, status=None, academic_year=None):
    filters = {}
    if student: filters["student"] = student
    if status: filters["payment_status"] = status
    if academic_year: filters["academic_year"] = academic_year

    return frappe.get_all(
        "Student Fee",
        filters=filters,
        fields=[
            "name", "student", "student_name", "program", "fee_type",
            "total_amount", "paid_amount", "outstanding_amount",
            "payment_status", "due_date", "payment_date", "academic_year", "transaction_id", "payment_method"
        ],
        order_by="due_date desc"
    )

@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_fee(data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_student_defaults(data)
    data = _apply_fee_structure(data)
    doc = frappe.get_doc({"doctype": "Student Fee", **data})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}

@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_fee(fee_name, data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_student_defaults(data)
    data = _apply_fee_structure(data)
    doc = frappe.get_doc("Student Fee", fee_name)
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}

@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_fee(fee_name):
    frappe.delete_doc("Student Fee", fee_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}

@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_payment(fee_name, paid_amount, payment_date, payment_method=None):
    doc = frappe.get_doc("Student Fee", fee_name)
    doc.paid_amount = float(paid_amount)
    doc.payment_date = payment_date
    if payment_method:
        doc.payment_method = payment_method
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "payment_status": doc.payment_status}
