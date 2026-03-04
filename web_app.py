from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from companies import (
    COMPANIES, load_state, save_state,
    buy_shares, sell_shares, get_price
)

STARTING_CASH = 1_000_000

app = Flask(__name__)
app.secret_key = "vc-fantasy-secret-key-2024"


# ── Helpers ───────────────────────────────────────────────────────────────────

def portfolio_value(state, vc_name):
    vc = state["vcs"][vc_name]
    holdings_val = sum(
        shares * get_price(state, company)
        for company, shares in vc["portfolio"].items()
        if shares > 0
    )
    return round(vc["cash"] + holdings_val, 2)


def require_login():
    if "vc_name" not in session:
        return redirect(url_for("login"))
    return None


def prices_active(state):
    return len(state["vcs"]) >= 100


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "vc_name" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "vc_name" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not username:
            flash("Username is required.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        state = load_state()

        if username in state["vcs"]:
            flash("That username is already taken.", "danger")
            return redirect(url_for("register"))

        state["vcs"][username] = {
            "cash": STARTING_CASH,
            "portfolio": {},
            "password_hash": generate_password_hash(password, method="pbkdf2:sha256"),
        }
        save_state(state)
        session["vc_name"] = username
        flash(f"Welcome, {username}! You have ${STARTING_CASH:,.2f} to invest.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "vc_name" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter username and password.", "warning")
            return redirect(url_for("login"))

        state = load_state()

        if username not in state["vcs"]:
            flash("Username not found. Please register first.", "danger")
            return redirect(url_for("login"))

        vc = state["vcs"][username]

        # Legacy accounts without a password_hash (created before auth update)
        if "password_hash" not in vc:
            flash("Account requires re-registration. Please create a new account.", "warning")
            return redirect(url_for("register"))

        if not check_password_hash(vc["password_hash"], password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("login"))

        session["vc_name"] = username
        flash(f"Welcome back, {username}!", "info")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("vc_name", None)
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    redir = require_login()
    if redir:
        return redir

    vc_name = session["vc_name"]
    state = load_state()
    vc = state["vcs"][vc_name]

    holdings = []
    holdings_value = 0.0
    for company, shares in vc["portfolio"].items():
        if shares > 0:
            price = get_price(state, company)
            value = round(shares * price, 2)
            holdings_value += value
            sector = next((c["sector"] for c in COMPANIES if c["name"] == company), "")
            holdings.append({
                "company": company,
                "sector": sector,
                "shares": shares,
                "price": price,
                "value": value,
            })

    holdings_value = round(holdings_value, 2)
    total_value = round(vc["cash"] + holdings_value, 2)
    gain = round(total_value - STARTING_CASH, 2)

    # Add allocation % to each holding
    for h in holdings:
        h["allocation"] = round(h["value"] / total_value * 100, 1) if total_value > 0 else 0

    return render_template(
        "dashboard.html",
        vc_name=vc_name,
        cash=vc["cash"],
        holdings=holdings,
        holdings_value=holdings_value,
        total_value=total_value,
        gain=gain,
        prices_locked=not prices_active(state),
    )


@app.route("/companies")
def companies():
    redir = require_login()
    if redir:
        return redir

    vc_name = session["vc_name"]
    state = load_state()
    vc = state["vcs"][vc_name]

    current_sector = request.args.get("sector", "").strip()
    search_q = request.args.get("q", "").strip().lower()
    sectors = sorted({c["sector"] for c in COMPANIES})

    filtered = COMPANIES
    if current_sector:
        filtered = [c for c in filtered if c["sector"] == current_sector]
    if search_q:
        filtered = [c for c in filtered if search_q in c["name"].lower()]

    company_list = [
        {
            "name": c["name"],
            "sector": c["sector"],
            "country": c["country"],
            "price": get_price(state, c["name"]),
        }
        for c in filtered
    ]

    return render_template(
        "companies.html",
        companies=company_list,
        sectors=sectors,
        current_sector=current_sector,
        search_q=request.args.get("q", ""),
        cash=vc["cash"],
        prices_locked=not prices_active(state),
        total_companies=len(COMPANIES),
    )


@app.route("/buy", methods=["GET", "POST"])
def buy():
    redir = require_login()
    if redir:
        return redir

    vc_name = session["vc_name"]
    state = load_state()
    vc = state["vcs"][vc_name]

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        amount_str = request.form.get("amount", "").strip()

        valid_names = [c["name"] for c in COMPANIES]
        if company_name not in valid_names:
            flash("Company not found.", "danger")
            return redirect(url_for("companies"))

        try:
            amount = float(amount_str)
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for("companies"))

        if amount <= 0:
            flash("Amount must be greater than 0.", "danger")
            return redirect(url_for("companies"))

        if amount > vc["cash"]:
            flash(f"Not enough cash. You have ${vc['cash']:,.2f}.", "danger")
            return redirect(url_for("companies"))

        move_price = prices_active(state)
        shares = buy_shares(state, company_name, amount, move_price=move_price)
        vc["cash"] = round(vc["cash"] - amount, 2)

        if company_name not in vc["portfolio"]:
            vc["portfolio"][company_name] = 0
        vc["portfolio"][company_name] = round(vc["portfolio"][company_name] + shares, 4)

        save_state(state)
        new_price = get_price(state, company_name)
        flash(
            f"Bought {shares:.4f} shares of {company_name} for ${amount:,.2f}. "
            f"New price: ${new_price:.2f}",
            "success"
        )
        return redirect(url_for("dashboard"))

    company_list = [
        {"name": c["name"], "price": get_price(state, c["name"])}
        for c in COMPANIES
    ]
    selected_company = request.args.get("company", "")
    return render_template(
        "buy.html",
        companies=company_list,
        cash=vc["cash"],
        selected_company=selected_company,
    )


