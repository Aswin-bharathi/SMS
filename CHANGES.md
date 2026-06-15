# Changes

This file lists the full changes made to upgrade the SMS student management app from static / partially wired screens into a data-driven system.

## Definitions

- `Student`: Core learner record, including personal, contact, and academic information.
- `Attendance`: Daily or hourly presence record for a student.
- `Fee`: Student fee invoice and payment record.
- `Result`: Exam result record for a student.
- `Course`: Academic course linked to a program and department.
- `Program`: Academic program that belongs to a department.
- `Department`: Academic department that owns programs and courses.
- `Academic Year`: Reporting year used for enrollment, batches, and records.
- `Fee Structure`: Fixed program-wise fee template used to populate fee invoices.

## Backend Changes

### 1. Dashboard analytics

- Expanded dashboard statistics in `sms/api/student.py`.
- Added totals for:
  - total students
  - active students
  - inactive students
  - total programs
  - total departments
  - total courses
- Added fee metrics:
  - total billed
  - total collected
  - total outstanding
  - collection rate
- Kept recent students, attendance, and enrollment trend data available for the frontend.

### 2. Sample/demo data

- Fixed the demo seed flow in `sms/api/student.py`.
- Added connected demo records for:
  - departments
  - programs
  - academic years
  - courses
  - students
  - attendance
  - fees
  - exam results
  - fee structures
- Corrected the earlier fee/result insertion logic so demo records are created reliably.

### 3. Dynamic student save flow

- Updated student create and update APIs in `sms/api/student.py`.
- Auto-fills:
  - department from program
  - batch from academic year
  - full name from first and last name
- This reduces form errors and keeps the student record consistent.

### 4. Meta/master data APIs

- Extended `sms/api/meta.py` to support:
  - list fetch for programs, departments, academic years, courses, batches, students
  - create, update, and delete for programs
  - create, update, and delete for departments
  - create, update, and delete for academic years
  - create, update, and delete for fee structures
- Added new fields to list APIs:
  - `Program.is_active`
  - `Department.is_active`
  - `Academic Year.start_date`
  - `Academic Year.end_date`
  - `Academic Year.is_current`

### 5. Course behavior

- Updated `sms/api/course.py`.
- Program selection now auto-fills department where possible.
- Create/update flows are consistent with the linked master data.

### 6. Attendance behavior

- Updated `sms/api/attendance.py`.
- Student selection now backfills:
  - student name
  - department
  - academic year
  - batch
- Attendance deduplication remains enforced by student, course, date, and hour.

### 7. Result behavior

- Updated `sms/api/result.py`.
- Student selection auto-fills student name and academic year.
- Result entries continue to calculate grades and pass/fail status from child rows.

### 8. Fee behavior

- Updated `sms/api/fee.py`.
- Fee records now pull their base amount from `Program Fee Structure`.
- Fee list returns:
  - program
  - fee type
  - payment method
  - transaction id
- Payment flow now supports fixed billing amounts and remaining balance tracking.

### 9. Fee structure doctype

- Added a new backend doctype:
  - `Program Fee Structure`
- This stores fixed program-wise fee amounts for each fee type.
- Validation prevents duplicate active fee rules for the same program and fee type.

### 10. Student fee validation

- Updated `sms/sms/doctype/student_fee/student_fee.py`.
- Fee invoice total amount is now driven by the matching active fee structure.
- Outstanding amount and payment status are recalculated from the invoice data.

## Frontend Changes

### 1. Dashboard redesign and analytics

- Expanded the dashboard to show richer operational insight without changing the overall app style.
- Added:
  - additional KPI cards
  - program health panel
  - quick summary panel
  - improved fee collection display
  - stronger attendance visibility
- Kept existing chart areas and layout structure intact.

### 2. Master management screens

- Added frontend CRUD screens for:
  - departments
  - programs
  - academic years
  - fee structures
- These screens allow full frontend operation for master data management.

### 3. Status handling fixes

