import frappe
from frappe.model.document import Document

class StudentAttendance(Document):
    def validate(self):
        existing = frappe.db.exists("Student Attendance", {
            "student": self.student,
            "course": self.course,
            "attendance_date": self.attendance_date,
            "attendance_hour": self.attendance_hour,  # Added this line
            "name": ["!=", self.name]
        })
        if existing:
            frappe.throw(
                f"Attendance already marked for {self.student_name} "
                f"in {self.course} on {self.attendance_date}"
            )