@app.route("/sell", methods=["GET", "POST"])
def sell():
    redir = require_login()
    if redir:
        return redir

    vc_name = session["vc_name"]
    state = load_state()
    vc = state["vcs"][vc_name]

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        shares_str = request.form.get("shares_to_sell", "").strip()

        holdings = {c: s for c, s in vc["portfolio"].items() if s > 0}
        if company_name not in holdings:
            flash("You don't own shares in that company.", "danger")
            return redirect(url_for("sell"))

        try:
            shares_to_sell = float(shares_str)
        except ValueError:
            flash("Invalid number of shares.", "danger")
            return redirect(url_for("sell"))

        owned = holdings[company_name]
        if shares_to_sell <= 0 or shares_to_sell > owned:
            flash(f"Invalid amount. You own {owned:.4f} shares.", "danger")
            return redirect(url_for("sell"))

        move_price = prices_active(state)
        cash_received = sell_shares(state, company_name, shares_to_sell, move_price=move_price)
        vc["portfolio"][company_name] = round(owned - shares_to_sell, 4)
        vc["cash"] = round(vc["cash"] + cash_received, 2)

        save_state(state)
        new_price = get_price(state, company_name)
        flash(
            f"Sold {shares_to_sell:.4f} shares of {company_name} for ${cash_received:,.2f}. "
            f"New price: ${new_price:.2f}",
            "success"
        )
        return redirect(url_for("dashboard"))

    selected_company = request.args.get("company", "")
    holdings_list = []
    for company, shares in vc["portfolio"].items():
        if shares > 0:
            price = get_price(state, company)
            holdings_list.append({
                "company": company,
                "shares": shares,
                "price": price,
                "value": round(shares * price, 2),
            })

    return render_template(
        "sell.html",
        holdings=holdings_list,
        cash=vc["cash"],
        selected_company=selected_company,
    )


@app.route("/leaderboard")
def leaderboard():
    redir = require_login()
    if redir:
        return redir

    state = load_state()
    current_vc = session["vc_name"]

    rankings = []
    for name, vc in state["vcs"].items():
        holdings_val = sum(
            shares * get_price(state, company)
            for company, shares in vc["portfolio"].items()
            if shares > 0
        )
        total = round(vc["cash"] + holdings_val, 2)
        rankings.append({
            "name": name,
            "cash": vc["cash"],
            "holdings_value": round(holdings_val, 2),
            "total_value": total,
            "gain": round(total - STARTING_CASH, 2),
        })

    rankings.sort(key=lambda x: x["total_value"], reverse=True)

    return render_template(
        "leaderboard.html",
        rankings=rankings,
        current_vc=current_vc,
        starting_cash=STARTING_CASH,
    )


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
