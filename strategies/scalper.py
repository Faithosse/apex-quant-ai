import pandas as pd
from data.data_loader import fetch_bars, add_indicators

def calculate_score(df: pd.DataFrame) -> dict:
    """
    Multi-factor scoring system (0-100).
    Higher score = stronger BUY signal.
    """
    if df.empty or len(df) < 30:
        return {"score": 0, "signal": "NO_DATA", "reason": "Insufficient data", "price": 0, "indicators": {}}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    score = 0
    reasons = []
    
    # Use 'close' column, not 'price'
    close = latest.get('close', 0)
    
    # 1. RSI Momentum (0-25 points)
    rsi = latest.get('RSI_14', 50)
    if rsi < 30:
        score += 25
        reasons.append(f"RSI oversold ({rsi:.1f})")
    elif rsi < 45:
        score += 15
        reasons.append(f"RSI weak ({rsi:.1f})")
    elif rsi > 70:
        score -= 10
        reasons.append(f"RSI overbought ({rsi:.1f})")
    
    # 2. EMA Trend (0-25 points)
    ema9 = latest.get('EMA_9', 0)
    ema21 = latest.get('EMA_21', 0)
    if ema9 > ema21:
        score += 25
        reasons.append("EMA9 > EMA21 (bullish)")
    else:
        score += 10
        reasons.append("EMA9 < EMA21 (bearish)")
    
    # 3. MACD Momentum (0-25 points)
    macd = latest.get('MACD_12_26_9', 0)
    macd_signal = latest.get('MACDs_12_26_9', 0)
    if macd > macd_signal and macd > 0:
        score += 25
        reasons.append("MACD bullish crossover")
    elif macd > macd_signal:
        score += 15
        reasons.append("MACD crossing up")
    
    # 4. Bollinger Bands (0-15 points)
    bb_lower = latest.get('BBL_20_2.0', 0)
    bb_upper = latest.get('BBU_20_2.0', 0)
    if bb_lower > 0 and close < bb_lower * 1.02:
        score += 15
        reasons.append("Price near lower BBand")
    elif bb_upper > 0 and close > bb_upper * 0.98:
        score -= 5
        reasons.append("Price near upper BBand")
    
    # 5. Volume Confirmation (0-10 points)
    vol = latest.get('volume', 0)
    vol_avg = df['volume'].tail(10).mean() if 'volume' in df.columns else 0
    if vol_avg > 0 and vol > vol_avg * 1.5:
        score += 10
        reasons.append("Volume spike confirmed")
    
    # 6. ATR-based volatility check (0-10 points)
    atr = latest.get('ATRr_14', 0)  # pandas-ta default column name
    if atr > 0 and close > 0:
        atr_pct = atr / close
        if atr_pct < 0.02:  # Low volatility = good for scalping
            score += 10
            reasons.append("Low volatility (good)")
        elif atr_pct > 0.05:  # Too volatile
            score -= 5
            reasons.append("High volatility (caution)")
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Determine signal
    if score >= 40:
        signal = "BUY"
    elif score >= 80:
        signal = "STRONG_BUY"
    elif score <= 20:
        signal = "STRONG_SELL"
    elif score <= 35:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        "score": score,
        "signal": signal,
        "reasons": reasons,
        "price": close,  # <-- FIXED: use close, not missing 'price' column
        "indicators": {
            "rsi": rsi,
            "ema9": ema9,
            "ema21": ema21,
            "macd": macd,
            "macd_signal": macd_signal,
            "atr": atr  # <-- FIXED: include atr in indicators dict
        }
    }

def analyze_symbol(symbol: str) -> dict:
    """Full pipeline: fetch data → add indicators → calculate score."""
    df = fetch_bars(symbol)
    df = add_indicators(df)
    result = calculate_score(df)
    result["symbol"] = symbol
    return result