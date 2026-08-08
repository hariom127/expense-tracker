# Spec: Registration

## Overview
Enable user account creation with validation, error handling, and secure password storage. This step implements the POST handler for the `/register` route, allowing users to sign up with their name, email, and password. Passwords are hashed using werkzeug before storage, and duplicate emails are rejected with a user-friendly error message.

## Depends on
Step 1 — Database Setup (users table, `get_db()`, `init_db()`, `seed_db()`)

## Routes
- `POST /register` — Accept registration form submission (name, email, password). Validate inputs, hash password, insert into users table, and redirect to `/login` on success or show error on failure. — public

## Database changes
No database changes. The users table from Step 1 already has all required columns: `id`, `name`, `email`, `password_hash`, `created_at`.

## Templates
- **Modify:** `templates/register.html` — Already has the form structure; ensure it displays server-side validation errors via the `error` variable and is ready to POST to `/register`.

## Files to change
- `app.py` — Add a POST handler to `/register` route that:
  - Accepts form data (name, email, password)
  - Validates: email is required, password is at least 8 characters, email is not already taken
  - Hashes password with `generate_password_hash()` from werkzeug
  - Inserts user into database
  - Redirects to `/login` on success
  - Re-renders form with error message on failure (validation error or duplicate email)

## Files to create
None. `templates/register.html` already exists.

## New dependencies
No new dependencies. `werkzeug.security` is already imported in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs — use parameterised SQLite queries only
- Passwords must be hashed with `generate_password_hash()` from `werkzeug.security`
- Use `request.method` to distinguish GET (show form) from POST (process submission)
- Email validation: reject if already exists in database (UNIQUE constraint may fire, but catch and display user-friendly error)
- Password validation: minimum 8 characters, required
- On success, redirect to `/login` (no auto-login)
- On failure, re-render `register.html` with `error` variable set to the error message
- Do not modify CSS or add new classes — reuse existing `.auth-*`, `.form-*`, `.btn-*` classes
- All templates extend `base.html` — do not change this pattern

## Definition of done
- [ ] POST `/register` accepts form data and validates inputs (required name/email, password ≥ 8 chars)
- [ ] Duplicate email is rejected with error message "An account with this email already exists"
- [ ] Valid registration inserts user into database with hashed password
- [ ] On success, user is redirected to `/login` and can log in with the password they entered
- [ ] On failure, form re-renders with error message preserved in input fields (or at least email/name if supported)
- [ ] Passwords are stored as hashes, never plaintext (verify in database)
- [ ] Demo user from `seed_db()` can still be created and is not duplicated on app restart
