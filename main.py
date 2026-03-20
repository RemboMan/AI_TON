import asyncio
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
        print("Initializing TON AI Trading Bot...")
        print(f"API: {config.ANTHROPIC_BASE_URL}")
        print(f"Model: {config.ANTHROPIC_MODEL}")
        print(
            f"Real Trading: {'ENABLED' if config.ENABLE_REAL_TRADING else 'DISABLED (Simulation)'}"
        )
        await self.wallet.connect()
        await self.market_data.init_session()
        self.dex_handler = DEXHandler(self.wallet)
        print("[OK] Bot initialized successfully\n")

    async def run_cycle(self):
        """Run one trading cycle"""
        print(f"\n{'=' * 60}")
        print(f"[CYCLE] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")

        try:
            # Get all balances (TON + jettons)
            all_balances = await self.wallet.get_all_balances()
            ton_balance = all_balances.get("TON", 0)

            print(f"[BALANCE] TON: {ton_balance:.4f}")

            # Show jetton balances if any
            jetton_balances = {
                k: v for k, v in all_balances.items() if k != "TON" and v > 0
            }
            if jetton_balances:
                for token, balance in jetton_balances.items():
                    print(f"          {token}: {balance:.4f}")

            # Check if balance is valid
            if ton_balance <= 0:
                print("[!] TON balance is 0 or unavailable, skipping cycle")
                return

            # Show current holdings
            if self.ai_trader.holdings:
                print(f"[HOLDINGS] Current tokens: {self.ai_trader.holdings}")

            # Get market data
            print("[MARKET] Fetching market data...")
            market_overview = await self.market_data.get_market_overview()

            # AI makes decision (pass all balances)
            print("[AI] Analyzing market...")
            decision = self.ai_trader.make_decision(
                ton_balance, market_overview, jetton_balances
            )

            if decision.get("ai_failed"):
                print("[X] AI failed to make decision, skipping cycle")
                return

            # Execute decision
            if decision["action"] == "trade":
                print("\n[TRADE] Executing trade...")
                success = await self.dex_handler.execute_trade(decision)

                if success:
                    trade_record = {
                        "timestamp": datetime.now().isoformat(),
                        "action": decision["action"],
                        "type": decision.get("type", "buy"),
                        "dex": decision.get("dex"),
                        "token_pair": decision.get("token_pair"),
                        "amount": decision.get("amount"),
                        "balance_before": ton_balance,
                    }
                    self.ai_trader.record_trade(trade_record)
                    self.trade_logger.log_trade(trade_record)
                    print("[OK] Trade executed successfully")
                else:
                    print("[X] Trade failed")
            elif decision["action"] == "hold":
                print("[HOLD] AI decided to hold position")
            else:
                print("[ANALYZE] AI analyzing, no action taken")

        except Exception as e:
            print(f"[X] Cycle error: {e}")
            print("[!] Skipping this cycle, will retry next time")

    async def run(self):
        """Main bot loop"""
        await self.initialize()
        self.running = True

        print(f"\n[BOT] Running. Checking every {config.CHECK_INTERVAL} seconds.")
        print("Press Ctrl+C to stop.\n")

        try:
            while self.running:
                await self.run_cycle()
                print(
                    f"\n[WAIT] Waiting {config.CHECK_INTERVAL} seconds until next cycle..."
                )
                await asyncio.sleep(config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n[STOP] Stopping bot...")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        await self.market_data.close_session()
        await self.wallet.close()

        # Print final statistics
        print("\n" + "=" * 60)
        print("[STATS] Final Trading Statistics")
        print("=" * 60)
        stats = self.trade_logger.get_stats()
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Total Volume: {stats['total_volume']:.4f} TON")
        print(f"DEXes Used: {stats['dexes_used']}")
        print("=" * 60)

        print("\n[OK] Bot stopped successfully")


async def main():
    bot = TonAIBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
