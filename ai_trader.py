import anthropic
import json
import config
from typing import Dict

class AITrader:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=config.ANTHROPIC_API_KEY,
            base_url=config.ANTHROPIC_BASE_URL
        )
        self.trade_history = []

    def make_decision(self, wallet_balance: float, market_data: Dict) -> Dict:
        """AI makes trading decision based on market data"""

        prompt = f"""You are an autonomous crypto trading AI managing a TON wallet.

Current Status:
- Wallet Balance: {wallet_balance} TON
- Available DEXes: DeDust, STON.fi
- Min Trade Amount: {config.MIN_TRADE_AMOUNT} TON
- Max Trade Amount: {config.MAX_TRADE_AMOUNT} TON

Market Data:
{json.dumps(market_data, indent=2)}

Recent Trades (last 5):
{json.dumps(self.trade_history[-5:], indent=2) if self.trade_history else 'No trades yet'}

Trading Strategy Guidelines:
1. Analyze pool liquidity and trading volume
2. Look for arbitrage opportunities between DEXes
3. Consider market trends and token performance
4. Manage risk - don't trade more than {config.MAX_TRADE_AMOUNT} TON at once
5. Keep some TON for gas fees (minimum 0.5 TON reserve)
6. Learn from previous trades - avoid repeating mistakes

Your goal: Make profitable trades while managing risk.

Respond ONLY with valid JSON in this format:
{{
    "action": "trade" or "hold" or "analyze",
    "dex": "dedust" or "stonfi" (if trading),
    "token_pair": "TON/USDT" (if trading),
    "amount": 0.5 (TON amount if trading, must be between {config.MIN_TRADE_AMOUNT} and {config.MAX_TRADE_AMOUNT}),
    "reasoning": "brief explanation of your decision"
}}"""

        try:
            message = self.client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            # Extract JSON from response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]

            decision = json.loads(response_text.strip())
            print(f"\n🤖 AI Decision: {decision['action']}")
            print(f"💭 Reasoning: {decision['reasoning']}")

            return decision

        except Exception as e:
            print(f"❌ AI decision error: {e}")
            return {"action": "hold", "reasoning": f"Error: {e}"}

    def record_trade(self, trade_info: Dict):
        """Record trade in history"""
        self.trade_history.append(trade_info)
