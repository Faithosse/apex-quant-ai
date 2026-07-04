import os
from dotenv import load_dotenv
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import pandas_ta as ta

load_dotenv()

crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(
    os.getenv("APCA_API_KEY"),
    os.getenv("APCA_API_SECRET")
)

def fetch_bars(symbol: str, limit: int = 50):
    """Fetch recent OHLCV bars. Returns DataFrame."""
    try:
        if "/" in symbol:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                limit=limit
            )
            bars = crypto_client.get_crypto_bars(request)
        else:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                limit=limit
            )
            bars = stock_client.get_stock_bars(request)
        
        df = bars.df.reset_index()
        
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol].copy()
        
        if 'timestamp' not in df.columns:
            for col in ['timestamp', 'date', 'time']:
                if col in df.columns:
                    df = df.rename(columns={col: 'timestamp'})
                    break
        
        df.columns = [c.lower() for c in df.columns]
        
        return df
    
    except Exception as e:
        print(f"[DATA ERROR] {symbol}: {e}")
        return pd.DataFrame()

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators using pandas-ta."""
    if df.empty or len(df) < 30:
        return df
    
    required = ['open', 'high', 'low', 'close', 'volume']
    for col in required:
        if col not in df.columns:
            print(f"[INDICATOR ERROR] Missing column: {col}")
            return df
    
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=21, append=True)
    df.ta.macd(append=True)
    df.ta.atr(length=14, append=True)
    df.ta.bbands(length=20, append=True)
    
    return df