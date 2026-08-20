# Query helpers for the profile page.
# Pure data access — no Flask imports. Each helper opens its own connection
# via get_db() and closes it before returning.

from datetime import datetime

from database.db import get_db

NO_CATEGORY = "—"


def _format_member_since(created_at):
    """Turn a stored created_at value into 'Month YYYY' (e.g. 'January 2026')."""
    if not created_at:
        return ""
    raw = str(created_at)
    for value, fmt in ((raw, "%Y-%m-%d %H:%M:%S"), (raw[:10], "%Y-%m-%d")):
        try:
            return datetime.strptime(value, fmt).strftime("%B %Y")
        except ValueError:
            continue
    return raw


def get_user_by_id(user_id):
    """Return the user's display details, or None when no such user exists."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": _format_member_since(row["created_at"]),
    }


def get_summary_stats(user_id):
    """Return total spent, transaction count and the highest-spending category."""
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        top = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    return {
        "total_spent": totals["total"],
        "transaction_count": totals["count"],
        "top_category": top["category"] if top else NO_CATEGORY,
    }


def get_recent_transactions(user_id, limit=10):
    """Return the user's most recent expenses, newest first."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


def get_category_breakdown(user_id):
    """Return spending per category, largest first, with integer percentages.

    Percentages are rounded to the nearest integer; the largest category
    absorbs any rounding remainder so the values always sum to 100.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    total_spent = sum(row["total"] for row in rows)
    breakdown = [
        {
            "name": row["category"],
            "amount": row["total"],
            "pct": int(round(row["total"] / total_spent * 100)) if total_spent else 0,
        }
        for row in rows
    ]

    if total_spent:
        breakdown[0]["pct"] += 100 - sum(item["pct"] for item in breakdown)

    return breakdown
