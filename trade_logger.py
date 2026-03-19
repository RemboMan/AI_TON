import json
import os
from datetime import datetime
from typing import Dict, List


class TradeLogger:
    def __init__(self, log_file="trades.json"):
        self.log_file = log_file
        self.trades = self._load_trades()

    def _load_trades(self) -> List[Dict]:
        """Load existing trades from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def log_trade(self, trade_data: Dict):
        """Log a new trade"""
        trade_data["logged_at"] = datetime.now().isoformat()
        self.trades.append(trade_data)
        self._save_trades()

    def _save_trades(self):
        """Save trades to file"""
        with open(self.log_file, "w") as f:
            json.dump(self.trades, f, indent=2)

    def get_stats(self) -> Dict:
        """Get trading statistics"""
        if not self.trades:
            return {"total_trades": 0, "total_volume": 0, "dexes_used": {}}

        total_volume = sum(t.get("amount", 0) for t in self.trades)
        dexes = {}
        for trade in self.trades:
            dex = trade.get("dex", "unknown")
            dexes[dex] = dexes.get(dex, 0) + 1

        return {
            "total_trades": len(self.trades),
            "total_volume": total_volume,
            "dexes_used": dexes,
            "first_trade": self.trades[0].get("timestamp") if self.trades else None,
            "last_trade": self.trades[-1].get("timestamp") if self.trades else None,
        }

    def print_history(self, limit=10):
        """Print recent trade history"""
        print(f"\n📊 Trade History (last {limit} trades)\n")
        print("=" * 80)

        if not self.trades:
            print("No trades yet.")
            return

        recent = self.trades[-limit:]
        for i, trade in enumerate(reversed(recent), 1):
            print(f"\n{i}. {trade.get('timestamp', 'N/A')}")
            print(f"   DEX: {trade.get('dex', 'N/A')}")
            print(f"   Pair: {trade.get('token_pair', 'N/A')}")
            print(f"   Amount: {trade.get('amount', 0)} TON")
            print(f"   Balance Before: {trade.get('balance_before', 0):.4f} TON")

        print("\n" + "=" * 80)

        stats = self.get_stats()
        print("\n📈 Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Total Volume: {stats['total_volume']:.4f} TON")
        print(f"   DEXes Used: {stats['dexes_used']}")


if __name__ == "__main__":
    logger = TradeLogger()
    logger.print_history()
