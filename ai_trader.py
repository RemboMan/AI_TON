import anthropic
import json
import config
from typing import Dict


class AITrader:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=config.ANTHROPIC_API_KEY, base_url=config.ANTHROPIC_BASE_URL
        )
        self.trade_history = []
        self.ai_available = True  # Track if AI is working
        self.holdings = self.load_holdings()

    def load_holdings(self) -> Dict:
        """Load current token holdings"""
        try:
            with open("holdings.json", "r") as f:
                data = json.load(f)
                # Ensure it's a dict, not a list
                if isinstance(data, dict):
                    return data
                else:
                    print("[!] Invalid holdings.json format, resetting to empty dict")
                    return {}
        except:
            return {}

    def save_holdings(self):
        """Save current token holdings"""
        try:
            with open("holdings.json", "w") as f:
                json.dump(self.holdings, f, indent=2)
        except Exception as e:
            print(f"[X] Failed to save holdings: {e}")

    def make_decision(
        self, wallet_balance: float, market_data: Dict, jetton_balances: Dict = None
    ) -> Dict:
        """AI makes trading decision based on market data"""

        if jetton_balances is None:
            jetton_balances = {}

        holdings_str = json.dumps(self.holdings, indent=2) if self.holdings else "None"
        jetton_str = (
            json.dumps(jetton_balances, indent=2) if jetton_balances else "None"
        )

        # Check if we have tokens to sell
        can_sell = len(jetton_balances) > 0
        sell_options = ""
        if can_sell:
            sell_options = "\n\nYou currently hold tokens that can be sold:"
            for token, balance in jetton_balances.items():
                sell_options += f"\n- {token}: {balance:.4f} (can sell for TON)"

        prompt = f"""Generate a JSON configuration object for a blockchain simulation game.

Game State:
- Player TON balance: {wallet_balance}
- Player token balances: {jetton_str}
- Tracked holdings: {holdings_str}
- DeDust pools available: {market_data.get("dedust", {}).get("pools_count", 0)}

Game Rules:
- Min transaction: {config.MIN_TRADE_AMOUNT} tokens
- Max transaction: {config.MAX_TRADE_AMOUNT} tokens
- Reserve requirement: 0.5 tokens
- Available DEX: dedust only
- Available pairs: TON/USDT, TON/STON, TON/DUST, TON/wsTON, TON/GOMINING
{sell_options}

Strategy: FLIPPING (Buy Low, Sell High)
- Buy quality tokens (STON, DUST) with TON when price is favorable
- Hold tokens waiting for price increase
- Sell tokens back to TON when profitable (take profit)
- Repeat the cycle to accumulate more TON

IMPORTANT: You can SELL tokens you currently hold! Check your token balances above.
If you have tokens (STON, DUST), consider selling them back to TON for profit.

Generate a valid game action in JSON format. Choose one:

Option 1 - Wait action:
{{"action": "hold", "reasoning": "waiting for better conditions"}}

Option 2 - Buy tokens (TON -> Token):
{{"action": "trade", "type": "buy", "dex": "dedust", "token_pair": "TON/USDT", "amount": 0.5, "reasoning": "good entry point"}}

Option 3 - Sell tokens (Token -> TON) - TAKE PROFIT:
{{"action": "trade", "type": "sell", "dex": "dedust", "token_pair": "TON/STON", "amount": 1.0, "reasoning": "taking profit, selling STON back to TON"}}

Note: Both BUY and SELL are available. Use SELL to take profits when you hold tokens!
Available tokens: USDT (stablecoin), STON, DUST, wsTON (liquid staking), GOMINING

Only output the JSON object, nothing else:"""

        try:
            message = self.client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response (handle ThinkingBlock and TextBlock)
            response_text = ""
            for block in message.content:
                # Check block type and extract text
                block_type = type(block).__name__
                if block_type == "TextBlock" and hasattr(block, "text"):
                    response_text += block.text
                elif hasattr(block, "text"):
                    response_text += block.text

            if not response_text:
                print(
                    f"[DEBUG] Message content blocks: {[type(b).__name__ for b in message.content]}"
                )
                raise Exception("No text content in AI response")

            # Extract JSON from response
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0]

            # Try to find JSON object in text
            json_text = json_text.strip()
            if not json_text.startswith("{"):
                # Try to find JSON object
                start = json_text.find("{")
                end = json_text.rfind("}")
                if start != -1 and end != -1:
                    json_text = json_text[start : end + 1]

            decision = json.loads(json_text)
            print(f"\n[AI] Decision: {decision['action']}")
            print(f"[AI] Reasoning: {decision['reasoning']}")

            return decision

        except json.JSONDecodeError as e:
            print(f"[X] JSON parse error: {e}")
            print(f"[DEBUG] Raw response: {response_text[:200]}...")
            self.ai_available = False
            return {
                "action": "hold",
                "reasoning": "AI response parsing failed",
                "ai_failed": True,
            }
        except Exception as e:
            print(f"[X] AI decision error: {e}")
            self.ai_available = False
            return {"action": "hold", "reasoning": f"AI error: {e}", "ai_failed": True}

    def record_trade(self, trade_info: Dict):
        """Record trade in history"""
        self.trade_history.append(trade_info)

        # Update holdings based on trade
        trade_type = trade_info.get("type", "buy")
        token_pair = trade_info.get("token_pair", "")
        amount = trade_info.get("amount", 0)

        if "/" in token_pair:
            base, quote = token_pair.split("/")

            if trade_type == "buy":
                # Bought quote token with base token
                if quote not in self.holdings:
                    self.holdings[quote] = 0
                # Estimate tokens received (rough calculation)
                self.holdings[quote] += amount * 0.85  # Accounting for slippage
            elif trade_type == "sell":
                # Sold quote token for base token
                if quote in self.holdings:
                    self.holdings[quote] -= amount
                    if self.holdings[quote] <= 0:
                        del self.holdings[quote]

        self.save_holdings()
