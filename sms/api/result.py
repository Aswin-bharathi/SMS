import frappe
import json


def _apply_student_defaults(data):
    student = data.get("student")
    if not student:
        return data

    student_row = frappe.get_value(
        "Student",
        student,
        ["full_name", "academic_year"],
        as_dict=True,
    )
    if not student_row:
        return data

    data.setdefault("student_name", student_row.full_name)
    data.setdefault("academic_year", student_row.academic_year)
    return data


@frappe.whitelist(allow_guest=True)
def get_results(student=None, academic_year=None, exam_type=None):
    filters = {}
    if student: filters["student"] = student
    if academic_year: filters["academic_year"] = academic_year
    if exam_type: filters["exam_type"] = exam_type

    results = frappe.get_all(
        "Exam Result",
        filters=filters,
        fields=[
            "name", "student", "student_name", "academic_year",
            "exam_type", "semester", "result_date",
            "overall_percentage", "overall_grade", "result_status"
        ],
        order_by="result_date desc"
    )
    return results

@frappe.whitelist(allow_guest=True)
def get_result_detail(result_name):
    return frappe.get_doc("Exam Result", result_name).as_dict()

@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_result(data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_student_defaults(data)
    doc = frappe.get_doc({"doctype": "Exam Result", **data})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}

@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_result(result_name, data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_student_defaults(data)
    doc = frappe.get_doc("Exam Result", result_name)
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}

@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_result(result_name):
    frappe.delete_doc("Exam Result", result_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}
