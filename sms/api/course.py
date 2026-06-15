import frappe
import json


def _apply_program_defaults(data):
    if data.get("program") and not data.get("department"):
        data["department"] = frappe.db.get_value("Program", data["program"], "department")
    return data


@frappe.whitelist(allow_guest=True)
def get_courses(program=None, department=None, batch=None, academic_year=None, is_active=None, search=None):
    filters = {}
    if program:
        filters["program"] = program
    if department:
        filters["department"] = department
    if batch:
        filters["batch"] = batch
    if academic_year:
        filters["academic_year"] = academic_year
    if is_active not in [None, ""]:
        filters["is_active"] = int(is_active)

    or_filters = None
    if search:
        or_filters = {
            "course_name": ["like", f"%{search}%"],
            "course_code": ["like", f"%{search}%"],
            "instructor": ["like", f"%{search}%"],
        }

    return frappe.get_all(
        "Course",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name", "course_name", "course_code", "program", "department", "academic_year", "batch",
            "credits", "instructor", "semester", "is_active", "description"
        ],
        order_by="modified desc"
    )


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_course(data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_program_defaults(data)
    doc = frappe.get_doc({"doctype": "Course", **data})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_course(course_name, data):
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_program_defaults(data)
    doc = frappe.get_doc("Course", course_name)
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_course(course_name):
    frappe.delete_doc("Course", course_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}
