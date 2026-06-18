Excellent idea! 🎯 A solid `README.md` is the perfect handoff. Here's a comprehensive one that captures everything we've built, where we are, and exactly how to continue tomorrow.

---

## 📄 Create/Replace `README.md` at the project root

**Path:** `apps/sms/README.md`

```markdown
# 🎓 SMS — Student Management System

A modern, role-based Student Management System built on **Frappe Framework** (backend) with a **Vue 3 + Vite** frontend.

Implements a clean **Department → Batch → Students** hierarchy with hour-based attendance, timetable-driven workflows, fee management, and a substitution portal for class in-charges.

---

## 📊 Project Status (as of last session)

| Phase | Status | Notes |
|---|---|---|
| **Phase 1** — Data model foundations | ✅ Complete | Department, Batch, Student, Fees, Hour Slot, Subject, Timetable, Substitution |
| **Phase 2** — Backend APIs (hierarchy, fees, timetable) | ✅ Complete | All endpoints tested in `bench console` |
| **Phase 3** — Hierarchy UI (Academics → Batches → Detail) | ✅ Complete | Beautiful card-based drill-down navigation |
| **Phase 4-PRE** — Authentication (login/logout, session, role detection) | ✅ Complete | Vue auth guard, sidebar dropdown, role label |
| **Phase A** — Workflow redesign foundations | ✅ Complete | New DocTypes seeded, semesters auto-advance |
| **Phase B** — Timetable seeded | ✅ Complete | 30 slots for CS-2025-2029 Sem 2, 20 subject-faculty maps |
| **Phase C** — Workflow APIs (subject, timetable, attendance_v2, substitution) | ✅ Complete | All 4 APIs verified |
| **Phase D1** — `MyClassesView.vue` ("My Classes Today") | ✅ Complete | Faculty lands here, sees today's classes |
| **Phase D2** — `MarkAttendanceView.vue` (the marking screen) | 🟡 **In Progress** | First-time save works; bugs remaining (see below) |
| **Phase D3** — Substitutions UI | ⏭️ Next | Request + approve workflow |
| **Phase D4** — Subjects management UI (HOD) | ⏭️ Pending | CRUD + faculty assignment |
| **Phase D5** — Timetable editor UI (HOD grid) | ⏭️ Pending | Click-to-edit grid like the screenshot |
| **Phase E** — Full RBAC (Admin, HOD, Staff, Student, Accounts) | ⏭️ Pending | After D3-D5 complete |
| **Phase F** — Reports (attendance %, fee collection, exports) | ⏭️ Pending | Final phase |

---

## 🐛 Known Bugs in `MarkAttendanceView.vue` (resume point)

| # | Bug | Status |
|---|---|---|
| 1 | After first-time save, screen doesn't show "Update Attendance" mode with edit option for **same day** | 🔴 To fix |
| 2 | After midnight (12 AM), the screen still shows **yesterday's records** instead of empty for today | 🔴 To fix |
| 3 | Past hour's attendance shows editing enabled even for hours older than 24h | 🔴 To fix |
| 4 | First-time save with all-Present **works** ✅ |
| 5 | Visiting Mrs. SY's ADA class for today **works** ✅ |

**Next step:** Debug the date/time logic in `_hour_has_started()` and `_can_edit_for_date()` in `sms/api/attendance_v2.py`, and re-verify state computation in `get_marking_screen()`.

---

## 🏗 Architecture Overview

### Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Frappe Framework 15 (Python 3.11, MariaDB) |
| **Frontend** | Vue 3 + Vite + Tailwind CSS + lucide-vue-next icons |
| **State** | Vue Composition API (composables: `useAuth`, `useApi`) |
| **Routing** | Vue Router 4 with auth guard |
| **Auth** | Frappe session cookies, custom `whoami` endpoint |

### Directory Layout

```
apps/sms/
├── README.md                                # ← this file
├── sms/
│   ├── api/                                 # All whitelisted endpoints
│   │   ├── auth.py                          # whoami, login wrapper
│   │   ├── meta.py                          # dropdown options
│   │   ├── student.py                       # student CRUD
│   │   ├── fee.py                           # fee record CRUD + payments
│   │   ├── fee_structure.py                 # auto-assign fees to batch
│   │   ├── hierarchy.py                     # dept tree, batch detail, students by batch
│   │   ├── semester.py                      # auto-advance semesters (scheduled)
│   │   ├── subject.py                       # subject CRUD + faculty mapping
│   │   ├── timetable.py                     # timetable CRUD + "my classes today"
│   │   ├── attendance.py                    # OLD attendance (kept for compat)
│   │   ├── attendance_v2.py                 # NEW hour-based attendance
│   │   └── substitution.py                  # substitute staff workflow
│   ├── permissions.py                       # row-level security (RBAC)
│   ├── hooks.py                             # doc_events, scheduled jobs, RBAC wiring
│   └── (doctype folders auto-generated)
│
└── front-end/SMS/                           # Vue 3 app
    ├── vite.config.js                       # proxies /api → localhost:8000
    └── src/
        ├── App.vue
        ├── main.js
        ├── composables/
        │   ├── useApi.js                    # callApi(method, params, options)
        │   ├── useAuth.js                   # user, isLoggedIn, login(), logout()
        │   └── usePlural.js                 # "1 record" / "5 records"
        ├── components/
        │   ├── layout/
        │   │   ├── AppLayout.vue            # sidebar + main content shell
        │   │   ├── Sidebar.vue              # nav + user dropdown
        │   │   └── Navbar.vue
        │   └── ui/
        │       ├── Badge.vue
        │       ├── Card.vue
        │       └── Modal.vue
        ├── router/
        │   └── index.js                     # routes + auth guard
        └── views/
            ├── Dashboard.vue
            ├── Auth/
            │   └── LoginView.vue            # /login
            ├── Hierarchy/
            │   ├── DepartmentsView.vue      # /academics
            │   ├── BatchesView.vue          # /academics/:dept/batches
            │   ├── BatchDetailView.vue      # /batches/:batch
            │   ├── BatchAttendance.vue      # batch tab (old, read-only history)
            │   └── BatchFees.vue            # batch tab
            ├── Attendance/
            │   ├── MyClassesView.vue        # /attendance — faculty daily list
            │   └── MarkAttendanceView.vue   # /attendance/:slot/:date — marking screen
            ├── Fees/
            │   ├── FeeView.vue
            │   └── FeeStructureView.vue
            ├── Masters/
            │   ├── DepartmentView.vue
            │   ├── ProgramView.vue
            │   └── AcademicYearView.vue
            └── ... (Students, Courses, Results, Settings)
