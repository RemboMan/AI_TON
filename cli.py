#!/usr/bin/env python3
"""
TON AI Trading Bot - Command Line Interface
"""
import asyncio
import sys
from wallet import TonWallet
from market_data import MarketData
from trade_logger import TradeLogger
import config

async def show_balance():
    """Show wallet balance"""
    wallet = TonWallet()
    await wallet.connect()
    balance = await wallet.get_balance()
    print(f"\n💰 Balance: {balance:.4f} TON")
    print(f"📍 Address: {wallet.wallet.address.to_str()}\n")
    await wallet.close()

async def show_markets():
    """Show market overview"""
    market = MarketData()
    await market.init_session()
    data = await market.get_market_overview()
    print(f"\n📊 Market Overview:")
    print(f"   DeDust: {data['dedust']['pools_count']} pools")
    print(f"   STON.fi: {data['stonfi']['pools_count']} pools\n")
    await market.close_session()

def show_trades():
    """Show trade history"""
    logger = TradeLogger()
    logger.print_history()

def show_help():
    """Show help menu"""
    print("""
🤖 TON AI Trading Bot - CLI

Commands:
  balance    - Show wallet balance
  markets    - Show market overview
  trades     - Show trade history
  run        - Start the trading bot
  help       - Show this help message

Usage:
  python cli.py <command>

Examples:
  python cli.py balance
  python cli.py trades
  python cli.py run
""")

async def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    try:
        if command == "balance":
            await show_balance()
        elif command == "markets":
            await show_markets()
        elif command == "trades":
            show_trades()
        elif command == "run":
            print("Starting bot...")
            from main import main as run_bot
            await run_bot()
        elif command == "help":
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
