from companies import (
    COMPANIES, load_state, save_state,
    buy_shares, sell_shares, get_price, show_all, search_by_sector
)

STARTING_CASH = 100.0


# ── Helpers ───────────────────────────────────────────────────────────────────

def portfolio_value(state, vc_name):
    """Total value of a VC's cash + all holdings at current prices."""
    vc = state["vcs"][vc_name]
    holdings_value = sum(
        shares * get_price(state, company)
        for company, shares in vc["portfolio"].items()
        if shares > 0
    )
    return round(vc["cash"] + holdings_value, 2)


# ── Login ─────────────────────────────────────────────────────────────────────

def login(state):
    print("\n" + "="*40)
    print("   VC Fantasy — Login")
    print("="*40)
    name = input("Enter your VC name: ").strip()

    if name not in state["vcs"]:
        state["vcs"][name] = {
            "cash": STARTING_CASH,
            "portfolio": {}
        }
        print(f"\nWelcome, {name}! You've been given ${STARTING_CASH} to invest.")
    else:
        print(f"\nWelcome back, {name}!")

    return name


# ── Buy ───────────────────────────────────────────────────────────────────────

def do_buy(state, vc_name):
    show_all(state)
    company_name = input("\nEnter company name to buy (or press Enter to cancel): ").strip()

    if company_name == "":
        return

    # Check company exists
    names = [c["name"] for c in COMPANIES]
    if company_name not in names:
        print("Company not found. Check the spelling.")
        return

    vc = state["vcs"][vc_name]
    print(f"\nYour cash: ${vc['cash']}")
    print(f"Current price of {company_name}: ${get_price(state, company_name)}")

    try:
        amount = float(input("How much do you want to invest ($)? "))
    except ValueError:
        print("Invalid amount.")
        return

    if amount <= 0:
        print("Amount must be greater than 0.")
        return

    if amount > vc["cash"]:
        print(f"Not enough cash. You only have ${vc['cash']}.")
        return

    shares = buy_shares(state, company_name, amount)
    vc["cash"] = round(vc["cash"] - amount, 2)

    # Add to portfolio
    if company_name not in vc["portfolio"]:
        vc["portfolio"][company_name] = 0
    vc["portfolio"][company_name] = round(vc["portfolio"][company_name] + shares, 4)

    save_state(state)
    print(f"\nBought {round(shares, 4)} shares of {company_name} for ${amount}")
    print(f"New price: ${get_price(state, company_name)}")
    print(f"Cash remaining: ${vc['cash']}")


# ── Sell ──────────────────────────────────────────────────────────────────────

def do_sell(state, vc_name):
    vc = state["vcs"][vc_name]
    holdings = {c: s for c, s in vc["portfolio"].items() if s > 0}

    if not holdings:
        print("You don't own any shares yet.")
        return

    print("\nYour holdings:")
    for company, shares in holdings.items():
        price = get_price(state, company)
        value = round(shares * price, 2)
        print(f"  {company:<25} {round(shares, 4)} shares  (value: ${value})")

    company_name = input("\nEnter company name to sell (or press Enter to cancel): ").strip()

    if company_name == "" or company_name not in holdings:
        print("Invalid company.")
        return

    owned = holdings[company_name]
    print(f"You own {round(owned, 4)} shares of {company_name}")

    try:
        shares_to_sell = float(input("How many shares to sell? "))
    except ValueError:
        print("Invalid number.")
        return

    if shares_to_sell <= 0 or shares_to_sell > owned:
        print("Invalid amount.")
        return

    cash_received = sell_shares(state, company_name, shares_to_sell)
    vc["portfolio"][company_name] = round(owned - shares_to_sell, 4)
    vc["cash"] = round(vc["cash"] + cash_received, 2)

    save_state(state)
    print(f"\nSold {shares_to_sell} shares of {company_name} for ${round(cash_received, 2)}")
    print(f"New price: ${get_price(state, company_name)}")
    print(f"Cash balance: ${vc['cash']}")


# ── Portfolio ─────────────────────────────────────────────────────────────────

def show_portfolio(state, vc_name):
    vc = state["vcs"][vc_name]
    holdings = {c: s for c, s in vc["portfolio"].items() if s > 0}
    total = portfolio_value(state, vc_name)

    print(f"\n{'='*50}")
    print(f"  Portfolio: {vc_name}")
    print(f"{'='*50}")
    print(f"  Cash:             ${vc['cash']}")

    if holdings:
        print(f"\n  {'Company':<25} {'Shares':<10} {'Value'}")
        print(f"  {'-'*45}")
        for company, shares in holdings.items():
            price = get_price(state, company)
            value = round(shares * price, 2)
            print(f"  {company:<25} {round(shares,4):<10} ${value}")

    print(f"\n  Total Portfolio Value: ${total}")
    gain = round(total - STARTING_CASH, 2)
    sign = "+" if gain >= 0 else ""
    print(f"  vs Starting $100:      {sign}${gain}")
    print(f"{'='*50}")


# ── Leaderboard ───────────────────────────────────────────────────────────────

def show_leaderboard(state):
    if not state["vcs"]:
        print("No VCs have joined yet.")
        return

    rankings = [
        (name, portfolio_value(state, name))
        for name in state["vcs"]
    ]
    rankings.sort(key=lambda x: x[1], reverse=True)

    print(f"\n{'='*40}")
    print(f"  Leaderboard")
    print(f"{'='*40}")
    print(f"  {'#':<4} {'VC Name':<20} {'Total Value'}")
    print(f"  {'-'*36}")
    for i, (name, value) in enumerate(rankings):
        gain = round(value - STARTING_CASH, 2)
        sign = "+" if gain >= 0 else ""
        print(f"  {i+1:<4} {name:<20} ${value}  ({sign}${gain})")
    print(f"{'='*40}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    state = load_state()
    save_state(state)

    vc_name = login(state)
    save_state(state)

    while True:
        print(f"\n--- Main Menu ({vc_name}) ---")
        print("1. Browse companies")
        print("2. Search by sector")
        print("3. Buy shares")
        print("4. Sell shares")
        print("5. My portfolio")
        print("6. Leaderboard")
        print("7. Switch VC / Logout")
        print("8. Quit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            show_all(state)
        elif choice == "2":
            sector = input("Enter sector: ")
            search_by_sector(state, sector)
        elif choice == "3":
            do_buy(state, vc_name)
        elif choice == "4":
            do_sell(state, vc_name)
        elif choice == "5":
            show_portfolio(state, vc_name)
        elif choice == "6":
            show_leaderboard(state)
        elif choice == "7":
            vc_name = login(state)
            save_state(state)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