```

---

## 🗃 Data Model

### Core Hierarchy

```
Department
   └── Batch (CS-2025-2029, etc.)
         ├── class_in_charge (User)
         ├── current_semester (Sem 1 … Sem 8)
         ├── year_level (I UG, II UG, III UG, IV UG, I PG, II PG) — auto from sem
         ├── status (Active, Upcoming, Graduated, Archived) — auto-classified
         └── Students (linked via Student.batch)
                ├── roll_number (unique per dept+batch)
                ├── user (linked User account, SMS Student role)
                └── ... (full_name, email, gender, etc.)
```

### Academic Plumbing

```
Subject
   ├── subject_code (ADA, C++, NME, …)
   ├── department, year_level
   ├── is_lab, credits
   └── Subject Faculty Map (max 2 faculty per subject)

Hour Slot (master data, 7 records)
   ├── Hour 1   10:00 – 11:00
   ├── Hour 2   11:00 – 12:00
   ├── Lunch    12:00 – 13:00  (is_break=1)
   ├── Hour 3   13:00 – 14:00
   ├── Hour 4   14:00 – 15:00
   ├── Hour 5   15:00 – 16:00
   └── Hour 6   16:00 – 17:00

Timetable (one per batch+semester)
   ├── effective_from / effective_to
   ├── is_active
   └── Timetable Slot (child table)
         ├── day (Monday … Saturday)
         ├── hour → Hour Slot
         ├── subject → Subject
         ├── faculty → User
         ├── room (e.g. C15)
         └── is_lab
```

### Attendance + Substitution

```
Student Attendance
   ├── student, batch, department, date, hour
   ├── subject, faculty (auto from timetable_slot)
   ├── timetable_slot (audit reference)
   ├── substitution (Link to Staff Substitution if active)
   ├── status (Present, Absent, Late, On Leave)
   ├── marked_by, marked_at
   ├── last_edited_by, last_edited_at, edit_count
   └── UNIQUE(student, date, hour)

Staff Substitution
   ├── date, hour, timetable_slot, batch
   ├── original_faculty, substitute_faculty
   ├── reason
   ├── status (Pending, Approved, Rejected)
   └── requested_by, approved_by
