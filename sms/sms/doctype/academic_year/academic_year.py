import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class AcademicYear(Document):
    def validate(self):
        if getdate(self.start_date) >= getdate(self.end_date):
            frappe.throw("End Date must be after Start Date.")
