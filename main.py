import asyncio
import time
from datetime import datetime
from wallet import TonWallet
from market_data import MarketData
from ai_trader import AITrader
from dex_handler import DEXHandler
from trade_logger import TradeLogger
import config

class TonAIBot:
    def __init__(self):
        self.wallet = TonWallet()
        self.market_data = MarketData()
        self.ai_trader = AITrader()
        self.dex_handler = None
        self.trade_logger = TradeLogger()
        self.running = False

    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing TON AI Trading Bot...")
        print(f"📡 API: {config.ANTHROPIC_BASE_URL}")
        print(f"🤖 Model: {config.ANTHROPIC_MODEL}")
        print(f"💱 Real Trading: {'ENABLED ⚠️' if config.ENABLE_REAL_TRADING else 'DISABLED (Simulation)'}")
        await self.wallet.connect()
        await self.market_data.init_session()
        self.dex_handler = DEXHandler(self.wallet)
        print("✅ Bot initialized successfully\n")

    async def run_cycle(self):
        """Run one trading cycle"""
        print(f"\n{'='*60}")
        print(f"⏰ Cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Get wallet balance
        balance = await self.wallet.get_balance()
        print(f"💰 Current balance: {balance:.4f} TON")

        # Get market data
        print("📊 Fetching market data...")
        market_overview = await self.market_data.get_market_overview()

        # AI makes decision
        print("🤖 AI analyzing market...")
        decision = self.ai_trader.make_decision(balance, market_overview)

        # Execute decision
        if decision['action'] == 'trade':
            print(f"\n💱 Executing trade...")
            success = await self.dex_handler.execute_trade(decision)

            if success:
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'action': decision['action'],
                    'dex': decision.get('dex'),
                    'token_pair': decision.get('token_pair'),
                    'amount': decision.get('amount'),
                    'balance_before': balance
                }
                self.ai_trader.record_trade(trade_record)
                self.trade_logger.log_trade(trade_record)
                print("✅ Trade executed successfully")
            else:
                print("❌ Trade failed")
        elif decision['action'] == 'hold':
            print("⏸️  AI decided to hold position")
        else:
            print("🔍 AI analyzing, no action taken")

    async def run(self):
        """Main bot loop"""
        await self.initialize()
        self.running = True

        print(f"\n🤖 Bot is now running. Checking every {config.CHECK_INTERVAL} seconds.")
        print("Press Ctrl+C to stop.\n")

        try:
            while self.running:
                await self.run_cycle()
                print(f"\n⏳ Waiting {config.CHECK_INTERVAL} seconds until next cycle...")
                await asyncio.sleep(config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping bot...")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        await self.market_data.close_session()
        await self.wallet.close()

        # Print final statistics
        print("\n" + "="*60)
        print("📊 Final Trading Statistics")
        print("="*60)
        stats = self.trade_logger.get_stats()
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Total Volume: {stats['total_volume']:.4f} TON")
        print(f"DEXes Used: {stats['dexes_used']}")
        print("="*60)

        print("\n✅ Bot stopped successfully")

async def main():
    bot = TonAIBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
