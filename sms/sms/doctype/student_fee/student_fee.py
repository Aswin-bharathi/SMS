import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class StudentFee(Document):
    def validate(self):
        self.apply_program_fee_structure()
        self.calculate_outstanding()

    def apply_program_fee_structure(self):
        if not self.program or not self.fee_type:
            return

        amount = frappe.db.get_value(
            "Program Fee Structure",
            {
                "program": self.program,
                "fee_type": self.fee_type,
                "is_active": 1,
            },
            "amount",
        )
        if amount is not None:
            self.total_amount = float(amount)

    def calculate_outstanding(self):
        if self.paid_amount and self.paid_amount > self.total_amount:
            frappe.throw("Paid Amount cannot exceed Total Amount.")

        self.outstanding_amount = self.total_amount - (self.paid_amount or 0)

        if (self.paid_amount or 0) == 0:
            self.payment_status = "Unpaid"
        elif self.outstanding_amount > 0:
            self.payment_status = "Partially Paid"
        else:
            self.payment_status = "Paid"

        if self.payment_status in ["Unpaid", "Partially Paid"]:
            if self.due_date and getdate(self.due_date) < getdate(today()):
                self.payment_status = "Overdue"
