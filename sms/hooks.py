app_name = "sms"
app_title = "Sms"
app_publisher = "Your Name"
app_description = "Student Management System"
app_email = "your@email.com"
app_license = "MIT"


# ─── Document events: validators + auto-assignment ──────────────────────────
doc_events = {
    "Student": {
        "validate": [
            "sms.api.hierarchy.validate_unique_roll_number",
            "sms.api.hierarchy.normalize_student_id",     # ← NEW
        ],
        "before_save":  "sms.api.hierarchy.sync_department_from_batch",
        "after_insert": "sms.api.fee_structure.assign_existing_fees_to_new_student",
    },
    "Program Fee Structure": {
        "after_insert": "sms.api.fee_structure.auto_assign_to_batch",
        "on_update":    "sms.api.fee_structure.sync_batch_fees",
    },
}

scheduler_events = {
    "daily": [
        "sms.api.semester.auto_advance_semesters",
    ],
}

# ─── Row-level security (role-based queries) ────────────────────────────────
permission_query_conditions = {
    "Student":            "sms.permissions.student_query",
    "Student Attendance": "sms.permissions.attendance_query",
    "Student Fee":        "sms.permissions.student_fee_query",
    "Batch":              "sms.permissions.batch_query",
}
