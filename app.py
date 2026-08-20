import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["DEFAULT_MONTHLY_BUDGET"] = 500.00

with app.app_context():
    init_db()
    seed_db()


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


@app.context_processor
def inject_current_user():
    return {"current_user": get_current_user()}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("register.html", form_data={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    form_data = {"name": name, "email": email}

    if not name:
        error = "Full name is required"
    elif not email:
        error = "Email address is required"
    elif not password:
        error = "Password is required"
    elif len(password) < 8:
        error = "Password must be at least 8 characters long"
    else:
        error = None

    if error:
        return render_template("register.html", error=error, form_data=form_data)

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            return render_template(
                "register.html",
                error="An account with this email already exists",
                form_data=form_data,
            )

        password_hash = generate_password_hash(password)
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="An account with this email already exists",
                form_data=form_data,
            )
    finally:
        conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email:
        error = "Email is required"
    elif not password:
        error = "Password is required"
    else:
        error = None

    if error:
        return render_template("login.html", error=error)

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password")

    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")


@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_and_conditions.html")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    stats = get_summary_stats(user_id)

    return render_template(
        "profile.html",
        user=user,
        budget=app.config["DEFAULT_MONTHLY_BUDGET"],
        total_spent=stats["total_spent"],
        expense_count=stats["transaction_count"],
        top_category=stats["top_category"],
        recent_expenses=get_recent_transactions(user_id),
        category_breakdown=get_category_breakdown(user_id),
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
