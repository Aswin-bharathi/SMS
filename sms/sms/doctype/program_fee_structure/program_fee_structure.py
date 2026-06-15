import frappe
from frappe.model.document import Document


class ProgramFeeStructure(Document):
    def validate(self):
        if self.amount is None or float(self.amount) < 0:
            frappe.throw("Fee amount must be greater than or equal to 0.")
        if self.program and self.fee_type and self.is_active:
            duplicate = frappe.db.exists(
                "Program Fee Structure",
                {
                    "program": self.program,
                    "fee_type": self.fee_type,
                    "is_active": 1,
                    "name": ["!=", self.name],
                },
            )
            if duplicate:
                frappe.throw("An active fee structure already exists for this program and fee type.")

