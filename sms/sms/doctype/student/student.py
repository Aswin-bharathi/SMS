import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Student(Document):
    def before_insert(self):
        if not self.student_id:
            self.student_id = make_student_roll_number(self)

    def before_save(self):
        self.full_name = f"{self.first_name} {self.last_name}"
        if not self.batch and self.academic_year:
            self.batch = self.academic_year

    def validate(self):
        if not self.student_id:
            self.student_id = make_student_roll_number(self)
        self.validate_dob()
        self.validate_email()

    def validate_dob(self):
        if self.date_of_birth:
            if getdate(self.date_of_birth) >= getdate(today()):
                frappe.throw("Date of Birth must be in the past.")

    def validate_email(self):
        if self.email:
            if not frappe.utils.validate_email_address(self.email):
                frappe.throw("Please enter a valid Email Address.")


def make_student_roll_number(doc):
    academic_year = doc.academic_year or ""
    year = academic_year[:2] if len(academic_year) >= 2 else today()[2:4]
    level = doc.program_level or "UG"
    department_code = get_department_code(doc.department) if doc.department else get_program_department_code(doc.program)
    prefix = f"{year}-{level}-{department_code}"
    latest = frappe.db.sql(
        """
        SELECT student_id
        FROM `tabStudent`
        WHERE student_id LIKE %s
        ORDER BY student_id DESC
        LIMIT 1
        """,
        (f"{prefix}-%",),
        as_dict=True,
    )
    next_number = 1
    if latest:
        try:
            next_number = int(latest[0].student_id.rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            next_number = frappe.db.count("Student", {"department": doc.department}) + 1
    return f"{prefix}-{next_number:03d}"


def get_program_department_code(program):
    if not program:
        return "GEN"
    department = frappe.db.get_value("Program", program, "department")
    return get_department_code(department)


def get_department_code(department):
    if not department:
        return "GEN"
    code = frappe.db.get_value("Department", department, "department_code")
    return code or department[:3].upper()
