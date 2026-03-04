# VC Fantasy

A multiplayer stock-market-style game where players invest a virtual $1,000,000 in real private tech companies from top VC portfolios.

## How it works

- Register an account and receive **$1,000,000** in virtual cash
- Browse **360 companies** across 17 sectors (Gen AI, Fintech, Cybersecurity, Robotics, Space, and more)
- Buy and sell shares to maximise your portfolio value
- Compete on the leaderboard against other investors
- **Prices are locked** until 100+ investors join — once the market is live, buy/sell pressure nudges prices up and down

## Sectors

Gen AI · AI Infra · AI Applications · Fintech · Cybersecurity · Dev Tools · Productivity · Healthcare AI · Robotics · Space · Climate Tech · E-Commerce · Gaming · Design · Autonomous Vehicles · Social · HR Tech

## Running locally

```bash
pip install flask werkzeug
python3 web_app.py
```

Then open [http://localhost:5000](http://localhost:5000), register, and start investing.

## Stack

- **Backend:** Python / Flask
- **Auth:** werkzeug PBKDF2-SHA256 password hashing
- **State:** JSON file (`game_state.json`)
- **Frontend:** Bootstrap 5 + custom CSS