```

### Fee Module

```
Program Fee Structure
   ├── department, batch, semester
   ├── fee_type (Tuition Fee, Exam Fee, …)
   ├── amount, due_date, academic_year
   └── is_active

Student Fee (auto-created when structure assigned to batch)
   ├── student, batch, department, semester
   ├── fee_structure (reference)
   ├── installment_label (e.g. "Installment 1 of 2")
   ├── total_amount, paid_amount, outstanding_amount
   └── payment_status (Unpaid, Partially Paid, Paid, Overdue)
```

---

## 🔐 Roles & Permissions

| Role | Created In Frappe? | Purpose | Sees |
|---|---|---|---|
| **System Manager** | ✅ Built-in | Frappe admin | Everything |
| **SMS Admin** | ✅ Created | App admin | Everything within SMS |
| **SMS Staff** | ✅ Created | Class in-charge / Faculty | Only their assigned batches + classes they teach |
| **SMS Student** | ✅ Created | Student portal | Own profile, attendance, fees only |
| **SMS HOD** | ⏭️ TBD | Department head | All batches/staff in own department |
| **SMS Accounts** | ⏭️ TBD | Fee management team | Fee module only across departments |

Row-level security is enforced via **`sms/permissions.py`** + `permission_query_conditions` in `hooks.py`:

```python
permission_query_conditions = {
    "Student":            "sms.permissions.student_query",
    "Student Attendance": "sms.permissions.attendance_query",
    "Student Fee":        "sms.permissions.student_fee_query",
    "Batch":              "sms.permissions.batch_query",
}
```

---

## 🧪 Seeded Test Data

### Departments (8)
Business Administration, Civil Engineering, Commerce, **Computer Science**, Electrical Engineering, Mathematics, **Mechanical Engineering**, (Department of Computer Science — duplicate, kept for legacy)

### Batches (5)
| Batch | Year | Current Sem | Year Level | In-Charge | Students |
|---|---|---|---|---|---|
| Computer Science-2023-2027 | 2023-2027 | Sem 6 | III UG | — | 0 |
| Computer Science-2025-2029 | 2025-2029 | Sem 2 | I UG | **Subitha** (subi83.k@gmail.com) | 14 |
| Computer Science-2026-2030 | 2026-2030 | Sem 1 | I UG | — | 2 |
| Mechanical Engineering-2023-2027 | 2023-2027 | Sem 6 | III UG | — | 0 |
| Mechanical Engineering-2026-2030 | 2026-2030 | Sem 1 | I UG | — | 1 |

### Students (17 total)
- **CS-2026-2030**: Aswin Bharathi M (23UCS019), Subitha K (25PCS114)
- **CS-2025-2029**: 14 test students (STU-1001 to STU-1014)
- **Mech-2026-2030**: Asanth M (23UCS119)

### Subjects (13, all under Computer Science)
ADA, AOS, C++, C++-LAB, CC, CYBER, DIP, DIP-LAB, DS, LINUX-LAB, NME, PRO-COM, PYTHON

### Faculty Users (7, placeholder emails)
| Email | Role | Password |
|---|---|---|
| mrs.sy@college.local | SMS Staff | `Faculty@123` |
| dr.ad@college.local | SMS Staff | `Faculty@123` |
| mr.ms@college.local | SMS Staff | `Faculty@123` |
| mrs.ks@college.local | SMS Staff | `Faculty@123` |
| mr.vv@college.local | SMS Staff | `Faculty@123` |
| mrs.ra@college.local | SMS Staff | `Faculty@123` |
| dr.jk@college.local | SMS Staff | `Faculty@123` |
| **subi83.k@gmail.com** | SMS Staff (real) | (user's own) |

### Subject ↔ Faculty Maps (20 records)
- ADA → SY (PRIMARY)
- C++ → MS (PRIMARY), RA (secondary)
- C++-LAB → SY (PRIMARY), KS (secondary)
- DIP → AD (PRIMARY), MS (secondary)
- ... (full list in Phase B output)

### Active Timetable (1)
`TT-Computer Science-2025-2029-Sem 2` — 30 slots covering Mon-Sat, Hours 1-5

### Fee Records (4)
- Aswin Bharathi M: Tuition Fee installments 1 & 2 (₹25,000 each, both PAID)
- Asanth M: Tuition Fee installments 1 & 2 (₹40,000 each)

---

## 🚀 Local Development Setup

### Backend (Frappe)

```bash
# Start bench
cd ~/frappe-bench
bench start