- Program, department, and academic-year status indicators now work correctly.
- Fixed the truthy/falsey handling so active/inactive badges reflect real data.

### 4. Removed unneeded description columns

- Removed description columns from:
  - programs
  - departments
- Kept the UI cleaner and closer to your requested workflow.

### 5. Fee form improvements

- Fee amount is now read-only in the main fee entry screen.
- Payment entry now shows:
  - base fee
  - paid amount
  - remaining amount
- Added transaction ID input for payment tracking.
- Fee selection now uses the program fee structure.

### 6. Student form improvements

- Student form now auto-syncs:
  - department
  - batch
  - program-linked data
- This reduces manual entry and flow mistakes.

### 7. Attendance form improvements

- Student selection changed to linked dropdowns instead of free-text-only entry.
- The selected student now carries the correct academic context into attendance records.

### 8. Course form improvements

- Course form now uses linked dropdowns for:
  - program
  - department
  - academic year
- This keeps course records aligned with master data.

### 9. Routing and navigation

- Added routes for:
  - departments
  - programs
  - academic years
  - fee structures
- Added these modules to the sidebar and settings shortcuts.

### 10. App shell cleanup

- Fixed root app styling so the page fills the screen correctly.
- Kept the visual theme and layout language consistent.

## Data Flow Definitions

- `Student -> Program -> Department`: student academic fields now resolve from linked records instead of manual typing.
- `Student -> Fee Structure -> Fee`: fee invoices use program-wise fixed amounts.
- `Student -> Attendance`: attendance records auto-fill program context.
- `Student -> Results`: student results keep academic year in sync.
- `Dashboard`: now aggregates live counts, fee status, attendance, program mix, and recent records.

## Verification

- Frontend production build completed successfully.
- Backend Python syntax checks completed successfully.

## Errors Encountered During The Session

These were the main issues we hit while upgrading the app and how they were resolved:

### 1. No data was showing in the UI

- Problem: dashboard, student list, and other modules were rendering empty even though sample data was expected.
- Cause: the frontend still depended on static or incomplete data paths, and some demo records were not wired correctly.
- Fix: added proper backend list APIs, corrected demo seeding, and switched screens to dynamic fetches.

### 2. Academic year dates were not displaying

- Problem: the academic year screen showed the year name, but the start and end dates were missing.
- Cause: the API and view were not both returning and rendering the date fields correctly.
- Fix: updated the academic year API to return `start_date`, `end_date`, and `is_current`, then rendered them in the frontend.

### 3. Program and department status stayed inactive

- Problem: the status toggle/button appeared stuck on inactive.
- Cause: the frontend was treating the status field inconsistently, and the backend response did not always normalize the active flag.
- Fix: normalized `is_active` handling in the API and updated the UI to use the real boolean/numeric value.

### 4. Attendance flow was too manual

- Problem: attendance had to be entered student by student, which did not match real classroom workflow.
- Cause: the page was built around a modal form instead of a course roster.
- Fix: redesigned attendance into a course-first roster with per-student mark/edit actions.

### 5. Fee totals were editable when they should not be

- Problem: the total fee amount could be manually changed instead of following the program fee structure.
- Cause: the fee screen was still using free entry behavior.
- Fix: introduced fixed program fee structures and made the fee total read-only in the fee entry flow.

### 6. Linked fields were not auto-filling reliably

- Problem: some forms did not auto-populate program, department, batch, or academic year values.
- Cause: the save flow was not consistently resolving linked master data.
- Fix: added backend defaults and synchronized the frontend with those linked values.

### 7. Duplicate attendance handling was too rigid

- Problem: late arrival or corrected attendance needed editing, but the flow did not clearly support updating existing records.
- Cause: attendance was validated for uniqueness, but the UI did not expose a clean edit path.
- Fix: kept the duplicate protection, but made the save path behave like an update when the same student/course/date/hour already exists.

## Notes

- UI structure was preserved.
- The app is now much more data-driven and less dependent on hardcoded values.
- The new fee structure module is the core piece that makes fee totals deterministic and easier to manage.
