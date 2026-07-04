import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("journal/trades.json")
LOG_FILE.parent.mkdir(exist_ok=True)

def _load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def _save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2, default=str)

def log_entry(symbol: str, entry_price: float, qty: int, score: int, reasons: list):
    """Log a new trade entry."""
    log = _load_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "ENTRY",
        "symbol": symbol,
        "entry_price": entry_price,
        "qty": qty,
        "score": score,
        "reasons": reasons
    })
    _save_log(log)
    print(f"[JOURNAL] Entry logged: {symbol}")

def log_exit(symbol: str, exit_price: float, reason: str):
    """Log a trade exit."""
    log = _load_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "EXIT",
        "symbol": symbol,
        "exit_price": exit_price,
        "exit_reason": reason
    })
    _save_log(log)
    print(f"[JOURNAL] Exit logged: {symbol} ({reason})")