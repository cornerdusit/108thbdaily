# 108THBDAILY — BTC DCA Calculator

A DCA (Dollar-Cost Averaging) calculator built around the **108-1009 movement** — a practice popularised in the Thai Bitcoiner community where participants commit to buying **108 THB of Bitcoin every day**, starting now and never stopping.

**Live site → [cornerdusit.github.io/108thbdaily](https://cornerdusit.github.io/108thbdaily/)**

---

## What it does

Enter an amount, pick a frequency, choose how far back to start — the calculator shows exactly what your DCA position would look like today: total invested, current portfolio value, profit/loss, total return, BTC accumulated, and average buy price. An interactive chart plots your portfolio value over time.

**Compare mode** lets you run the same DCA strategy against S&P 500 or Gold side-by-side to see how Bitcoin stacks up.

---

## Features

| | |
|---|---|
| **Default amount** | 108 THB / day (the 108-1009 movement default) |
| **Frequencies** | Daily · Weekly · Monthly |
| **Starting period** | 1 – 10 years ago |
| **Compare** | BTC vs S&P 500 · BTC vs Gold (XAU/USD) |
| **Currency** | THB ⇄ USD toggle |
| **Chart modes** | Portfolio value (USD) · % Return |
| **Theme** | Dark / Light |
| **Language** | English / ไทย |

---

## Data sources

| Asset | Source | History |
|---|---|---|
| Bitcoin (BTC) | Binance klines API | 2017-08-17 → today |
| S&P 500 | Yahoo Finance (yfinance) | 2014-01-01 → today |
| Gold (XAU/USD) | Yahoo Finance (yfinance) | 2014-01-01 → today |

Price data is pre-fetched daily by a GitHub Actions workflow and committed as `data/prices.js`, so the page loads instantly without waiting for live API calls. A small top-up from Kraken fills in any days since the last file update.

---

## Running locally

```bash
# Open directly in a browser — no build step needed
open index.html
```

For S&P 500 / Gold live fallback, serve over HTTP to avoid CORS:

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

### Refreshing price data manually

```bash
pip install yfinance
python3 fetch_data.py          # skip if already up to date today
python3 fetch_data.py --force  # re-download everything
```

---

## How the 108-1009 movement works

The idea is simple: buy **108 THB of Bitcoin every single day**. No timing the market, no waiting for dips — just consistent, automated accumulation. The number 108 carries significance in Buddhist culture and is a nod to the Thai community that made it popular. The goal is to hold for the long term and let compounding do the work.

This calculator lets you look back and see what the strategy would have returned had you started 1, 3, 5, or up to 10 years ago.

---

## Project structure

```
108thbdaily/
├── index.html          # Single-file app (HTML + CSS + JS)
├── fetch_data.py       # Data fetcher (run locally or via CI)
├── data/
│   └── prices.js       # Pre-fetched price data (auto-updated daily)
├── logo-dark.svg
├── logo-light.svg
└── .github/
    └── workflows/
        └── update-prices.yml   # Daily GitHub Actions job
```
