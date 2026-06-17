"""
Semester auto-progression logic.
Run via scheduled job every day; it only acts when due.
"""
import frappe
from frappe.utils import getdate, nowdate, add_months


def auto_advance_semesters():
    """
    For each active batch, advance current_semester if 6 months have
    passed since the batch's modified date or last semester change.
    """
    today = getdate(nowdate())
    advanced = []

    for b in frappe.get_all("Batch",
        filters={"is_active": 1},
        fields=["name", "batch_year", "current_semester",
                "total_semesters", "modified"],
        limit_page_length=0):

        if not b.current_semester:
            continue

        # Parse current semester number
        try:
            current_num = int(b.current_semester.replace("Sem ", "").strip())
        except (ValueError, AttributeError):
            continue

        # Determine target semester from batch year
        try:
            start_year = int(b.batch_year.split("-")[0])
        except (ValueError, IndexError, AttributeError):
            continue

        # Each academic year covers 2 semesters
        years_elapsed = today.year - start_year
        # Adjust for mid-year start (assuming July start)
        if today.month < 7:
            years_elapsed -= 1

        target_sem = (years_elapsed * 2) + 1
        # Bump to next sem if we're past January
        if today.month >= 1 and today.month <= 6:
            target_sem += 1

        # Cap at total_semesters
        max_sem = b.total_semesters or 8
        target_sem = max(1, min(target_sem, max_sem))

        if target_sem > current_num:
            new_sem = f"Sem {target_sem}"
            frappe.db.set_value("Batch", b.name, "current_semester", new_sem)

            # Also bump every student in this batch
            for s in frappe.get_all("Student",
                filters={"batch": b.name, "status": "Active"},
                pluck="name"):
                frappe.db.set_value("Student", s, "semester", new_sem)

            advanced.append(f"{b.name}: Sem {current_num} → Sem {target_sem}")

    if advanced:
        frappe.db.commit()
        # Log to Error Log so admins can see the action
        frappe.log_error(
            title="Semester Auto-Advance",
            message="\n".join(advanced),
        )

    return advanced


@frappe.whitelist()
def run_now():
    """Admin can trigger this manually from a button."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Managers can run this.")
    return {"advanced": auto_advance_semesters()}
