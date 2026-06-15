import frappe
from frappe.model.document import Document

class Program(Document):
    def validate(self):
        if self.program_code:
            self.program_code = self.program_code.upper()