# In another terminal — access console
bench --site student.local console

# Run scheduled jobs manually (semester auto-advance, etc.)
bench --site student.local execute sms.api.semester.auto_advance_semesters

# Clear cache after backend changes
bench --site student.local clear-cache

# Migrate after schema changes
bench --site student.local migrate
```

### Frontend (Vue)

```bash
cd apps/sms/front-end/SMS
npm run dev        # starts Vite on http://localhost:5173
```

Open **http://localhost:5173/student-app/** in browser.

### Test Logins

| Role | Email | Password |
|---|---|---|
| Admin | `Administrator` | (set during bench setup) |
| Staff (Subitha, real account) | `subi83.k@gmail.com` | (user's own) |
| Staff (test) | `mrs.sy@college.local` | `Faculty@123` |
| Student | `asanth2712@gmail.com` | `Student@123` |

---

## 🔌 API Endpoint Reference

All endpoints are `@frappe.whitelist(allow_guest=True)` (auth handled by session cookie).

### Auth
- `sms.api.auth.whoami` — current user info + roles
- `frappe.client.login` (POST: usr, pwd)
- `frappe.client.logout`

### Hierarchy
- `sms.api.hierarchy.get_department_tree`
- `sms.api.hierarchy.get_batches_under_dept(department)`
- `sms.api.hierarchy.get_batch_detail(batch)`
- `sms.api.hierarchy.get_students_by_batch(batch)`
- `sms.api.hierarchy.get_overview_counts`

### Timetable
- `sms.api.timetable.list_timetables`
- `sms.api.timetable.get_timetable_grid(batch, semester=None)`
- `sms.api.timetable.get_my_classes_today(date=None, user=None)`
- `sms.api.timetable.create_timetable(data)` (POST)
- `sms.api.timetable.update_timetable_slot(slot_id, data)` (POST)

### Subjects
- `sms.api.subject.list_subjects(department, year_level, is_active)`
- `sms.api.subject.get_subject(name)`
- `sms.api.subject.get_faculty_for_subject(subject)`
- `sms.api.subject.create_subject(data)` (POST)
- `sms.api.subject.assign_faculty(subject, faculty, is_primary)` (POST)

### Attendance (NEW v2 — hour-based)
- `sms.api.attendance_v2.get_marking_screen(timetable_slot, date)`
- `sms.api.attendance_v2.save_attendance(timetable_slot, date, records)` (POST)
- `sms.api.attendance_v2.get_batch_attendance_history(batch, from_date, to_date, ...)`
- `sms.api.attendance_v2.get_student_attendance_percentage(student, from_date, to_date)`

### Substitution
- `sms.api.substitution.get_available_faculty(date, hour, department, exclude)`
- `sms.api.substitution.request_substitution(data)` (POST)
- `sms.api.substitution.approve_substitution(name)` (POST)
- `sms.api.substitution.reject_substitution(name, reason)` (POST)
- `sms.api.substitution.list_substitutions(status, faculty, from_date, to_date)`

### Fees
- `sms.api.fee.list_fees(student, status, semester, academic_year)`
- `sms.api.fee.create_fee(data)` (POST)
- `sms.api.fee.update_fee(name, data)` (POST)
- `sms.api.fee.record_payment(fee_name, amount, ...)` (POST)
- `sms.api.fee_structure.get_structures_for_batch(batch)`
- `sms.api.fee_structure.get_fees_by_batch(batch)`

### Meta / Dropdowns
- `sms.api.meta.get_programs`
- `sms.api.meta.get_departments`
- `sms.api.meta.get_academic_years`
- `sms.api.meta.get_student_options(search)`
- `sms.api.meta.get_fee_structures`
- `sms.api.meta.get_semester_options`
- `sms.api.meta.get_batches`

---

## ⚙️ Hooks Active in `hooks.py`

```python
# Document validation + auto-assignment
doc_events = {
    "Student": {
        "validate":     [
            "sms.api.hierarchy.validate_unique_roll_number",
            "sms.api.hierarchy.normalize_student_id",
        ],
        "before_save":  "sms.api.hierarchy.sync_department_from_batch",
        "after_insert": "sms.api.fee_structure.assign_existing_fees_to_new_student",
    },
    "Program Fee Structure": {
        "after_insert": "sms.api.fee_structure.auto_assign_to_batch",
        "on_update":    "sms.api.fee_structure.sync_batch_fees",
    },
}

