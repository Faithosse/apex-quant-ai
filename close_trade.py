import sys
from execution.broker import close_position, client

if __name__ == "__main__":
    # First, list all actual positions
    print("[CHECK] All open positions in Alpaca:")
    try:
        positions = client.get_all_positions()
        if not positions:
            print("  None")
        for pos in positions:
            print(f"  {pos.symbol}: {pos.qty} @ ${pos.current_price}")
    except Exception as e:
        print(f"  Error: {e}")
    
    if len(sys.argv) < 2:
        print("\nUsage: python close_trade.py <SYMBOL>")
        print("Example: python close_trade.py ETHUSD")
        sys.exit(1)
    
    symbol = sys.argv[1]
    print(f"\n[MANUAL CLOSE] Closing {symbol}...")
    result = close_position(symbol)
    
    if result.get("success"):
        print(f"[OK] Closed {symbol} | Order ID: {result['order_id']}")
    else:
        print(f"[FAIL] {result.get('error')}")