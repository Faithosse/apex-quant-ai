from config import settings

def ai_approve(signal_data: dict) -> bool:
    """Final gate before execution."""
    score = signal_data.get("score", 0)
    signal = signal_data.get("signal", "HOLD")
    
    # Hard threshold
    if score < settings.SCORE_THRESHOLD:
        print(f"[AI FILTER] Score {score} below threshold {settings.SCORE_THRESHOLD}")
        return False
    
    # Only allow BUY signals in v1
    if signal not in ["BUY", "STRONG_BUY"]:
        print(f"[AI FILTER] Signal {signal} not actionable")
        return False
    
    # Volatility check using correct key from indicators
    indicators = signal_data.get("indicators", {})
    atr = indicators.get("atr", 0)  # <-- FIXED: matches key set in scalper.py
    price = signal_data.get("price", 1)
    
    if price > 0 and atr > 0:
        atr_pct = atr / price
        if atr_pct > 0.05:  # ATR > 5% of price = too volatile
            print(f"[AI FILTER] ATR too high ({atr:.2f} / {price:.2f} = {atr_pct:.2%})")
            return False
    
    print(f"[AI APPROVED] {signal_data.get('symbol', 'UNKNOWN')} | Score: {score} | Signal: {signal}")
    return True