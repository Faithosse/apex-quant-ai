from execution import broker
from config import settings

class RiskManager:
    def __init__(self):
        self.positions = {}  # symbol -> position info
        self.daily_pnl = 0.0
        self.trades_today = 0
    
    def can_open_position(self, symbol: str) -> bool:
        """Check if we're allowed to open a new trade."""
        # Max positions limit
        if len(self.positions) >= settings.MAX_POSITIONS:
            print(f"[RISK] Max positions ({settings.MAX_POSITIONS}) reached")
            return False
        
        # No duplicate symbols
        if symbol in self.positions:
            print(f"[RISK] Already holding {symbol}")
            return False
        
        # Daily loss limit
        if self.daily_pnl <= -settings.MAX_DAILY_LOSS:
            print(f"[RISK] Daily loss limit hit ({self.daily_pnl:.2f})")
            return False
        
        return True
    
    def register_position(self, symbol: str, entry_price: float, qty: int, order_id: str):
        """Track an opened position."""
        self.positions[symbol] = {
            "entry_price": entry_price,
            "qty": qty,
            "order_id": order_id,
            "stop_loss": entry_price * (1 - settings.STOP_LOSS_PCT),
            "take_profit": entry_price * (1 + settings.TAKE_PROFIT_PCT)
        }
        self.trades_today += 1
        print(f"[RISK] Position registered: {symbol} @ {entry_price:.2f}")
    
    def check_exits(self, symbol: str, current_price: float) -> str:
        """
        Check if position should be exited.
        Returns: 'STOP_LOSS', 'TAKE_PROFIT', or 'HOLD'
        """
        if symbol not in self.positions:
            return "HOLD"
        
        pos = self.positions[symbol]
        
        if current_price <= pos["stop_loss"]:
            return "STOP_LOSS"
        elif current_price >= pos["take_profit"]:
            return "TAKE_PROFIT"
        
        return "HOLD"
    
    def close_position(self, symbol: str, exit_price: float):
        """Remove position and update P&L."""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        pnl = (exit_price - pos["entry_price"]) * pos["qty"]
        self.daily_pnl += pnl
        del self.positions[symbol]
        print(f"[RISK] Position closed: {symbol} | P&L: ${pnl:.2f} | Daily: ${self.daily_pnl:.2f}")

# Global instance
risk_mgr = RiskManager()