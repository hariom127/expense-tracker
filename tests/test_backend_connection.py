"""Tests for Step 5 — profile page backend connection.

Unit tests run against a throwaway SQLite file (database.db.DB_PATH is
monkeypatched per test). Route tests run against the real seeded dev database
via the Flask test client.
"""

import pytest

# Imported at module scope so the app's init_db()/seed_db() run against the
# real DB_PATH, before any test monkeypatches it.
from app import app as flask_app
from database import db as db_module
from database.db import get_db, init_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

SEED_EMAIL = "demo@spendly.com"
SEED_PASSWORD = "demo123"
SEED_NAME = "Demo User"
SEED_TOTAL = 284.74
SEED_COUNT = 8
SEED_TOP_CATEGORY = "Bills"
SEED_CATEGORY_COUNT = 7


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """An isolated database with one user who has expenses and one without."""
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))
    init_db()

    conn = get_db()
    with_expenses = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) "
        "VALUES (?, ?, ?, ?)",
        ("Test User", "test@example.com", "hash", "2026-01-15 10:00:00"),
    ).lastrowid
    without_expenses = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) "
        "VALUES (?, ?, ?, ?)",
        ("Empty User", "empty@example.com", "hash", "2025-11-02 08:30:00"),
    ).lastrowid

    # Three equal categories: 33.33% each, so rounding leaves a remainder of 1
    # that the largest category must absorb.
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            (with_expenses, 40.00, "Food", "2026-03-01", "Groceries"),
            (with_expenses, 60.00, "Food", "2026-03-05", "Restaurant"),
            (with_expenses, 100.00, "Bills", "2026-03-03", "Electricity"),
            (with_expenses, 100.00, "Transport", "2026-03-04", None),
        ],
    )
    conn.commit()
    conn.close()

    return {"with_expenses": with_expenses, "without_expenses": without_expenses}


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture
def seed_user_id():
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", (SEED_EMAIL,)
        ).fetchone()
    finally:
        conn.close()
    assert row is not None, "seed user missing — delete expense_tracker.db and rerun"
    return row["id"]


# ------------------------------------------------------------------ #
# get_user_by_id                                                      #
# ------------------------------------------------------------------ #


def test_get_user_by_id_returns_details(temp_db):
    user = get_user_by_id(temp_db["with_expenses"])
    assert user == {
        "name": "Test User",
        "email": "test@example.com",
        "member_since": "January 2026",
    }


def test_get_user_by_id_unknown_id_returns_none(temp_db):
    assert get_user_by_id(9999) is None


# ------------------------------------------------------------------ #
# get_summary_stats                                                   #
# ------------------------------------------------------------------ #


def test_get_summary_stats_with_expenses(temp_db):
    stats = get_summary_stats(temp_db["with_expenses"])
    assert stats["total_spent"] == pytest.approx(300.00)
    assert stats["transaction_count"] == 4
    # Food totals 100.00, tying with Bills and Transport; any of the three is a
    # valid top category, so assert on the total rather than the name here.
    assert stats["top_category"] in {"Food", "Bills", "Transport"}


def test_get_summary_stats_picks_highest_spending_category(temp_db):
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        (temp_db["with_expenses"], 500.00, "Shopping", "2026-03-06", "Laptop"),
    )
    conn.commit()
    conn.close()

    assert get_summary_stats(temp_db["with_expenses"])["top_category"] == "Shopping"


def test_get_summary_stats_without_expenses(temp_db):
    assert get_summary_stats(temp_db["without_expenses"]) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


# ------------------------------------------------------------------ #
# get_recent_transactions                                             #
# ------------------------------------------------------------------ #


def test_get_recent_transactions_newest_first(temp_db):
    transactions = get_recent_transactions(temp_db["with_expenses"])

    assert [t["date"] for t in transactions] == [
        "2026-03-05",
        "2026-03-04",
        "2026-03-03",
        "2026-03-01",
    ]
    for transaction in transactions:
        assert set(transaction) == {"date", "description", "category", "amount"}


def test_get_recent_transactions_respects_limit(temp_db):
    assert len(get_recent_transactions(temp_db["with_expenses"], limit=2)) == 2


def test_get_recent_transactions_without_expenses(temp_db):
    assert get_recent_transactions(temp_db["without_expenses"]) == []


# ------------------------------------------------------------------ #
# get_category_breakdown                                              #
# ------------------------------------------------------------------ #


def test_get_category_breakdown_ordered_and_sums_to_100(temp_db):
    breakdown = get_category_breakdown(temp_db["with_expenses"])

    assert len(breakdown) == 3
    amounts = [item["amount"] for item in breakdown]
    assert amounts == sorted(amounts, reverse=True)
    assert all(isinstance(item["pct"], int) for item in breakdown)
    assert sum(item["pct"] for item in breakdown) == 100
    # 100/300 rounds to 33 three times, leaving 1 for the largest to absorb.
    assert breakdown[0]["pct"] == 34


def test_get_category_breakdown_without_expenses(temp_db):
    assert get_category_breakdown(temp_db["without_expenses"]) == []


# ------------------------------------------------------------------ #
# GET /profile                                                        #
# ------------------------------------------------------------------ #


def test_profile_unauthenticated_redirects_to_login(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated_shows_seed_user_data(client, seed_user_id):
    client.post("/login", data={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    response = client.get("/profile")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert SEED_NAME in html
    assert SEED_EMAIL in html
    assert "₹" in html
    assert "£" not in html and "$" not in html

    stats = get_summary_stats(seed_user_id)
    assert stats["total_spent"] == pytest.approx(SEED_TOTAL)
    assert stats["transaction_count"] == SEED_COUNT
    assert stats["top_category"] == SEED_TOP_CATEGORY
    assert f"{SEED_TOTAL:.2f}" in html
    assert SEED_TOP_CATEGORY in html


def test_profile_transaction_list_is_newest_first(client, seed_user_id):
    client.post("/login", data={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    html = client.get("/profile").get_data(as_text=True)

    dates = [t["date"] for t in get_recent_transactions(seed_user_id)]
    assert dates == sorted(dates, reverse=True)
    positions = [html.index(date) for date in dict.fromkeys(dates)]
    assert positions == sorted(positions)


def test_profile_category_breakdown_covers_every_category(client, seed_user_id):
    client.post("/login", data={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    html = client.get("/profile").get_data(as_text=True)

    breakdown = get_category_breakdown(seed_user_id)
    assert len(breakdown) == SEED_CATEGORY_COUNT
    assert sum(item["pct"] for item in breakdown) == 100
    for item in breakdown:
        assert item["name"] in html


def test_profile_for_user_without_expenses(client):
    email = "no-expenses@example.com"
    conn = get_db()
    try:
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
        user_id = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("No Expenses", email, "hash"),
        ).lastrowid
        conn.commit()
    finally:
        conn.close()

    try:
        with client.session_transaction() as flask_session:
            flask_session["user_id"] = user_id

        response = client.get("/profile")
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "₹0.00" in html
        assert "spending-chart" not in html
        assert "No expenses logged yet." in html
    finally:
        conn = get_db()
        try:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()
