# Student Management System

A Frappe app with a Vue 3 student-management dashboard. The app includes student records, attendance, fees, exam results, courses, settings, responsive UI, and PWA support for mobile installation.

## Features

- Student dashboard with charts, recent students, attendance summary, and program distribution
- Student list/detail pages with add, edit, delete, filters, export, and responsive table/grid views
- Attendance tracking with filters and mark-attendance modal
- Fees management with billing summaries and add/edit/delete actions
- Exam results management with course-wise marks and calculated grades
- Course management with add/edit/delete, active status, credits, semester, and instructor details
- Settings page with theme controls, PWA status, backend status, and shortcuts
- Dark mode, responsive layout, mobile sidebar, icons, animations, and custom scrollbars
- PWA manifest, service worker, and install prompt for production builds

## Tech Stack

- Backend: Frappe Framework
- Frontend: Vue 3, Vite, Pinia, Vue Router
- UI: Tailwind CSS, Lucide icons, Chart.js
- HTTP: Axios through Frappe `/api/method` endpoints

## Project Structure

```text
sms/
  api/                    # Whitelisted Frappe API methods
  sms/doctype/            # Frappe DocTypes
front-end/SMS/
  src/                    # Vue app source
  public/                 # Frontend static/PWA assets
public/student-app/       # Built Vue app served by Frappe
```

## Installation

From your bench directory:

```bash
bench get-app <repo-url> --branch develop
bench --site <site-name> install-app sms
bench --site <site-name> migrate
```

## Backend Development

Run Frappe from the bench root:

```bash
bench start
```

The Vue dev server proxies `/api` requests to:

```text
http://localhost:8000
```

If you add or rename Python API methods, restart the Frappe process so the updated whitelisted methods are loaded.

## Frontend Development

```bash
cd front-end/SMS
npm install
npm run dev -- --host 0.0.0.0
```

Open:

```text
http://localhost:5174/student-app/
```

The port may change if `5173` or `5174` is already in use.

## Build

```bash
cd front-end/SMS
npm run build
```

The production build is written to:

```text
public/student-app/
```

## PWA Notes

The service worker only registers in production builds. During Vite development, old `/student-app/` service workers are unregistered to avoid stale caches and auto-refresh issues.

## Useful Commands

```bash
# Compile backend Python files
python3 -m py_compile sms/api/*.py

# Build frontend
cd front-end/SMS && npm run build

# Lint frontend
cd front-end/SMS && npm run lint
```

## License

MIT
