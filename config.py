import os
from dotenv import load_dotenv

load_dotenv()

# Wallet settings
WALLET_MNEMONIC = os.getenv("WALLET_MNEMONIC", "")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")

# AI settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.kiro.cheap")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250514")

# Trading settings
MIN_TRADE_AMOUNT = float(os.getenv("MIN_TRADE_AMOUNT", "0.1"))
MAX_TRADE_AMOUNT = float(os.getenv("MAX_TRADE_AMOUNT", "1.0"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
ENABLE_REAL_TRADING = os.getenv("ENABLE_REAL_TRADING", "false").lower() == "true"

# Only DeDust is supported (STON.fi removed from codebase)
FORCE_DEDUST = True

# DEX endpoints
DEDUST_API = "https://api.dedust.io/v2"
STONFI_API = "https://api.ston.fi/v1"

# Known token addresses (TON mainnet)
# IMPORTANT: These must be JETTON MASTER addresses, not pool addresses!
TOKENS = {
    "TON": "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
    "USDT": "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",  # Tether USD
    "STON": "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO",  # STON token
    "DUST": "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE",  # DUST token
    "wsTON": "EQB0SoxuGDx5qjVt0P_bPICFeWdFLBmVopHhjgfs0q-wsTON",  # Ton Whales liquid staking
    "GOMINING": "EQD0laik0FgHV8aNfRhebi8GDG2rpDyKGXem0MBfya_Ew1-8",  # GoMining token
}
