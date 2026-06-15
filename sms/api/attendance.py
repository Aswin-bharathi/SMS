import frappe


def _apply_student_defaults(data):
    student = data.get("student")
    if not student:
        return data

    student_row = frappe.get_value(
        "Student",
        student,
        ["full_name", "department", "academic_year", "batch"],
        as_dict=True,
    )
    if not student_row:
        return data

    data.setdefault("student_name", student_row.full_name)
    data.setdefault("department", student_row.department)
    data.setdefault("academic_year", student_row.academic_year)
    data.setdefault("batch", student_row.batch)
    return data


@frappe.whitelist(allow_guest=True)
def get_attendance(
    student=None,
    course=None,
    status=None,
    department=None,
    batch=None,
    academic_year=None,
    attendance_hour=None,
    from_date=None,
    to_date=None
):
    filters = {}
    if student: filters["student"] = student
    if course: filters["course"] = course
    if status: filters["status"] = status
    if department: filters["department"] = department
    if batch: filters["batch"] = batch
    if academic_year: filters["academic_year"] = academic_year
    if attendance_hour: filters["attendance_hour"] = attendance_hour
    if from_date and to_date:
        filters["attendance_date"] = ["between", [from_date, to_date]]

    return frappe.get_all(
        "Student Attendance",
        filters=filters,
        fields=["name", "student", "student_name", "course", "department",
                "academic_year", "batch", "attendance_date", "attendance_hour",
                "status", "remarks"],
        order_by="attendance_date desc, attendance_hour asc"
    )

@frappe.whitelist(allow_guest=True)
def get_attendance_summary(student):
    data = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabStudent Attendance`
        WHERE student = %s
        GROUP BY status
    """, (student,), as_dict=True)
    return data

@frappe.whitelist(allow_guest=True, methods=["POST"])
def mark_attendance(data):
    import json
    if isinstance(data, str):
        data = json.loads(data)
    data = _apply_student_defaults(data)

    if not data.get("attendance_hour"):
        data["attendance_hour"] = "1"

    existing = frappe.db.exists("Student Attendance", {
        "student": data.get("student"),
        "course": data.get("course"),
        "attendance_date": data.get("attendance_date"),
        "attendance_hour": data.get("attendance_hour"),
    })
    if existing:
        doc = frappe.get_doc("Student Attendance", existing)
        doc.update(data)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "name": doc.name, "updated": True}

    doc = frappe.get_doc({"doctype": "Student Attendance", **data})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": doc.name}
