import json

import frappe


def _as_list(rows):
    return rows or []


def _parse_data(data):
    if isinstance(data, str):
        return json.loads(data)
    return data or {}


def _create_doc(doctype, data):
    doc = frappe.get_doc({"doctype": doctype, **data})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}


def _update_doc(doctype, name, data):
    doc = frappe.get_doc(doctype, name)
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}


def _delete_doc(doctype, name):
    frappe.delete_doc(doctype, name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist(allow_guest=True)
def get_programs():
    return _as_list(frappe.get_all(
        "Program",
        fields=["name", "program_name", "program_code", "department", "is_active"],
        order_by="program_name asc"
    ))


@frappe.whitelist(allow_guest=True)
def get_academic_years():
    return _as_list(frappe.get_all(
        "Academic Year",
        fields=["name", "year_name", "start_date", "end_date", "is_current"],
        order_by="year_name desc"
    ))


@frappe.whitelist(allow_guest=True)
def get_course_options():
    return _as_list(frappe.get_all(
        "Course",
        fields=["name", "course_name", "course_code", "department", "academic_year", "batch"],
        order_by="course_name asc"
    ))


@frappe.whitelist(allow_guest=True)
def get_departments():
    return _as_list(frappe.get_all(
        "Department",
        fields=["name", "department_name", "department_code", "is_active"],
        order_by="department_name asc"
    ))


@frappe.whitelist(allow_guest=True)
def get_batches():
    rows = frappe.get_all(
        "Student",
        fields=["batch"],
        filters={"batch": ["!=", ""]},
        group_by="batch",
        order_by="batch desc"
    )
    return [{"name": row.batch, "batch": row.batch} for row in rows if row.batch]


@frappe.whitelist(allow_guest=True)
def get_student_options(search=None):
    filters = {}
    if search:
        filters = {"name": ["like", f"%{search}%"]}
    students = frappe.get_all(
        "Student",
        filters=filters,
        fields=["name", "student_id", "full_name", "program", "department", "academic_year", "batch", "status"],
        order_by="creation desc",
        limit_page_length=200
    )
    return _as_list(students)


@frappe.whitelist(allow_guest=True)
def create_department(data):
    return _create_doc("Department", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_department(department_name, data):
    return _update_doc("Department", department_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_department(department_name):
    return _delete_doc("Department", department_name)


@frappe.whitelist(allow_guest=True)
def create_program(data):
    return _create_doc("Program", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_program(program_name, data):
    return _update_doc("Program", program_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_program(program_name):
    return _delete_doc("Program", program_name)


@frappe.whitelist(allow_guest=True)
def create_academic_year(data):
    return _create_doc("Academic Year", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_academic_year(year_name, data):
    return _update_doc("Academic Year", year_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_academic_year(year_name):
    return _delete_doc("Academic Year", year_name)


@frappe.whitelist(allow_guest=True)
def get_fee_structures(program=None, fee_type=None):
    filters = {}
    if program:
        filters["program"] = program
    if fee_type:
        filters["fee_type"] = fee_type
    return _as_list(frappe.get_all(
        "Program Fee Structure",
        filters=filters,
        fields=["name", "program", "fee_type", "amount", "is_active"],
        order_by="program asc, fee_type asc"
    ))


@frappe.whitelist(allow_guest=True)
def create_fee_structure(data):
    return _create_doc("Program Fee Structure", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_fee_structure(structure_name, data):
    return _update_doc("Program Fee Structure", structure_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_fee_structure(structure_name):
    return _delete_doc("Program Fee Structure", structure_name)
