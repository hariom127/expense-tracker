# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask-based personal expense tracker built as a step-by-step tutorial project. Large parts of the backend (database layer, auth, CRUD for expenses) are intentionally unimplemented placeholders — routes exist and return literal strings like `"Logout — coming in Step 3"` rather than real functionality. When working on this codebase, check whether the route/feature you're touching is one of these placeholders before assuming it's broken.

## Commands

```bash
# Activate the venv (already created at ./venv)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dev server (Flask debug mode, port 5001)
python app.py

# Run tests (pytest-flask is installed; no test files exist yet)
pytest
```

There is no build step, linter, or bundler configured — plain server-rendered HTML/CSS/JS.

## Architecture

- **`app.py`** — single-file Flask app. All routes are registered directly here (no blueprints). Implemented routes: `/` (landing), `/register`, `/login`, `/privacy-policy`, `/terms-and-conditions`. Placeholder routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) return plain strings and are marked with `# Step N` comments indicating future tutorial steps — do not treat these as bugs.
- **`database/db.py`** — stubbed out; intended to hold `get_db()` (SQLite connection with `row_factory` + foreign keys), `init_db()`, and `seed_db()`, per its header comment. Not yet implemented — there is currently no persistence layer, and `/register` and `/login` do not actually create or check accounts.
- **`templates/`** — Jinja2 templates, all extending `base.html` via `{% extends %}` / `{% block title/content/head/scripts %}`. `base.html` owns the `<head>` (Google Fonts, `style.css` link), navbar, and footer — shared across every page, so changes there affect the whole site, not just one page.
- **`static/css/style.css`** — single plain CSS file, no framework/preprocessor. Organized into commented sections (Variables, Reset, Navbar, Hero, Auth, Legal, Footer, Responsive). Design tokens are defined once as CSS custom properties in `:root` (colors: `--ink*`, `--paper*`, `--accent`, `--accent-2`, `--danger`; fonts: `--font-display` = DM Serif Display, `--font-body` = DM Sans; spacing/radius: `--radius-sm/md/lg`, `--max-width`) — reuse these instead of hardcoding values. Class naming is kebab-case, prefixed by component/section (`hero-*`, `mock-*`, `auth-*`, `legal-*`, `footer-*`, `btn-*`).
- **`static/js/main.js`** — empty stub; students add JS here as features are built.
- Responsive breakpoints used throughout: `@media (max-width: 900px)` and `@media (max-width: 600px)`.

## Conventions

- Keep new pages consistent with the existing template inheritance pattern (`{% extends "base.html" %}`, override `title`/`content` blocks) and route them through `app.py` with `render_template`.
- Reuse existing CSS custom properties and component classes (e.g. `.btn-primary`, `.btn-ghost`, `.auth-*`, `.legal-*`) before introducing new ones; match the existing kebab-case, section-prefixed naming when new classes are genuinely needed.
- Since `database/db.py` isn't implemented, any feature needing persistence should build out `get_db()`/`init_db()`/`seed_db()` there first rather than improvising ad hoc SQLite handling elsewhere.
