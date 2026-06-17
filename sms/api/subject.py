"""
Subject management — CRUD + faculty assignment.
"""
import frappe
from frappe import _


# ════════════════════════════════════════════════════════════════════════════
# READ
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True)
def list_subjects(department=None, year_level=None, is_active=1):
    """List subjects, optionally filtered."""
    filters = {}
    if department:
        filters["department"] = department
    if year_level:
        filters["year_level"] = year_level
    if is_active is not None:
        filters["is_active"] = int(is_active)

    subjects = frappe.get_all(
        "Subject",
        filters=filters,
        fields=[
            "name", "subject_code", "subject_name", "department",
            "year_level", "credits", "is_lab", "is_active",
        ],
        order_by="department asc, year_level asc, subject_name asc",
        limit_page_length=0,
    )

    # Add faculty list for each subject
    for s in subjects:
        faculty = frappe.get_all(
            "Subject Faculty Map",
            filters={"subject": s["name"]},
            fields=["faculty", "is_primary"],
        )
        s["faculty_list"] = []
        for f in faculty:
            full_name = frappe.db.get_value("User", f["faculty"], "full_name") or f["faculty"]
            s["faculty_list"].append({
                "email": f["faculty"],
                "name": full_name,
                "is_primary": bool(f["is_primary"]),
            })

    return subjects


@frappe.whitelist(allow_guest=True)
def get_subject(name):
    """Get a single subject with its faculty."""
    if not name or not frappe.db.exists("Subject", name):
        frappe.throw(_("Subject not found"))

    doc = frappe.get_doc("Subject", name).as_dict()
    faculty = frappe.get_all(
        "Subject Faculty Map",
        filters={"subject": name},
        fields=["name", "faculty", "is_primary", "year_level"],
    )
    for f in faculty:
        f["faculty_name"] = frappe.db.get_value(
            "User", f["faculty"], "full_name"
        ) or f["faculty"]
    doc["faculty_mappings"] = faculty

    return doc


@frappe.whitelist(allow_guest=True)
def get_faculty_for_subject(subject):
    """Get all faculty assigned to a subject."""
    if not subject:
        return []
    rows = frappe.get_all(
        "Subject Faculty Map",
        filters={"subject": subject},
        fields=["faculty", "is_primary", "year_level"],
        order_by="is_primary desc",
    )
    for r in rows:
        r["full_name"] = frappe.db.get_value("User", r["faculty"], "full_name") or r["faculty"]
    return rows


# ════════════════════════════════════════════════════════════════════════════
# CREATE / UPDATE / DELETE
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_subject(data):
    """Admin/HOD creates a new subject."""
    import json
    if isinstance(data, str):
        data = json.loads(data)

    if not data.get("subject_code"):
        frappe.throw(_("Subject code is required"))
    if not data.get("subject_name"):
        frappe.throw(_("Subject name is required"))

    doc = frappe.get_doc({
        "doctype":     "Subject",
        "subject_code": data["subject_code"].upper().strip(),
        "subject_name": data["subject_name"].strip(),
        "department":  data.get("department"),
        "year_level":  data.get("year_level"),
        "credits":     int(data.get("credits") or 3),
        "is_lab":      1 if data.get("is_lab") else 0,
        "is_active":   1 if data.get("is_active", 1) else 0,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": "Subject created"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_subject(name, data):
    """Update a subject."""
    import json
    if isinstance(data, str):
        data = json.loads(data)

    doc = frappe.get_doc("Subject", name)
    for field in ["subject_name", "department", "year_level", "credits",
                  "is_lab", "is_active"]:
        if field in data:
            setattr(doc, field, data[field])

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Subject updated"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def delete_subject(name):
    """Delete a subject (only if no timetable slots use it)."""
    used_in = frappe.db.count("Timetable Slot", {"subject": name})
    if used_in > 0:
        frappe.throw(_(
            "Cannot delete subject — it is used in {0} timetable slot(s). "
            "Deactivate it instead."
        ).format(used_in))

    frappe.delete_doc("Subject", name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Subject deleted"}


# ════════════════════════════════════════════════════════════════════════════
# Faculty assignment (max 2 per subject)
# ════════════════════════════════════════════════════════════════════════════
@frappe.whitelist(allow_guest=True, methods=["POST"])
def assign_faculty(subject, faculty, is_primary=0):
    """Assign a faculty to a subject. Max 2 faculty per subject."""
    if not frappe.db.exists("Subject", subject):
        frappe.throw(_("Subject not found"))
    if not frappe.db.exists("User", faculty):
        frappe.throw(_("Faculty user not found"))

    # Check max 2 rule
    existing_count = frappe.db.count("Subject Faculty Map", {"subject": subject})
    already_assigned = frappe.db.exists("Subject Faculty Map", {
        "subject": subject, "faculty": faculty,
    })

    if already_assigned:
        frappe.throw(_("This faculty is already assigned to this subject"))

    if existing_count >= 2:
        frappe.throw(_(
            "Maximum 2 faculty allowed per subject. "
            "Remove one before adding another."
        ))

    subject_doc = frappe.get_doc("Subject", subject)
    doc = frappe.get_doc({
        "doctype":    "Subject Faculty Map",
        "subject":    subject,
        "faculty":    faculty,
        "is_primary": 1 if int(is_primary) else 0,
        "year_level": subject_doc.year_level,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": "Faculty assigned"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def remove_faculty(mapping_name):
    """Remove a faculty assignment."""
    frappe.delete_doc("Subject Faculty Map", mapping_name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Faculty removed from subject"}
