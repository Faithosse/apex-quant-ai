import os
from dotenv import load_dotenv

load_dotenv()

# Broker credentials
APCA_API_KEY = os.getenv("APCA_API_KEY")
APCA_API_SECRET = os.getenv("APCA_API_SECRET")
APCA_PAPER = os.getenv("APCA_PAPER", "true").lower() == "true"

# Trading parameters
SYMBOLS = ["BTC/USD", "ETH/USD", "AAPL", "TSLA"]  # Adjust to your preference
TIMEFRAME = "1Min"  # Alpaca crypto supports 1Min, 5Min, 15Min, 1Hour, 1Day
SCORE_THRESHOLD = 35  # Minimum score to trigger a trade
MAX_POSITIONS = 3  # Max concurrent positions
QTY_PER_TRADE = 1  # Default quantity (can be dynamic later)

# Risk limits
MAX_DAILY_LOSS = 100.0  # USD
STOP_LOSS_PCT = 0.02  # 2% stop loss
TAKE_PROFIT_PCT = 0.04  # 4% take profit