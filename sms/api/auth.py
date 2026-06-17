"""
Authentication utilities for the Vue SPA.
"""
import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def whoami():
    """
    Return info about the currently logged-in user.
    Used by frontend to know who's logged in + their roles.
    """
    user = frappe.session.user

    if user == "Guest":
        return {
            "logged_in": False,
            "user": None,
            "full_name": None,
            "email": None,
            "roles": [],
            "is_admin": False,
            "is_staff": False,
            "is_student": False,
            "student_id": None,
            "batches": [],
        }

    user_doc = frappe.get_doc("User", user)
    roles = [r.role for r in user_doc.roles]

    # Detect SMS role flags
    is_admin   = "SMS Admin" in roles or "System Manager" in roles or user == "Administrator"
    is_staff   = "SMS Staff" in roles
    is_student = "SMS Student" in roles

    # If student, get their student record
    student_id = None
    if is_student:
        student_id = frappe.db.get_value("Student", {"user": user}, "name")

    # If staff, get the batches they're in-charge of
    batches = []
    if is_staff or is_admin:
        batches = frappe.get_all(
            "Batch",
            filters={"class_in_charge": user, "is_active": 1},
            fields=["name", "department", "batch_year", "current_semester"],
        )

    return {
        "logged_in":  True,
        "user":       user,
        "full_name":  user_doc.full_name,
        "email":      user_doc.email or user,
        "roles":      roles,
        "is_admin":   is_admin,
        "is_staff":   is_staff,
        "is_student": is_student,
        "student_id": student_id,
        "batches":    batches,
    }


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    """
    Custom login endpoint — wraps Frappe's auth and returns user info.
    """
    from frappe.auth import LoginManager

    try:
        login_manager = LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
        frappe.db.commit()
    except frappe.AuthenticationError:
        frappe.local.response["http_status_code"] = 401
        return {"success": False, "message": _("Invalid email or password")}
    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": str(e)}

    return {
        "success": True,
        "message": _("Login successful"),
        "user_info": whoami(),
    }


@frappe.whitelist(allow_guest=True)
def logout():
    """End the current session."""
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"success": True, "message": _("Logged out")}