# Row-level security
permission_query_conditions = {
    "Student":            "sms.permissions.student_query",
    "Student Attendance": "sms.permissions.attendance_query",
    "Student Fee":        "sms.permissions.student_fee_query",
    "Batch":              "sms.permissions.batch_query",
}

# Scheduled jobs
scheduler_events = {
    "daily": [
        "sms.api.semester.auto_advance_semesters",
    ],
}
```

---

## 📋 Workflow Specification (Locked Design)

### 1. Student Creation
- ✅ **Single source of truth**: students are added **only from the Batch Detail page**
- ❌ No "+ Add Student" button anywhere else
- ✅ Roll number is **unique per (department, batch)** — auto-validated
- ✅ Department + semester are **auto-filled from selected batch**

### 2. Attendance Workflow
- ✅ Marked **hour-by-hour**, not per-day
- ✅ Faculty lands on `/attendance` → sees only their classes for today (from timetable)
- ✅ Click → opens marking screen showing **subject + auto-loaded roster**
- ✅ Bulk actions: "All Present" / "All Absent" / "Reset"
- ✅ Edit window: **24h for faculty**, **always for admin**
- ❌ **Future dates** cannot be marked (only after class hour starts)
- ❌ **Archived batches** never accept new attendance (historical view only)
- ❌ Past hours (>24h) are read-only for faculty

### 3. Timetable Rules
- ✅ One timetable per **(batch, semester)** combo
- ✅ Lab slots = 2 separate Timetable Slot rows (same subject/faculty)
- ✅ Max **2 faculty per subject** (enforced in `Subject Faculty Map`)
- ✅ HOD creates/edits timetables; faculty are assigned per slot
- ✅ Lunch (12-1) is a non-attendance break slot

### 4. Substitution Flow
- Faculty requests substitution → HOD approves
- HOD can directly assign (auto-approved)
- System shows available faculty (free at that hour, same dept preferred)
- On approved date, attendance marking uses the substitute as effective faculty

### 5. Semester Auto-Advancement
- Daily scheduled job (`auto_advance_semesters`)
- Advances batches based on `batch_year` + months elapsed
- Bumps all students in the batch to new semester simultaneously

### 6. Fee Auto-Assignment
- When a `Program Fee Structure` is created for (department + batch), system **auto-creates Student Fee records** for every active student in that batch
- When a new student is added to a batch, system **auto-applies all active structures** of that batch

---

## 📚 How to Continue Tomorrow (Resume Guide)

### Read This Section First
1. Open this README
2. Check **"Project Status"** table at top
3. Check **"Known Bugs"** section to see exactly where we stopped

### Resume Plan

**Current Position:** Phase D2 — `MarkAttendanceView.vue` has 3 bugs to fix.

#### Step 1: Verify backend is still healthy
```bash
bench --site student.local console
```
```python
from sms.api.attendance_v2 import get_marking_screen
# Get a slot ID
import frappe
slot = frappe.db.get_value("Timetable Slot",
    {"parent": "TT-Computer Science-2025-2029-Sem 2", "day": "Monday", "hour": "Hour 1"},
    "name")
result = get_marking_screen(slot, "2026-06-17")
print({k: v for k, v in result.items() if k not in ('students',)})
```

#### Step 2: Pick up where we left off
Tell the AI assistant:
> "Continuing SMS project from yesterday. We're at Phase D2. Read README.md.
> The 3 bugs in MarkAttendanceView.vue still need fixing:
> 1. After save, screen doesn't refresh to show 'Update Attendance' mode
> 2. After midnight, old date's records appear
> 3. Past hours show editable when they shouldn't
> Let's fix the backend `_hour_has_started()` and `_can_edit_for_date()` first."

#### Step 3: Phases ahead (in order)
1. **D2 Bug Fixes** ← resume here
2. **D3** — Substitutions UI (`/substitutions` page)
3. **D4** — Subjects management UI (`/subjects` page)
4. **D5** — Timetable Editor UI (`/timetables/:id` grid)
5. **Sidebar cleanup** — remove flat "Students" link, reorganize by role
6. **BatchDetailView refactor** — attendance tab → read-only history
7. **Phase E (RBAC)** — full role gating
8. **Phase F (Reports)** — attendance %, fee collection, exports

---

## 🐛 Quick Debugging Reference

### Auth not working
```bash
# Check current session
bench --site student.local console
import frappe
print(frappe.session.user)
```

### Frontend can't reach backend
Check `vite.config.js` proxy:
```js
'/api': {
  target: 'http://localhost:8000',
  changeOrigin: true,
}
```

### Reset a user's password
```python
from frappe.utils.password import update_password
update_password("mrs.sy@college.local", "Faculty@123")
frappe.db.commit()
```

### See all SMS roles + users
```python
import frappe
for role in ["SMS Admin", "SMS Staff", "SMS Student"]:
    users = frappe.db.sql("""
        SELECT u.name FROM `tabUser` u
        INNER JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = %s
    """, (role,))
    print(f"{role}: {[u[0] for u in users]}")
