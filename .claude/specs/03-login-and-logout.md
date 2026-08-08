# Spec: Login and Logout

## Overview
Implement user authentication with session management and authenticated route protection. The login feature validates user credentials against the database and creates a session, allowing authenticated users to access protected routes and see an authenticated navbar. The logout feature destroys the session and returns the user to the landing page. Authenticated users are redirected away from `/login` and `/register` to prevent re-authentication. The navbar dynamically reflects authentication state — showing login/register links when unauthenticated, and user info + logout when authenticated. All auth state is server-side (Flask session), never frontend-only.

## Depends on
Step 1 — Database Setup (users table with email and password_hash columns)
Step 2 — Registration (users can create accounts with hashed passwords)

## Routes
- `GET /login` — Display login form with email and password fields. Redirect authenticated users to `/`. — public/authenticated
- `POST /login` — Accept login form submission (email, password). Validate credentials against users table, create session if valid, redirect to `/` on success or show generic error on failure. — public
- `GET /logout` — Clear the current session and redirect to `/`. Accessible whether authenticated or not. — public/authenticated
- **Route protection:** Authenticated users attempting to access `/login` or `/register` are redirected to `/`.

## Database changes
No database changes. The users table already has all required columns: `email` and `password_hash`.

## Templates
- **Modify:** `templates/base.html` — Update navbar to conditionally show links based on authentication state:
  - When unauthenticated (no `session['user_id']`): Show "Sign in" and "Get started" links (current behavior)
  - When authenticated: Hide "Sign in" and "Get started"; instead show user's name and a "Sign out" link
  - Use Jinja2 session context variable to determine state (e.g., `{% if session.get('user_id') %}...{% endif %}`)
- **Modify:** `templates/login.html` — Ensure it displays server-side validation errors via the `error` variable and POST form submission is ready to be processed.

## Files to change
- `app.py` — 
  - Configure Flask session security:
    - Set `app.secret_key` from environment variable (or hardcoded for development only)
    - Configure `SESSION_COOKIE_HTTPONLY=True`
    - Configure `SESSION_COOKIE_SAMESITE="Lax"`
  - Import `session` and `check_password_hash` from werkzeug.security
  - Add a helper function `get_current_user()` that returns the user dict from the database if logged in, or None if not:
    - Check if `session.get('user_id')` exists
    - If yes, query users table for that id and return the row
    - If no, return None
    - Use this to pass user data to templates
  - Implement `GET /login` handler that:
    - Check if user is already authenticated (`session.get('user_id')`)
    - If authenticated, redirect to `/`
    - Otherwise, render login form
  - Implement `POST /login` handler that:
    - Accepts form data (email, password)
    - Validates that both email and password are provided
    - Normalize email by trimming and converting to lowercase
    - Queries users table for matching email
    - Verifies password using `check_password_hash()`
    - On success: clear existing session, set `session['user_id']`, redirect to `/`
    - On failure: show generic error "Invalid email or password" (do not distinguish between email/password errors)
    - Re-renders login form with error message
  - Modify `GET /register` handler to:
    - Check if user is already authenticated (`session.get('user_id')`)
    - If authenticated, redirect to `/`
    - Otherwise, render register form (existing behavior)
  - Implement `GET /logout` handler that:
    - Clears session with `session.clear()`
    - Redirects to `/`
  - Create a context processor or pass user data to all templates so navbar can access `session` and user info

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available in werkzeug, which is already installed.

## Session & Security
- Use Flask's built-in signed session cookie for authentication (client-side, not server-side database sessions).
- `SECRET_KEY` must be set from an environment variable in production; a hardcoded value is acceptable for local development only.
- Configure cookie security: `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE="Lax"`.
- Store only `user_id` in the session; never store password, password_hash, or email.
- Clear any existing session before establishing a new authenticated session on login.
- Use a generic "Invalid email or password" error for failed authentication attempts to prevent user/account enumeration.
- Normalize email input (trim whitespace, convert to lowercase) consistently with the registration flow.
- Rate limiting and brute-force protection are recommended but out of scope for this step.

## Rules for implementation
- No SQLAlchemy or ORMs — use parameterised SQLite queries only
- Passwords must be validated using `check_password_hash()` from `werkzeug.security`
- Use `request.method` to distinguish GET (show form) from POST (process submission)
- Use Flask's built-in signed session cookie (requires `from flask import session` and `app.secret_key` to be set)
- Session should store only `user_id` to identify the authenticated user
- Clear the existing session before establishing a new authenticated session on successful login
- Do not store password, password_hash, or email in the session
- Return a generic "Invalid email or password" error for authentication failures to prevent user enumeration
- Normalize email input by trimming whitespace and converting to lowercase before querying
- **Authenticated route protection:** GET `/login` and GET `/register` must redirect authenticated users to `/` using `if session.get('user_id'): return redirect(url_for('landing'))`
- **Authenticated navbar:** Pass user data or use Flask session context in templates so navbar can conditionally render based on `session.get('user_id')`. When authenticated, show user's name (fetched from database) and "Sign out" link; when unauthenticated, show "Sign in" and "Get started" links
- **User data for navbar:** Create a helper to fetch user dict from database (name, email) when needed, or pass it through a context processor so templates have access
- Authentication state is determined entirely by Flask `session['user_id']` — never rely on frontend-only state or cookies sent by the client
- Do not create duplicate auth logic; reuse the Flask session implementation everywhere
- After successful login, redirect to `/` (home page / landing)
- Do not modify CSS or add new classes — reuse existing `.auth-*`, `.form-*`, `.btn-*` classes
- All templates extend `base.html` — do not change this pattern
- Demo credentials are for development/testing only and must not be used in production
- Rate limiting/brute-force protection is recommended but out of scope for this step

## Definition of done

### Authentication (core login/logout)
- [ ] GET `/login` displays the login form
- [ ] POST `/login` accepts form data and validates inputs (required email/password)
- [ ] POST `/login` with missing email shows validation error "Email is required"
- [ ] POST `/login` with missing password shows validation error "Password is required"
- [ ] User can log in with correct email and password from registration
- [ ] Incorrect password shows generic error "Invalid email or password"
- [ ] Non-existent email shows generic error "Invalid email or password" (not "Email does not exist")
- [ ] On successful login, user is redirected to `/` (landing/home page)
- [ ] Session is created with `user_id` stored in `session` object (not email or password)
- [ ] Session does not contain password or password_hash
- [ ] GET `/logout` clears the session and redirects to `/`
- [ ] Accessing `/logout` without being logged in does not fail
- [ ] Demo user from `seed_db()` can log in with email "demo@spendly.com" and password "demo123"
- [ ] Email normalization works (e.g., "Demo@Spendly.com" and " demo@spendly.com " should both log in successfully)

### Route protection (authenticated users redirected from auth pages)
- [ ] Unauthenticated user can access GET `/login` and POST to it
- [ ] Authenticated user accessing GET `/login` is redirected to `/`
- [ ] Authenticated user accessing GET `/register` is redirected to `/`
- [ ] Unauthenticated user can still access `/register` normally

### Authenticated navbar display
- [ ] When unauthenticated, navbar shows "Sign in" and "Get started" links
- [ ] When authenticated, navbar hides "Sign in" and "Get started" links
- [ ] When authenticated, navbar shows the logged-in user's name (fetched from database)
- [ ] When authenticated, navbar shows a "Sign out" link (or similar logout control)
- [ ] Clicking "Sign out" in navbar clears the session and redirects to `/`
- [ ] After logout, "Sign in" and "Get started" links are visible again
- [ ] Navbar state is determined from Flask `session['user_id']`, not frontend state
