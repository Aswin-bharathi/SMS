import json
import frappe
from frappe import _
from frappe.utils import nowdate, getdate


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════
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
    return {"name": doc.name, "message": f"{doctype} created"}


def _update_doc(doctype, name, data):
    doc = frappe.get_doc(doctype, name)
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": f"{doctype} updated"}


def _delete_doc(doctype, name):
    frappe.delete_doc(doctype, name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": f"{doctype} deleted"}


# ════════════════════════════════════════════════════════════════════════════
# Read endpoints (dropdowns)
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def get_programs():
    return _as_list(frappe.get_all(
        "Program",
        fields=["name", "program_name", "program_code", "department",
                "is_active", "duration_years", "total_credits"],
        order_by="program_name asc",
        limit_page_length=0,
    ))


@frappe.whitelist(allow_guest=True)
def get_academic_years():
    return _as_list(frappe.get_all(
        "Academic Year",
        fields=["name", "year_name", "start_date", "end_date", "is_current"],
        order_by="year_name desc",
        limit_page_length=0,
    ))


@frappe.whitelist(allow_guest=True)
def get_course_options():
    return _as_list(frappe.get_all(
        "Course",
        fields=["name", "course_name", "course_code", "department",
                "academic_year", "batch"],
        order_by="course_name asc",
        limit_page_length=0,
    ))


@frappe.whitelist(allow_guest=True)
def get_departments():
    return _as_list(frappe.get_all(
        "Department",
        fields=["name", "department_name", "department_code", "is_active"],
        order_by="department_name asc",
        limit_page_length=0,
    ))


@frappe.whitelist(allow_guest=True)
def get_batches():
    try:
        rows = frappe.get_all(
            "Student",
            fields=["batch"],
            filters={"batch": ["!=", ""]},
            group_by="batch",
            order_by="batch desc",
            limit_page_length=0,
        )
        return [{"name": r.batch, "batch": r.batch} for r in rows if r.batch]
    except Exception:
        return []


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_student_options(search=None):
    """Return students for dropdowns. Falls back gracefully if a field is missing."""
    # Detect which fields actually exist on the Student doctype
    desired = ["name", "student_id", "full_name", "program",
               "department", "academic_year", "batch", "status"]
    meta = frappe.get_meta("Student")
    available = {f.fieldname for f in meta.fields}
    fields = [f for f in desired if f == "name" or f in available]

    if search:
        or_filters = [
            ["full_name", "like", f"%{search}%"],
        ]
        if "student_id" in available:
            or_filters.append(["student_id", "like", f"%{search}%"])
        return _as_list(frappe.get_all(
            "Student",
            or_filters=or_filters,
            fields=fields,
            order_by="creation desc",
            limit_page_length=500,
        ))

    return _as_list(frappe.get_all(
        "Student",
        fields=fields,
        order_by="creation desc",
        limit_page_length=500,
    ))


# ════════════════════════════════════════════════════════════════════════════
# Fee Structure (your actual doctype is "Program Fee Structure")
# ════════════════════════════════════════════════════════════════════════════
FEE_STRUCTURE_DOCTYPE = "Program Fee Structure"


@frappe.whitelist(allow_guest=True)
def get_fee_structures(program=None, fee_type=None, semester=None):
    """Return fee structures. Includes semester / academic_year / due_date if those fields exist."""
    filters = {}
    if program:    filters["program"]    = program
    if fee_type:   filters["fee_type"]   = fee_type
    if semester:   filters["semester"]   = semester

    desired = ["name", "program", "fee_type", "amount", "is_active",
               "semester", "academic_year", "due_date"]
    meta = frappe.get_meta(FEE_STRUCTURE_DOCTYPE)
    available = {f.fieldname for f in meta.fields}
    fields = [f for f in desired if f == "name" or f in available]

    return _as_list(frappe.get_all(
        FEE_STRUCTURE_DOCTYPE,
        filters=filters,
        fields=fields,
        order_by="program asc, fee_type asc",
        limit_page_length=0,
    ))


@frappe.whitelist(allow_guest=True)
def get_semester_options():
    """
    Distinct semesters from Program Fee Structure (if the field exists).
    Falls back to Sem 1–Sem 8 so the dropdown is never empty.
    """
    options = []
    try:
        meta = frappe.get_meta(FEE_STRUCTURE_DOCTYPE)
        if any(f.fieldname == "semester" for f in meta.fields):
            rows = frappe.db.sql(
                f"""SELECT DISTINCT semester
                    FROM `tab{FEE_STRUCTURE_DOCTYPE}`
                    WHERE semester IS NOT NULL AND semester != ''
                    ORDER BY semester""",
                as_dict=True,
            )
            options = [r.semester for r in rows if r.semester]
    except Exception as e:
        frappe.log_error(f"get_semester_options: {e}")

    if not options:
        # Always return something so the UI is usable
        options = [f"Sem {i}" for i in range(1, 9)]

    return options


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_fee_structure(data):
    return _create_doc(FEE_STRUCTURE_DOCTYPE, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_fee_structure(structure_name, data):
    return _update_doc(FEE_STRUCTURE_DOCTYPE, structure_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_fee_structure(structure_name):
    return _delete_doc(FEE_STRUCTURE_DOCTYPE, structure_name)


# ════════════════════════════════════════════════════════════════════════════
# Department CRUD
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_department(data):
    return _create_doc("Department", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_department(department_name, data):
    return _update_doc("Department", department_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_department(department_name):
    return _delete_doc("Department", department_name)


# ════════════════════════════════════════════════════════════════════════════
# Program CRUD
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_program(data):
    return _create_doc("Program", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_program(program_name, data):
    return _update_doc("Program", program_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_program(program_name):
    return _delete_doc("Program", program_name)


# ════════════════════════════════════════════════════════════════════════════
# Academic Year CRUD
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_academic_year(data):
    return _create_doc("Academic Year", _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["PUT", "POST"])
def update_academic_year(year_name, data):
    return _update_doc("Academic Year", year_name, _parse_data(data))


@frappe.whitelist(allow_guest=True, methods=["DELETE", "POST"])
def delete_academic_year(year_name):
    return _delete_doc("Academic Year", year_name)
