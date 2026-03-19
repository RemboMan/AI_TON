import asyncio
import sys
import os
from dotenv import load_dotenv

async def test_setup():
    """Test if everything is configured correctly"""
    print("Testing TON AI Trading Bot Setup\n")

    all_good = True

    # Test 1: Check .env file
    print("1. Checking .env file...")
    if not os.path.exists('.env'):
        print("   [X] .env file not found!")
        print("   -> Create it: cp .env.example .env")
        all_good = False
    else:
        print("   [OK] .env file exists")
        load_dotenv()

        # Check required variables
        required_vars = ['WALLET_MNEMONIC', 'ANTHROPIC_API_KEY']
        for var in required_vars:
            value = os.getenv(var, '')
            if not value or value.startswith('your'):
                print(f"   [X] {var} not configured")
                all_good = False
            else:
                print(f"   [OK] {var} configured")

    print()

    # Test 2: Check dependencies
    print("2. Checking dependencies...")
    try:
        import pytoniq
        print("   [OK] pytoniq installed")
    except ImportError:
        print("   [X] pytoniq not installed")
        print("   -> Run: pip install -r requirements.txt")
        all_good = False

    try:
        import anthropic
        print("   [OK] anthropic installed")
    except ImportError:
        print("   [X] anthropic not installed")
        all_good = False

    try:
        import aiohttp
        print("   [OK] aiohttp installed")
    except ImportError:
        print("   [X] aiohttp not installed")
        all_good = False

    print()

    # Test 3: Test wallet connection (if configured)
    if all_good:
        print("3. Testing wallet connection...")
        try:
            from wallet import TonWallet
            wallet = TonWallet()
            await wallet.connect()
            balance = await wallet.get_balance()
            print(f"   [OK] Wallet connected!")
            print(f"   Balance: {balance:.4f} TON")
            await wallet.close()
        except Exception as e:
            print(f"   [X] Wallet connection failed: {e}")
            all_good = False

        print()

        # Test 4: Test market data APIs
        print("4. Testing market data APIs...")
        try:
            from market_data import MarketData
            market = MarketData()
            await market.init_session()
            data = await market.get_market_overview()
            print(f"   [OK] DeDust API: {data['dedust']['pools_count']} pools")
            print(f"   [OK] STON.fi API: {data['stonfi']['pools_count']} pools")
            await market.close_session()
        except Exception as e:
            print(f"   [X] Market data failed: {e}")
            all_good = False

        print()

        # Test 5: Test AI connection
        print("5. Testing AI connection...")
        try:
            import anthropic
            import config
            client = anthropic.Anthropic(
                api_key=config.ANTHROPIC_API_KEY,
                base_url=config.ANTHROPIC_BASE_URL
            )
            message = client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'OK' if you can read this"}]
            )
            print(f"   [OK] AI connected and responding")
        except Exception as e:
            print(f"   [X] AI connection failed: {e}")
            all_good = False

    print()
    print("="*60)
    if all_good:
        print("[OK] All tests passed! You can run: python main.py")
    else:
        print("[FAIL] Some tests failed. Fix the issues above before running the bot.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_setup())
