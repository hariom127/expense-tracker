# Spec: Profile Page

## Overview
Implement a user profile page that displays the authenticated user's account information and expense overview. The page serves as the hub for logged-in users, showing their name, email, account creation date, a summary card containing their budget, total number of transactions, and top spending category, followed by a list of their recent transactions.

This page establishes the pattern for server-rendering user-specific data and protecting routes to authenticated users only. It integrates the existing users and expenses tables and sets the foundation for future CRUD operations on expenses (Steps 7–9).

## Depends on
Step 1 — Database Setup (users and expenses tables, seed data)  
Step 2 — Registration (users can create accounts)  
Step 3 — Login and Logout (users are authenticated; `session['user_id']` is set; `get_current_user()` helper and context processor exist)

## Routes
- `GET /profile` — Display the authenticated user's profile page with account information, expense summary cards, and recent transactions. Redirect unauthenticated users to `/login`. — logged-in

No new routes beyond `/profile` (which currently is a placeholder).

## Database changes
- No changes are required to the existing `users` or `expenses` tables for the account information, transaction count, total spending, or top category.
- **Budget:** The current schema does not contain a budget field. The source of the user's budget must be defined before implementation. If budget is intended to be user-specific and persisted, add a budget field/table in a separate database step rather than hardcoding it in the profile page.
- Do not introduce a database change solely to support the top category; it can be calculated from the existing `expenses` table.

## Templates
- **Create:** `templates/profile.html` — User profile page extending `base.html`.

The page must contain exactly these sections:

1. **Login user info**
   - User name
   - User email
   - Account creation date

2. **Budget, total transactions, and top category — card section**
   - Budget
   - Total number of transactions
   - Top spending category
   - The top category is the category with the highest total spending across the authenticated user's expenses.
   - Do not display the previous spending-by-category horizontal bar chart.

3. **Recent transactions list**
   - Display the user's 10 most recent transactions.
   - Each transaction shows:
     - Amount
     - Category
     - Date
     - Description
   - Transactions are sorted newest first.

- **Modify:** No existing templates need modification for this step.

## Files to change
- `app.py` —
  - Modify `GET /profile` handler to:
    - Check authentication: redirect unauthenticated users to `/login` using `if not session.get('user_id'): return redirect(url_for('login'))`
    - Fetch the current user's full information using `get_current_user()` (already exists)
    - Query the expenses table for the authenticated user
    - Calculate the total number of transactions
    - Calculate the user's top spending category by summing expense amounts grouped by category and selecting the category with the highest total
    - Retrieve the user's recent 10 transactions, sorted by date descending
    - Retrieve the user's budget from the agreed budget source
    - Render `profile.html` with user, budget, transaction summary, top category, and recent transaction data
- `static/css/style.css` —
  - Add styles for the profile information section
  - Add styles for the summary cards containing budget, total transactions, and top category
  - Add styles for the recent transactions list
  - Add responsive breakpoints for the card and transaction-list layout
  - Remove or stop using styles that were specific to the removed spending chart if they are no longer needed
- No changes to `database/db.py` unless a persisted user budget is added as part of the budget data-source decision.

## Files to create
- `templates/profile.html` — Profile page template

## New dependencies
No new dependencies. All functionality uses existing Flask, Jinja2, and SQLite.

## Rules for implementation
- No SQLAlchemy or ORMs — use parameterised SQLite queries only.
- All database queries must use `?` placeholders and pass parameters as tuples.
- Protect the `/profile` route: unauthenticated users must be redirected to `/login`.
- Reuse the existing `get_current_user()` context processor so user information is available in templates.
- All templates extend `base.html` and use the standard `{% block title %}` / `{% block content %}` pattern.
- CSS must reuse existing design tokens (`--ink*`, `--paper*`, `--accent`, `--radius-*`, `--max-width`, `--font-*`) and component classes.
- Follow kebab-case naming for any new CSS classes (for example, `profile-*`, `summary-card`, `transaction-*`).
- Display dates in ISO format (`YYYY-MM-DD`) or a human-readable format such as `Aug 8, 2026`.
- Display currency amounts as floats with 2 decimal places (for example, `12.50`).
- The total transaction count must include all expenses belonging to the authenticated user.
- The top category must be calculated from the authenticated user's expenses based on the highest total spending amount per category.
- If the user has no transactions, the top category should display an appropriate empty state such as `No spending yet`.
- The recent transaction list must contain at most 10 expenses, sorted by date descending.
- Do not add a "Delete" or "Edit" button for expenses yet — those are future steps.
- Session must be used to determine the current user (via `session.get('user_id')` or `get_current_user()`) — never trust client-provided user IDs.
- Do not hardcode a user-specific budget. The budget must come from the agreed data source.

## Definition of done
- [ ] `GET /profile` displays the authenticated user's profile page.
- [ ] Unauthenticated users accessing `/profile` are redirected to `/login`.
- [ ] Profile page displays the logged-in user's name from the database.
- [ ] Profile page displays the logged-in user's email from the database.
- [ ] Profile page displays the account creation date from the database `created_at`.
- [ ] Profile page contains a summary card section with exactly three metrics:
  - [ ] Budget
  - [ ] Total transactions
  - [ ] Top spending category
- [ ] Budget is retrieved from the agreed budget data source and is not hardcoded.
- [ ] Total transactions accurately reflects the number of expenses belonging to the authenticated user.
- [ ] Top category is accurately calculated from the user's expenses based on total spending per category.
- [ ] Profile page does not display the previous spending-by-category horizontal bar chart.
- [ ] Profile page displays the user's most recent 10 transactions.
- [ ] Each transaction shows amount, category, date, and description.
- [ ] Transactions are sorted by date descending (newest first).
- [ ] Demo user (`demo@spendly.com`) can log in and view their profile.
- [ ] Profile values are calculated only from the authenticated user's data.
- [ ] Login/logout links in the navbar still work correctly while viewing the profile.
- [ ] Page is responsive on mobile, tablet, and desktop and reuses existing CSS breakpoints.
- [ ] The summary cards and transaction list are visually consistent with the existing design language.
- [ ] No SQL injection vulnerabilities — all database queries use parameterised statements.