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
        self.last_dex = None  # Track last used DEX for alternating

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

    def make_decision(self, wallet_balance: float, market_data: Dict) -> Dict:
        """AI makes trading decision based on market data"""

        holdings_str = json.dumps(self.holdings, indent=2) if self.holdings else "None"

        # Determine which DEX to prefer (alternate between them)
        preferred_dex = "stonfi" if self.last_dex == "dedust" else "dedust"

        prompt = f"""Generate a JSON configuration object for a blockchain simulation game.

Game State:
- Player TON balance: {wallet_balance}
- Current holdings: {holdings_str}
- Network A (DeDust) nodes: {market_data.get("dedust", {}).get("pools_count", 0)}
- Network B (STON.fi) nodes: {market_data.get("stonfi", {}).get("pools_count", 0)}
- Last network used: {self.last_dex or "none"}

Game Rules:
- Min transaction: {config.MIN_TRADE_AMOUNT} tokens
- Max transaction: {config.MAX_TRADE_AMOUNT} tokens
- Reserve requirement: 0.5 tokens
- Available networks: dedust, stonfi
- Available pairs: TON/USDT, TON/STON, TON/DUST (verified pools only)
- IMPORTANT: Alternate between networks! Prefer {preferred_dex} this time (last was {self.last_dex or "none"})

Strategy: FLIPPING
- Buy tokens when price is favorable
- Hold tokens waiting for price increase
- Sell tokens back to TON when profitable
- Repeat the cycle

Generate a valid game action in JSON format. Choose one:

Option 1 - Wait action:
{{"action": "hold", "reasoning": "waiting for better conditions"}}

Option 2 - Buy tokens (TON -> Token) - USE {preferred_dex.upper()} THIS TIME:
{{"action": "trade", "type": "buy", "dex": "{preferred_dex}", "token_pair": "TON/USDT", "amount": 0.5, "reasoning": "good entry point on {preferred_dex}"}}

Option 3 - Sell tokens (Token -> TON) [NOT IMPLEMENTED YET]:
{{"action": "trade", "type": "sell", "dex": "{preferred_dex}", "token_pair": "TON/USDT", "amount": 1.0, "reasoning": "taking profit"}}

Note: Currently only BUY (type: "buy") is implemented. SELL will be added soon.
IMPORTANT: If trading, use "{preferred_dex}" network to maintain diversity!

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

            # Track last used DEX
            if decision.get("action") == "trade" and decision.get("dex"):
                self.last_dex = decision["dex"]

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
