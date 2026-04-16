#!/usr/bin/env python3
"""
fetch_data.py — Download BTC, S&P 500, and Gold price history → data/prices.js

Sources (all free, no API key required):
  BTC      — Binance klines API  (data from 2017-08-17 onward)
  S&P 500  — yfinance  ^GSPC     (data from 2014 onward)
  Gold     — yfinance  GC=F      (data from 2014 onward)

Requirements:
  pip install yfinance            (one-time install)

Usage:
  python3 fetch_data.py           # Skip if today's data already saved
  python3 fetch_data.py --force   # Re-download everything

Run once to initialise, then re-run whenever you want fresh data.
The browser page loads data/prices.js instantly and only calls Kraken
for a quick top-up of the most recent BTC candles.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    import yfinance as yf
    import warnings
    warnings.filterwarnings('ignore')
except ImportError:
    print('ERROR: yfinance is not installed.')
    print('Run:  pip install yfinance')
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
START_DATE   = '2014-01-01'
BINANCE_FROM = datetime(2017, 8, 17, tzinfo=timezone.utc)   # Binance launch date
OUTPUT_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, 'prices.js')


def log(msg='', end='\n'):
    print(msg, end=end, flush=True)


# ── BTC — Binance klines ──────────────────────────────────────────────────────
def fetch_btc():
    """
    Fetch BTC/USDT daily closing prices from Binance klines (free, no key).
    Returns {YYYY-MM-DD: close_price}.  Data available from 2017-08-17.
    """
    log('Fetching BTC from Binance...')

    def get_url(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    prices   = {}
    start_ms = int(BINANCE_FROM.timestamp() * 1000)
    now_ms   = int(time.time() * 1000)
    page     = 1

    while start_ms < now_ms:
        url = (
            'https://api.binance.com/api/v3/klines'
            f'?symbol=BTCUSDT&interval=1d&startTime={start_ms}&limit=1000'
        )
        log(f'  page {page}... ', end='')
        klines = get_url(url)
        if not klines:
            break

        for k in klines:
            dt = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
            prices[dt] = round(float(k[4]), 2)   # k[4] = close price

        log(f'{len(klines)} candles  ({len(prices)} total)')

        if len(klines) < 1000:
            break                       # Last (partial) batch — we're done
        start_ms = klines[-1][6] + 1    # close_time of last candle + 1 ms
        page += 1
        time.sleep(0.08)

    log(f'  => {len(prices)} days  (from {min(prices)})\n')
    return prices


# ── S&P 500 + Gold — yfinance ─────────────────────────────────────────────────
def fetch_yf(symbol, label):
    """
    Fetch daily closing prices via yfinance (Yahoo Finance wrapper).
    Returns {YYYY-MM-DD: close_price}.
    """
    log(f'Fetching {label} ({symbol}) via yfinance... ', end='')
    today  = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    df     = yf.download(symbol, start=START_DATE, end=today, progress=False, auto_adjust=True)

    if df.empty:
        raise RuntimeError(f'yfinance returned no data for {symbol}')

    # Flatten multi-level columns if present
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)

    prices = {}
    for dt, row in df['Close'].items():
        if row == row:    # skip NaN
            prices[dt.strftime('%Y-%m-%d')] = round(float(row), 2)

    log(f'{len(prices)} days  (from {min(prices)})')
    return prices


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    force = '--force' in sys.argv
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # Skip if already up to date today
    if not force and os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            head = f.read(120)
        if f'"updated":"{today}"' in head:
            log(f'Already up to date ({today}). Use --force to re-download.')
            return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log('=' * 52)
    log('  DCA Bitcoin — Data Fetcher')
    log(f'  Date  : {today}')
    log(f'  BTC   : 2017-08-17 → today  (Binance)')
    log(f'  S&P   : 2014-01-01 → today  (Yahoo Finance)')
    log(f'  Gold  : 2014-01-01 → today  (Yahoo Finance)')
    log('=' * 52)
    log()

    btc   = fetch_btc()
    sp500 = fetch_yf('^GSPC', 'S&P 500')
    gold  = fetch_yf('GC=F',  'Gold')

    payload = {
        'updated': today,
        'btc':     btc,
        'sp500':   sp500,
        'gold':    gold,
    }

    js = 'window.LOCAL_PRICES=' + json.dumps(payload, separators=(',', ':')) + ';'

    with open(OUTPUT_FILE, 'w') as f:
        f.write(js)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024

    log()
    log('=' * 52)
    log(f'  Saved : {OUTPUT_FILE}')
    log(f'  Size  : {size_kb:.0f} KB')
    log(f'  BTC   : {len(btc):,} days')
    log(f'  S&P   : {len(sp500):,} days')
    log(f'  Gold  : {len(gold):,} days')
    log('=' * 52)
    log()
    log('Done. Open index.html in your browser.')


if __name__ == '__main__':
    main()
