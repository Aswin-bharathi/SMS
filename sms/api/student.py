import frappe
import json
from frappe import _
from frappe.utils import add_months, nowdate
from collections import OrderedDict
from sms.sms.doctype.student.student import make_student_roll_number


def _serialise_doc(doc):
    result = doc.as_dict()
    for key, val in list(result.items()):
        if hasattr(val, "isoformat"):
            result[key] = str(val)
    return result


def _insert_if_missing(doctype, name, data):
    if name and frappe.db.exists(doctype, name):
        return False
    doc = frappe.get_doc({"doctype": doctype, **data})
    doc.insert(ignore_permissions=True)
    return True


# ============================================================
# DASHBOARD STATS
# ============================================================

@frappe.whitelist(allow_guest=True)
def get_dashboard_stats(months=6):
    try:
        months = int(months or 6)
        return {
            "totals": _get_totals(),
            "fee_stats": _get_fee_stats(),
            "attendance": _get_today_attendance(),
            "enrollment_trend": _get_enrollment_trend(months),
            "by_program": _get_students_by_program(),
            "recent_students": _get_recent_students(),
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_dashboard_stats failed")
        frappe.throw(_("Unable to fetch dashboard stats"))


def _get_totals():
    if not frappe.db.exists("DocType", "Student"):
        return {
            "total_students": 0,
            "active_students": 0,
            "inactive_students": 0,
            "total_programs": 0,
            "total_courses": 0,
        }

    total = frappe.db.count("Student")
    active = total

    if frappe.db.has_column("Student", "status"):
        active = frappe.db.count("Student", {"status": "Active"})
    elif frappe.db.has_column("Student", "enabled"):
        active = frappe.db.count("Student", {"enabled": 1})

    programs = 0
    if frappe.db.exists("DocType", "Program"):
        programs = frappe.db.count("Program")

    departments = 0
    if frappe.db.exists("DocType", "Department"):
        departments = frappe.db.count("Department")

    courses = 0
    if frappe.db.exists("DocType", "Course"):
        courses = frappe.db.count("Course")

    return {
        "total_students": total,
        "active_students": active,
        "inactive_students": total - active,
        "total_programs": programs,
        "total_departments": departments,
        "total_courses": courses,
    }


def _get_fee_stats():
    if not frappe.db.exists("DocType", "Student Fee"):
        return {"total_outstanding": 0, "total_billed": 0, "total_collected": 0, "collection_rate": 0}
    rows = frappe.db.sql("""
        SELECT
            COALESCE(SUM(total_amount), 0) AS total_billed,
            COALESCE(SUM(paid_amount), 0) AS total_collected,
            COALESCE(SUM(outstanding_amount), 0) AS total_outstanding
        FROM `tabStudent Fee`
    """, as_dict=True)
    billed = rows[0].total_billed if rows else 0
    collected = rows[0].total_collected if rows else 0
    outstanding = rows[0].total_outstanding if rows else 0
    collection_rate = round((collected / billed) * 100, 1) if billed else 0
    return {
        "total_billed": billed,
        "total_collected": collected,
        "total_outstanding": outstanding,
        "collection_rate": collection_rate,
    }


def _get_today_attendance():
    if not frappe.db.exists("DocType", "Student Attendance"):
        return {"present_today": 0, "absent_today": 0}
    return {
        "present_today": frappe.db.count("Student Attendance", {
            "attendance_date": nowdate(),
            "status": "Present"
        }),
        "absent_today": frappe.db.count("Student Attendance", {
            "attendance_date": nowdate(),
            "status": "Absent"
        }),
    }


def _get_enrollment_trend(months):
    start_date = add_months(nowdate(), -months + 1)
    rows = frappe.db.sql("""
        SELECT DATE_FORMAT(creation, '%%Y-%%m') AS month, COUNT(name) AS count
        FROM `tabStudent`
        WHERE creation >= %s
        GROUP BY month
        ORDER BY month ASC
    """, (start_date,), as_dict=True)

    trend = OrderedDict()
    for i in range(months):
        key = add_months(nowdate(), -months + 1 + i)[:7]
        trend[key] = 0
    for r in rows:
        trend[r.month] = r.count
    return [{"month": k, "count": v} for k, v in trend.items()]


def _get_students_by_program():
    if not frappe.db.has_column("Student", "program"):
        return []
    return frappe.db.sql("""
        SELECT COALESCE(program, 'Unassigned') AS program, COUNT(name) AS count
        FROM `tabStudent`
        GROUP BY program
        ORDER BY count DESC
    """, as_dict=True)


def _get_recent_students(limit=5):
    fields = ["name", "creation"]
    for f in ["student_name", "first_name", "last_name", "program", "department", "batch", "status"]:
        if frappe.db.has_column("Student", f):
            fields.append(f)
    students = frappe.get_all(
        "Student",
        fields=fields,
        order_by="creation desc",
        limit=limit
    )
    for s in students:
        if s.get("creation"):
            s["creation"] = str(s["creation"])
    return students


# ============================================================
# CRUD APIs
# ============================================================

@frappe.whitelist(allow_guest=True)
def get_all_students(
    page=1,
    page_size=20,
    search=None,
    program=None,
    status=None,
    department=None,
    batch=None,
    academic_year=None,
    filters=None
):
    try:
        page = int(page or 1)
        page_size = int(page_size or 20)
        start = (page - 1) * page_size

        filter_map = {}
        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
            filter_map.update(filters)
        if program:
            filter_map["program"] = program
        if status:
            filter_map["status"] = status
        if department:
            filter_map["department"] = department
        if batch:
            filter_map["batch"] = batch
        if academic_year:
            filter_map["academic_year"] = academic_year

        fields = ["name", "creation", "modified"]
        for f in ["student_id", "first_name", "last_name", "full_name",
                  "program_level", "program", "department", "academic_year", "batch",
                  "email", "phone", "status", "gender", "current_semester"]:
            if frappe.db.has_column("Student", f):
                fields.append(f)

        or_filters = None
        if search:
            or_filters = {}
            for sf in ["first_name", "last_name", "full_name", "student_id", "email", "name"]:
                or_filters[sf] = ["like", f"%{search}%"]

        students = frappe.get_all(
            "Student",
            fields=fields,
            filters=filter_map,
            or_filters=or_filters,
            order_by="creation desc",
            start=start,
            page_length=page_size
        )

        for s in students:
            for key in ["creation", "modified"]:
                if s.get(key):
                    s[key] = str(s[key])

        total = frappe.db.count("Student", filters=filter_map)

        return {
            "data": students,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_all_students failed")
        frappe.throw(_("Failed to fetch students"))


@frappe.whitelist(allow_guest=True)
def get_student(student_id):
    try:
        if not frappe.db.exists("Student", student_id):
            frappe.throw(_("Student not found"))
        doc = frappe.get_doc("Student", student_id)
        return _serialise_doc(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_student failed")
        frappe.throw(_("Failed to fetch student"))


@frappe.whitelist(allow_guest=True)
def create_student(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        data["doctype"] = "Student"
        if data.get("program") and not data.get("department"):
            data["department"] = frappe.db.get_value("Program", data["program"], "department")
        if data.get("academic_year") and not data.get("batch"):
            data["batch"] = data["academic_year"]
        if data.get("first_name") or data.get("last_name"):
            data["full_name"] = " ".join(filter(None, [data.get("first_name"), data.get("last_name")]))
        if not data.get("student_id"):
            data["student_id"] = make_student_roll_number(frappe._dict(data))
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return _serialise_doc(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "create_student failed")
        frappe.throw(_("Failed to create student"))


@frappe.whitelist(allow_guest=True)
def update_student(student_id, data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        if not frappe.db.exists("Student", student_id):
            frappe.throw(_("Student not found"))

        if data.get("program") and not data.get("department"):
            data["department"] = frappe.db.get_value("Program", data["program"], "department")
        if data.get("academic_year") and not data.get("batch"):
            data["batch"] = data["academic_year"]
        if data.get("first_name") or data.get("last_name"):
            data["full_name"] = " ".join(filter(None, [data.get("first_name"), data.get("last_name")]))

        doc = frappe.get_doc("Student", student_id)
        doc.update(data)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return _serialise_doc(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "update_student failed")
        frappe.throw(_("Failed to update student"))


@frappe.whitelist(allow_guest=True)
def delete_student(student_id):
    try:
        if not frappe.db.exists("Student", student_id):
            frappe.throw(_("Student not found"))
        frappe.delete_doc("Student", student_id, ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "message": "Student deleted successfully"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "delete_student failed")
        frappe.throw(_("Failed to delete student"))


@frappe.whitelist(allow_guest=True, methods=["POST"])
def seed_demo_data():
    """Create a connected demo dataset without duplicating existing records."""
    try:
        created = OrderedDict([
            ("departments", 0), ("programs", 0), ("academic_years", 0),
            ("courses", 0), ("fee_structures", 0), ("students", 0), ("attendance", 0),
            ("fees", 0), ("results", 0),
        ])

        for row in [
            {"department_name": "Computer Science", "department_code": "CSE", "head_of_department": "Dr. Meera Iyer", "description": "Computing, software systems, and data science"},
            {"department_name": "Business Administration", "department_code": "BBA", "head_of_department": "Prof. Arjun Rao", "description": "Management, finance, and entrepreneurship"},
        ]:
            created["departments"] += int(_insert_if_missing("Department", row["department_name"], row))

        for row in [
            {"program_name": "B.Tech Computer Science", "program_code": "BTCS", "department": "Computer Science", "duration_years": 4, "total_credits": 160, "description": "Undergraduate computer science engineering program"},
            {"program_name": "Bachelor of Business Administration", "program_code": "BBA", "department": "Business Administration", "duration_years": 3, "total_credits": 120, "description": "Undergraduate business administration program"},
        ]:
            created["programs"] += int(_insert_if_missing("Program", row["program_code"], row))

        created["academic_years"] += int(_insert_if_missing("Academic Year", "2026-27", {
            "year_name": "2026-27", "is_current": 1,
            "start_date": "2026-06-01", "end_date": "2027-05-31",
        }))

        for row in [
            {"course_name": "Data Structures", "course_code": "CS201", "program": "BTCS", "credits": 4, "instructor": "Dr. Neha Sharma", "semester": "3", "description": "Core data structures and algorithms"},
            {"course_name": "Database Management Systems", "course_code": "CS301", "program": "BTCS", "credits": 4, "instructor": "Prof. Karan Malhotra", "semester": "4", "description": "Relational databases, SQL, and transactions"},
            {"course_name": "Principles of Management", "course_code": "BA101", "program": "BBA", "credits": 3, "instructor": "Prof. Ritu Nair", "semester": "1", "description": "Management fundamentals and organizational behavior"},
        ]:
            created["courses"] += int(_insert_if_missing("Course", row["course_code"], row))

        for row in [
            {"program": "BTCS", "fee_type": "Tuition Fee", "amount": 75000, "is_active": 1},
            {"program": "BTCS", "fee_type": "Lab Fee", "amount": 12000, "is_active": 1},
            {"program": "BBA", "fee_type": "Tuition Fee", "amount": 55000, "is_active": 1},
            {"program": "BBA", "fee_type": "Library Fee", "amount": 5000, "is_active": 1},
        ]:
            exists = frappe.db.exists("Program Fee Structure", {
                "program": row["program"],
                "fee_type": row["fee_type"],
            })
            if not exists:
                doc = frappe.get_doc({"doctype": "Program Fee Structure", **row})
                doc.insert(ignore_permissions=True)
                created.setdefault("fee_structures", 0)
                created["fee_structures"] += 1

        students = [
            {"student_id": "STU-1001", "first_name": "Aarav", "last_name": "Sharma", "date_of_birth": "2005-03-12", "gender": "Male", "blood_group": "B+", "email": "aarav.sharma@example.com", "phone": "+91 9876543210", "address": "MG Road, Bengaluru", "guardian_name": "Rajesh Sharma", "guardian_phone": "+91 9876500011", "program": "BTCS", "department": "Computer Science", "academic_year": "2026-27", "current_semester": "3", "enrollment_date": "2026-06-03", "status": "Active"},
            {"student_id": "STU-1002", "first_name": "Diya", "last_name": "Patel", "date_of_birth": "2005-08-25", "gender": "Female", "blood_group": "O+", "email": "diya.patel@example.com", "phone": "+91 9876543211", "address": "Navrangpura, Ahmedabad", "guardian_name": "Nilesh Patel", "guardian_phone": "+91 9876500012", "program": "BTCS", "department": "Computer Science", "academic_year": "2026-27", "current_semester": "3", "enrollment_date": "2026-06-04", "status": "Active"},
            {"student_id": "STU-1003", "first_name": "Kabir", "last_name": "Khan", "date_of_birth": "2006-01-18", "gender": "Male", "blood_group": "A+", "email": "kabir.khan@example.com", "phone": "+91 9876543212", "address": "Bandra West, Mumbai", "guardian_name": "Sameer Khan", "guardian_phone": "+91 9876500013", "program": "BBA", "department": "Business Administration", "academic_year": "2026-27", "current_semester": "1", "enrollment_date": "2026-06-05", "status": "Active"},
            {"student_id": "STU-1004", "first_name": "Ananya", "last_name": "Menon", "date_of_birth": "2005-11-07", "gender": "Female", "blood_group": "AB+", "email": "ananya.menon@example.com", "phone": "+91 9876543213", "address": "Kakkanad, Kochi", "guardian_name": "Suresh Menon", "guardian_phone": "+91 9876500014", "program": "BBA", "department": "Business Administration", "academic_year": "2026-27", "current_semester": "1", "enrollment_date": "2026-06-06", "status": "Inactive"},
        ]
        for row in students:
            created["students"] += int(_insert_if_missing("Student", row["student_id"], row))

        for row in [
            {"student": "STU-1001", "course": "CS201", "attendance_date": nowdate(), "status": "Present", "remarks": "On time"},
            {"student": "STU-1002", "course": "CS201", "attendance_date": nowdate(), "status": "Late", "remarks": "Arrived after roll call"},
            {"student": "STU-1003", "course": "BA101", "attendance_date": nowdate(), "status": "Present", "remarks": ""},
            {"student": "STU-1004", "course": "BA101", "attendance_date": nowdate(), "status": "Absent", "remarks": "No prior notice"},
        ]:
            check_filter = {
                "student": row["student"], 
                "course": row["course"], 
                "attendance_date": row["attendance_date"],
                "attendance_hour": row.get("attendance_hour", "1")
            }
            exists = frappe.db.exists("Student Attendance", check_filter)
            
            if not exists:
                doc = frappe.get_doc({"doctype": "Student Attendance", **row})
                doc.insert(ignore_permissions=True)
                created["attendance"] += 1

        for row in [
            {"student": "STU-1001", "program": "BTCS", "academic_year": "2026-27", "fee_type": "Tuition Fee", "due_date": "2026-07-15", "total_amount": 75000, "paid_amount": 50000, "payment_date": "2026-06-12", "payment_method": "Online", "remarks": "First installment received"},
            {"student": "STU-1002", "program": "BTCS", "academic_year": "2026-27", "fee_type": "Lab Fee", "due_date": "2026-07-20", "total_amount": 12000, "paid_amount": 12000, "payment_date": "2026-06-13", "payment_method": "Bank Transfer", "remarks": "Paid in full"},
            {"student": "STU-1003", "program": "BBA", "academic_year": "2026-27", "fee_type": "Tuition Fee", "due_date": "2026-07-15", "total_amount": 55000, "paid_amount": 0, "remarks": "Pending"},
        ]:
            exists = frappe.db.exists("Student Fee", {
                "student": row["student"],
                "fee_type": row["fee_type"],
                "academic_year": row["academic_year"],
            })
            if not exists:
                doc = frappe.get_doc({"doctype": "Student Fee", **row})
                doc.insert(ignore_permissions=True)
                created["fees"] += 1

        for row in [
            {"student": "STU-1001", "academic_year": "2026-27", "exam_type": "Midterm", "semester": "3", "result_date": "2026-06-14", "results": [{"course": "CS201", "max_marks": 100, "marks_obtained": 86}, {"course": "CS301", "max_marks": 100, "marks_obtained": 79}]},
            {"student": "STU-1002", "academic_year": "2026-27", "exam_type": "Midterm", "semester": "3", "result_date": "2026-06-14", "results": [{"course": "CS201", "max_marks": 100, "marks_obtained": 91}, {"course": "CS301", "max_marks": 100, "marks_obtained": 88}]},
            {"student": "STU-1003", "academic_year": "2026-27", "exam_type": "Quiz", "semester": "1", "result_date": "2026-06-14", "results": [{"course": "BA101", "max_marks": 50, "marks_obtained": 41}]},
        ]:
            exists = frappe.db.exists("Exam Result", {
                "student": row["student"],
                "exam_type": row["exam_type"],
                "academic_year": row["academic_year"],
            })
            if not exists:
                doc = frappe.get_doc({"doctype": "Exam Result", **row})
                doc.insert(ignore_permissions=True)
                created["results"] += 1

        frappe.db.commit()
        return {"success": True, "created": created, "totals": _get_totals()}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "seed_demo_data failed")
        frappe.throw(_("Failed to seed demo data"))
