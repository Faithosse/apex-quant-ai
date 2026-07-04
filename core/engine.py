import time
from datetime import datetime
from config import settings
from strategies import scalper
from ai import filter as ai_filter
from risk import risk_manager
from execution import broker
from journal import trade_logger

def run_once():
    print(f"\n{'='*50}")
    print(f"[ENGINE] Scan cycle @ {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    # 1. Check existing positions for exits
    try:
        positions = broker.get_positions()
        for pos in positions:
            symbol = pos.symbol
            current_price = float(pos.current_price)
            
            exit_signal = risk_manager.risk_mgr.check_exits(symbol, current_price)
            
            if exit_signal == "STOP_LOSS":
                print(f"[EXIT] Stop loss triggered for {symbol}")
                broker.sell(symbol, float(pos.qty))
                risk_manager.risk_mgr.close_position(symbol, current_price)
                trade_logger.log_exit(symbol, current_price, "STOP_LOSS")
                
            elif exit_signal == "TAKE_PROFIT":
                print(f"[EXIT] Take profit triggered for {symbol}")
                broker.sell(symbol, float(pos.qty))
                risk_manager.risk_mgr.close_position(symbol, current_price)
                trade_logger.log_exit(symbol, current_price, "TAKE_PROFIT")
    except Exception as e:
        print(f"[POSITION CHECK ERROR] {e}")
    
    # 2. Scan for new entries — PER SYMBOL with individual error handling
    for symbol in settings.SYMBOLS:
        try:
            # Skip if already in position
            if symbol in risk_manager.risk_mgr.positions:
                print(f"[SKIP] Already holding {symbol}")
                continue
            
            # Skip if risk manager says no
            if not risk_manager.risk_mgr.can_open_position(symbol):
                continue
            
            # Analyze
            analysis = scalper.analyze_symbol(symbol)
            score = analysis.get("score", 0)
            signal = analysis.get("signal", "NO_DATA")
            price = analysis.get("price", 0)
            
            print(f"[SCAN] {symbol:10} | Score: {score:2d}/100 | Signal: {signal:12} | Price: ${price:,.2f}")
            
            # AI Filter gate
            if not ai_filter.ai_approve(analysis):
                continue
            
            # EXECUTE PAPER TRADE
            print(f"[EXECUTE] >>> ENTERING {symbol} <<<")
            result = broker.buy(symbol, settings.QTY_PER_TRADE)
            
            if result.get("success"):
                risk_manager.risk_mgr.register_position(
                    symbol=symbol,
                    entry_price=price,
                    qty=settings.QTY_PER_TRADE,
                    order_id=result["order_id"]
                )
                trade_logger.log_entry(
                    symbol=symbol,
                    entry_price=price,
                    qty=settings.QTY_PER_TRADE,
                    score=score,
                    reasons=analysis.get("reasons", [])
                )
            else:
                print(f"[ERROR] Order failed: {result.get('error')}")
                
        except Exception as e:
            print(f"[SCAN ERROR] {symbol}: {e}")
            import traceback
            traceback.print_exc()

def run():
    print("="*60)
    print("  APEX AI v1 — STRATEGY ENGINE ACTIVE")
    print("  Mode: PAPER TRADING")
    print("  Symbols: " + ", ".join(settings.SYMBOLS))
    print("  Interval: 60 seconds")
    print("="*60)
    
    try:
        account = broker.get_account()
        print(f"[OK] Broker connected. Equity: ${account.equity}")
    except Exception as e:
        print(f"[FATAL] Broker connection failed: {e}")
        return
    
    while True:
        run_once()
        print(f"[SLEEP] Waiting 60s until next cycle...")
        time.sleep(60)