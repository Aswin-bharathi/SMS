# Student Management UI

Vue 3 frontend for the Frappe Student Management System app.

## Features

- Responsive dashboard and app shell
- Students, attendance, fees, results, courses, and settings pages
- Add/edit/delete modals for management workflows
- Dark mode, icons, animations, custom scrollbars, and mobile sidebar
- PWA manifest, service worker, and install prompt

## Setup

```sh
npm install
```

## Development

```sh
npm run dev -- --host 0.0.0.0
```

The dev server proxies `/api` to the Frappe backend at `http://localhost:8000`.

Open the app at the shown Vite URL with `/student-app/`, for example:

```text
http://localhost:5174/student-app/
```

## Build

```sh
npm run build
```

The build output is written to:

```text
../../../sms/public/student-app
```

## Preview Production Build

```sh
npm run preview
```

## Lint

```sh
npm run lint
```

## PWA Behavior

The service worker registers only in production. In development, old `/student-app/` service workers are unregistered to prevent stale cache and unexpected refresh behavior.
