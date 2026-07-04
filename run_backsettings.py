from backsettings.engine import run_backtest
from config import settings

if __name__ == "__main__":
    for symbol in settings.SYMBOLS:
        # Use 30 days to ensure enough bars across weekends
        result = run_backtest(symbol, days=30)
        total_return = result.get("total_return_pct", -100)
        win_rate = result.get("win_rate_pct", 0)
        profit_factor = result.get("profit_factor", 0)
        
        if total_return > 0 and win_rate > 50 and profit_factor > 1.2:
            print(f"\n✅ {symbol} PASSED — ready for live")
        else:
            print(f"\n❌ {symbol} FAILED — DO NOT trade live")