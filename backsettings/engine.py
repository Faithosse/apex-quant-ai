import pandas as pd
from datetime import datetime
from pathlib import Path
import json

from data.data_loader import fetch_bars, add_indicators
from strategies.scalper import calculate_score
from config import settings

class BacktestEngine:
    """
    Walk-forward backtester.
    Simulates trades on historical data using the same scoring logic as live engine.
    """
    
    def __init__(self, symbol: str, initial_cash: float = 10000.0):
        self.symbol = symbol
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.position = None
        self.trades = []
        self.equity_curve = []
        
    def run(self, df: pd.DataFrame) -> dict:
        """Walk through each bar, generate signals, simulate entries/exits."""
        if df.empty or len(df) < 50:
            return {"error": "Insufficient data for backtest"}
        
        df = add_indicators(df)
        
        for i in range(30, len(df)):
            current_bar = df.iloc[i]
            window = df.iloc[:i+1]
            
            signal_data = calculate_score(window)
            score = signal_data["score"]
            signal = signal_data["signal"]
            price = current_bar["close"]
            timestamp = current_bar.get("timestamp", i)
            
            equity = self._calculate_equity(price)
            self.equity_curve.append({
                "timestamp": timestamp,
                "price": price,
                "equity": equity,
                "cash": self.cash,
                "position": self.position is not None
            })
            
            if self.position:
                exit_reason = self._check_exit(price)
                if exit_reason:
                    self._close_position(price, timestamp, exit_reason)
                    continue
            
            if not self.position and score >= settings.SCORE_THRESHOLD and signal in ["BUY", "STRONG_BUY"]:
                self._open_position(price, timestamp, score, signal_data.get("reasons", []))
        
        if self.position:
            final_price = df.iloc[-1]["close"]
            final_time = df.iloc[-1].get("timestamp", len(df)-1)
            self._close_position(final_price, final_time, "END_OF_DATA")
        
        return self._generate_report()
    
    def _open_position(self, price: float, timestamp, score: int, reasons: list):
        qty = self._calculate_qty(price)
        if qty <= 0:
            return
        
        cost = qty * price
        self.cash -= cost
        
        self.position = {
            "entry_price": price,
            "qty": qty,
            "timestamp": timestamp,
            "score": score,
            "reasons": reasons,
            "stop_loss": price * (1 - settings.STOP_LOSS_PCT),
            "take_profit": price * (1 + settings.TAKE_PROFIT_PCT)
        }
        
        print(f"[BACKTEST] BUY  {self.symbol} | {qty:.6f} @ ${price:.2f} | Score: {score}")
    
    def _close_position(self, price: float, timestamp, reason: str):
        if not self.position:
            return
        
        qty = self.position["qty"]
        entry = self.position["entry_price"]
        pnl = (price - entry) * qty
        self.cash += qty * price
        
        trade = {
            "symbol": self.symbol,
            "entry_price": entry,
            "exit_price": price,
            "qty": qty,
            "pnl": pnl,
            "pnl_pct": (price - entry) / entry * 100,
            "entry_time": self.position["timestamp"],
            "exit_time": timestamp,
            "exit_reason": reason,
            "score_at_entry": self.position["score"],
            "holding_bars": self._count_holding_bars(self.position["timestamp"], timestamp)
        }
        self.trades.append(trade)
        
        emoji = "✅" if pnl > 0 else "❌"
        print(f"[BACKTEST] SELL {self.symbol} | {qty:.6f} @ ${price:.2f} | P&L: ${pnl:.2f} ({pnl/entry*100:.2f}%) {emoji} | {reason}")
        
        self.position = None
    
    def _check_exit(self, price: float) -> str:
        if not self.position:
            return None
        
        if price <= self.position["stop_loss"]:
            return "STOP_LOSS"
        elif price >= self.position["take_profit"]:
            return "TAKE_PROFIT"
        return None
    
    def _calculate_qty(self, price: float) -> float:
        risk_amount = self.cash * 0.05
        return risk_amount / price if price > 0 else 0
    
    def _calculate_equity(self, current_price: float) -> float:
        if not self.position:
            return self.cash
        return self.cash + (self.position["qty"] * current_price)
    
    def _count_holding_bars(self, entry, exit):
        try:
            return abs(exit - entry) if isinstance(exit, int) else 0
        except:
            return 0
    
    def _generate_report(self) -> dict:
        if not self.trades:
            return {"error": "No trades executed during backtest period"}
        
        pnls = [t["pnl"] for t in self.trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        total_return = (self.cash - self.initial_cash) / self.initial_cash * 100
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        
        report = {
            "symbol": self.symbol,
            "initial_cash": self.initial_cash,
            "final_cash": self.cash,
            "total_return_pct": round(total_return, 2),
            "total_trades": len(self.trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": round(win_rate, 2),
            "avg_win": round(sum(wins)/len(wins), 2) if wins else 0,
            "avg_loss": round(sum(losses)/len(losses), 2) if losses else 0,
            "max_drawdown_pct": self._max_drawdown(),
            "profit_factor": self._profit_factor(wins, losses),
            "trades": self.trades,
            "equity_curve": self.equity_curve
        }
        
        return report
    
    def _max_drawdown(self) -> float:
        if not self.equity_curve:
            return 0.0
        
        peak = self.equity_curve[0]["equity"]
        max_dd = 0.0
        
        for point in self.equity_curve:
            equity = point["equity"]
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return round(max_dd, 2)
    
    def _profit_factor(self, wins: list, losses: list) -> float:
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1
        return round(gross_profit / gross_loss, 2)


def run_backtest(symbol: str, days: int = 30, save_report: bool = True) -> dict:
    """Fetch historical data and run backtest."""
    print(f"\n{'='*60}")
    print(f"  BACKTEST: {symbol} | Last {days} days")
    print(f"{'='*60}")
    
    limit = min(days * 1440, 10000)
    df = fetch_bars(symbol, limit=limit)
    
    if df.empty:
        print(f"[ERROR] No data returned for {symbol}")
        return {"error": "No data"}
    
    print(f"[DATA] Loaded {len(df)} bars for {symbol}")
    
    engine = BacktestEngine(symbol)
    report = engine.run(df)
    
    print(f"\n{'='*60}")
    print(f"  BACKTEST RESULTS: {symbol}")
    print(f"{'='*60}")
    print(f"  Total Return:     {report.get('total_return_pct', 0):+.2f}%")
    print(f"  Total Trades:     {report.get('total_trades', 0)}")
    print(f"  Win Rate:         {report.get('win_rate_pct', 0):.1f}%")
    print(f"  Profit Factor:    {report.get('profit_factor', 0):.2f}")
    print(f"  Max Drawdown:     {report.get('max_drawdown_pct', 0):.2f}%")
    print(f"  Avg Win:          ${report.get('avg_win', 0):.2f}")
    print(f"  Avg Loss:         ${report.get('avg_loss', 0):.2f}")
    print(f"{'='*60}")
    
    if save_report:
        Path("backtesting/reports").mkdir(parents=True, exist_ok=True)
        filename = f"backtesting/reports/{symbol.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"[SAVED] Report: {filename}")
    
    return report