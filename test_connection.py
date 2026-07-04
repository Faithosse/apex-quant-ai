from alpaca.trading.client import TradingClient
from config.settings import APCA_API_KEY, APCA_API_SECRET

client = TradingClient(
    APCA_API_KEY,
    APCA_API_SECRET,
    paper=True
)

account = client.get_account()

print("ACCOUNT STATUS:", account.status)
print("BUYING POWER:", account.buying_power)