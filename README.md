\# Apex Quant AI v1



Automated algorithmic trading bot for Alpaca paper trading.

Fetches market data, calculates technical indicators, scores signals,

and executes BUY/SELL orders with risk management.



\## What It Does



\- Connects to Alpaca broker (paper trading mode)

\- Fetches real-time price bars for crypto and stocks

\- Calculates RSI, EMA, MACD, Bollinger Bands, ATR

\- Scores each symbol 0-100 based on indicator alignment

\- AI filter gates trades below score threshold

\- Risk manager enforces position limits, stop loss, take profit

\- Logs all trades to JSON journal

\- Backtests strategy on historical data before going live



\## Project Structure



&#x20;   core/engine.py          Main trading loop, runs every 60 seconds

&#x20;   data/data\_loader.py       Fetches bars from Alpaca, adds indicators

&#x20;   strategies/scalper.py     Signal scoring engine (0-100)

&#x20;   ai/filter.py              Final approval gate before execution

&#x20;   risk/risk\_manager.py      Tracks positions, stop loss, take profit

&#x20;   execution/broker.py         Sends orders to Alpaca

&#x20;   journal/trade\_logger.py     Records entries and exits to JSON

&#x20;   backsetting/engine.py       Backtests strategy on historical data

&#x20;   config/settings.py          All tunable parameters



\## Setup



1\. Install dependencies



&#x20;   pip install -r requirements.txt



2\. Add your Alpaca API keys



&#x20;   copy .env.example .env



&#x20;   Then edit .env and paste your keys from:

&#x20;   https://app.alpaca.markets/paper/dashboard



3\. Test broker connection



&#x20;   python test\_connection.py



&#x20;   Should show: Account connected, equity $100000.00



\## Run Backtest First



&#x20;   python run\_backtest.py



Checks strategy on 30 days of historical data.

Only trade live if win rate \&gt; 50% and profit factor \&gt; 1.2.



\## Run Live Engine (Paper Trading)



&#x20;   python main.py



Loops every 60 seconds:

\- Scans all symbols

\- Calculates scores

\- Enters positions if AI approves

\- Monitors open positions for stop loss / take profit

\- Logs everything



\## Manual Commands



&#x20;   python test\_connection.py              Verify broker link

&#x20;   python run\_backtest.py                 Test strategy on history

&#x20;   python main.py                         Start live paper trading

&#x20;   python close\_trade.py ETHUSD           Close a position manually



\## Tunable Settings (config/settings.py)



&#x20;   SYMBOLS = \["BTC/USD", "ETH/USD", "AAPL", "TSLA"]

&#x20;   SCORE\_THRESHOLD = 75                   Min score to trade

&#x20;   MAX\_POSITIONS = 3                      Max open at once

&#x20;   STOP\_LOSS\_PCT = 0.02                   2% stop loss

&#x20;   TAKE\_PROFIT\_PCT = 0.04                 4% take profit

&#x20;   QTY\_PER\_TRADE = 1                      Shares/coins per order



\## Requirements



\- Python 3.10+

\- Alpaca paper trading account (free)

\- Windows / Mac / Linux

\---

.env.example

APCA\_API\_KEY=your\_alpaca\_key\_here

APCA\_API\_SECRET=your\_alpaca\_secret\_here

APCA\_PAPER=true

