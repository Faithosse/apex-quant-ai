import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.common.exceptions import APIError

load_dotenv()

client = TradingClient(
    os.getenv("APCA_API_KEY"),
    os.getenv("APCA_API_SECRET"),
    paper=os.getenv("APCA_PAPER", "true").lower() == "true"
)

def get_account():
    """Verify account connection."""
    return client.get_account()

def get_positions():
    """List current positions."""
    return client.get_all_positions()

def submit_market_order(symbol: str, qty: float, side: str) -> dict:
    """
    Execute a market order.
    side: 'buy' or 'sell'
    """
    try:
        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        
        # For crypto, Alpaca uses notional qty sometimes
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side_enum,
            time_in_force=TimeInForce.GTC
        )
        
        result = client.submit_order(order)
        print(f"[BROKER] {side.upper()} {qty} {symbol} @ MARKET | ID: {result.id}")
        return {
            "success": True,
            "order_id": str(result.id),
            "symbol": result.symbol,
            "qty": result.qty,
            "side": result.side.value,
            "status": result.status.value
        }
    
    except APIError as e:
        print(f"[BROKER ERROR] {e}")
        return {"success": False, "error": str(e)}

def buy(symbol: str, qty: float = 1.0):
    return submit_market_order(symbol, qty, "buy")

def sell(symbol: str, qty: float = 1.0):
    return submit_market_order(symbol, qty, "sell")

def close_position(symbol: str):
    """Market sell to close an open position."""
    try:
        # Get current position qty
        positions = client.get_all_positions()
        for pos in positions:
            if pos.symbol == symbol:
                qty = abs(float(pos.qty))
                return submit_market_order(symbol, qty, "sell")
        print(f"[BROKER] No open position found for {symbol}")
        return {"success": False, "error": "No position"}
    except Exception as e:
        print(f"[BROKER ERROR] {e}")
        return {"success": False, "error": str(e)}