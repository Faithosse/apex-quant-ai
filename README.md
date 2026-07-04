\# Apex Quant AI v1



Automated algorithmic trading bot for Alpaca paper trading. Fetches market data, calculates technical indicators, scores signals, and executes BUY/SELL orders with risk management.



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



| File | Purpose |

|------|---------|

| core/engine.py | Main trading loop, runs every 60 seconds |

| data/data\_loader.py | Fetches bars from Alpaca, adds indicators |

| strategies/scalper.py | Signal scoring engine (0-100) |

| ai/filter.py | Final approval gate before execution |

| risk/risk\_manager.py | Tracks positions, stop loss, take profit |

| execution/broker.py | Sends orders to Alpaca |

| journal/trade\_logger.py | Records entries and exits to JSON |

| backsetting/engine.py | Backtests strategy on historical data |

| config/settings.py | All tunable parameters |



\## Setup



1\. Install dependencies



&#x20;      pip install -r requirements.txt



2\. Add your Alpaca API keys



&#x20;      copy .env.example .env



&#x20;  Then edit .env and paste your keys from: https://app.alpaca.markets/paper/dashboard



3\. Test broker connection



&#x20;      python test\_connection.py



&#x20;  Should show: Account connected, equity $100000.00



\## Run Backtest First



&#x20;   python run\_backtest.py



Checks strategy on 30 days of historical data. Only trade live if win rate \&gt; 50% and profit factor \&gt; 1.2.



\## Run Live Engine (Paper Trading)



&#x20;   python main.py



Loops every 60 seconds:

\- Scans all symbols

\- Calculates scores

\- Enters positions if AI approves

\- Monitors open positions for stop loss / take profit

\- Logs everything



\## Manual Commands



| Command | Purpose |

|---------|---------|

| python test\_connection.py | Verify broker link |

| python run\_backtest.py | Test strategy on history |

| python main.py | Start live paper trading |

| python close\_trade.py ETHUSD | Close a position manually |



\## Tunable Settings (config/settings.py)



| Setting | Default | Description |

|---------|---------|-------------|

| SYMBOLS | BTC/USD, ETH/USD, AAPL, TSLA | Assets to trade |

| SCORE\_THRESHOLD | 75 | Min score to trade |

| MAX\_POSITIONS | 3 | Max open at once |

| STOP\_LOSS\_PCT | 0.02 | 2% stop loss |

| TAKE\_PROFIT\_PCT | 0.04 | 4% take profit |

| QTY\_PER\_TRADE | 1 | Shares/coins per order |



\## Requirements



\- Python 3.10+

\- Alpaca paper trading account (free)

\- Windows / Mac / Linux

