#!/usr/bin/env python3
"""
Test real trading functionality (simulation mode)
"""
import asyncio
from wallet import TonWallet
from dex_handler import DEXHandler
import config

async def test_trading():
    print("Testing Trading Functionality\n")
    print("="*60)

    # Check config
    print(f"API Base URL: {config.ANTHROPIC_BASE_URL}")
    print(f"AI Model: {config.ANTHROPIC_MODEL}")
    print(f"Real Trading: {config.ENABLE_REAL_TRADING}")
    print(f"Min Trade: {config.MIN_TRADE_AMOUNT} TON")
    print(f"Max Trade: {config.MAX_TRADE_AMOUNT} TON")
    print("="*60)
    print()

    # Connect wallet
    print("Connecting to wallet...")
    wallet = TonWallet()
    await wallet.connect()

    balance = await wallet.get_balance()
    print(f"Wallet Balance: {balance:.4f} TON\n")

    # Initialize DEX handler
    dex = DEXHandler(wallet)

    # Test STON.fi swap (simulation)
    print("Testing STON.fi swap...")
    decision = {
        'dex': 'stonfi',
        'token_pair': 'TON/USDT',
        'amount': 0.1
    }

    result = await dex.execute_trade(decision)
    print(f"Result: {'Success' if result else 'Failed'}\n")

    # Test DeDust swap (simulation)
    print("Testing DeDust swap...")
    decision = {
        'dex': 'dedust',
        'token_pair': 'TON/USDT',
        'amount': 0.1
    }

    result = await dex.execute_trade(decision)
    print(f"Result: {'Success' if result else 'Failed'}\n")

    await wallet.close()

    print("="*60)
    print("Test completed!")
    print()

    if not config.ENABLE_REAL_TRADING:
        print("NOTE: Real trading is DISABLED (simulation mode)")
        print("To enable real trading, set ENABLE_REAL_TRADING=true in .env")
    else:
        print("WARNING: Real trading is ENABLED!")
        print("Transactions will be sent to blockchain!")

if __name__ == "__main__":
    asyncio.run(test_trading())