```

### Clear DocType cache after schema change
```bash
bench --site student.local clear-cache
bench --site student.local migrate
```

### Hard refresh browser
- `Ctrl + Shift + R` (Chrome/Firefox)
- DevTools open → right-click reload → "Empty Cache and Hard Reload"

---

## 📝 Change Log

| Date | Phase | Description |
|---|---|---|
| Day 1 | Setup | Initial Frappe app, basic Vue scaffolding |
| Day 2 | 1-2 | Department, Batch, Student, Fee doctypes + APIs |
| Day 3 | 3 | Hierarchy navigation UI complete (Academics page) |
| Day 4 | Auth | Login page, useAuth composable, sidebar dropdown |
| Day 5 | A | Subject, Hour Slot, Subject Faculty Map, Timetable doctypes |
| Day 5 | B | Seeded 13 subjects, 7 faculty users, 20 mappings, 30 slots |
| Day 5 | C | 4 new API files (subject, timetable, attendance_v2, substitution) |
| Day 5 | D1 | MyClassesView complete — daily class list works |
| Day 5 | D2 | MarkAttendanceView in progress — first-save works, edit flow buggy |

---

## 🤝 Conventions

### Backend
- All APIs use `@frappe.whitelist(allow_guest=True)` (session auth)
- POST methods declared as `methods=["POST"]`
- Datetime fields normalized with `getdate()`, `nowdate()`, `now_datetime()`
- Field types follow Frappe conventions (Link, Data, Select, Int, Date, Datetime, Check)
- DB column names match field names

### Frontend
- Composables in `src/composables/` (camelCase: `useAuth`, `useApi`)
- Views grouped by feature in `src/views/<Feature>/`
- Tailwind utility classes — no separate CSS files (except for transitions)
- All forms use Vue's `v-model` + manual validation; no Vuelidate yet
- API calls via `useApi().callApi(method_path, params, { method: 'POST' })`

### Naming
- DocType names: TitleCase ("Student Fee", "Hour Slot")
- Field names: snake_case (`student_id`, `payment_status`)
- API endpoints: `sms.api.<module>.<function_name>` snake_case
- Vue components: PascalCase (`BatchDetailView.vue`)
- Routes: kebab-case paths, PascalCase names

---

## 📦 Tech Versions

- Python 3.11
- Frappe Framework 15.x
- MariaDB 10.6
- Node 20.x
- Vue 3.x + Vite 5.x + Tailwind 3.x

---

## 🔗 Useful Links

- Frappe Docs: https://frappeframework.com/docs
- Vue 3 Docs: https://vuejs.org/
- Tailwind: https://tailwindcss.com/docs
- Lucide Icons: https://lucide.dev/

---

**Last updated:** _After Phase D2 (Mark Attendance UI) — first-save works, edit flow has 3 bugs pending._
**Next session:** Fix D2 bugs → proceed to D3 (Substitutions UI).
```

---

## 📋 Save Instructions

```bash
cd ~/frappe-bench/apps/sms
# Open README.md in your editor (VS Code, nano, etc.)
nano README.md
# Paste the entire content above
# Save (Ctrl+O, Enter, Ctrl+X in nano)
```

Verify:
```bash
ls -la README.md
head -20 README.md
```

---
✅ Bug 1: After save → switches to "Update Attendance" mode correctly
✅ Bug 2: Date handling → server-side nowdate() always correct
✅ Bug 3: Edit window → time-aware check using hour end time
✅ Root cause: Student Attendance DocType had mandatory 'course' + 'attendance_hour' fields blocking saves

----
