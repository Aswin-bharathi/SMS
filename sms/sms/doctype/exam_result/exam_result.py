import frappe
from frappe.model.document import Document

class ExamResult(Document):
    def validate(self):
        self.calculate_results()

    def calculate_results(self):
        total_marks = 0
        total_max = 0
        has_fail = False

        for row in self.results:
            if row.marks_obtained > row.max_marks:
                frappe.throw(
                    f"Row {row.idx}: Marks obtained cannot exceed max marks for {row.course}"
                )
            row.percentage = (row.marks_obtained / row.max_marks * 100) if row.max_marks else 0
            row.grade = self.calculate_grade(row.percentage)
            if row.percentage < 40:
                has_fail = True
            total_marks += row.marks_obtained
            total_max += row.max_marks

        self.total_marks = total_marks
        self.total_max_marks = total_max
        self.overall_percentage = (total_marks / total_max * 100) if total_max else 0
        self.overall_grade = self.calculate_grade(self.overall_percentage)
        self.result_status = "Fail" if has_fail else "Pass"

    @staticmethod
    def calculate_grade(percentage):
        if percentage >= 90: return "A+"
        elif percentage >= 80: return "A"
        elif percentage >= 70: return "B+"
        elif percentage >= 60: return "B"
        elif percentage >= 50: return "C"
        elif percentage >= 40: return "D"
        else: return "F"
