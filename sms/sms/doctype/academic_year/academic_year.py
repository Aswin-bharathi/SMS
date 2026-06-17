import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class AcademicYear(Document):
    def validate(self):
        if getdate(self.start_date) >= getdate(self.end_date):
            frappe.throw("End Date must be after Start Date.")
        # Only one year should be current at a time
        if self.is_current:
            frappe.db.set_value(
                "Academic Year",
                {"name": ["!=", self.name], "is_current": 1},
                "is_current", 0
            )
