import os
from dotenv import load_dotenv

load_dotenv()

# Wallet settings
WALLET_MNEMONIC = os.getenv('WALLET_MNEMONIC', '')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS', '')

# AI settings
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ANTHROPIC_BASE_URL = os.getenv('ANTHROPIC_BASE_URL', 'https://api.kiro.cheap')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250514')

# Trading settings
MIN_TRADE_AMOUNT = float(os.getenv('MIN_TRADE_AMOUNT', '0.1'))
MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', '1.0'))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))
ENABLE_REAL_TRADING = os.getenv('ENABLE_REAL_TRADING', 'false').lower() == 'true'

# DEX endpoints
DEDUST_API = "https://api.dedust.io/v2"
STONFI_API = "https://api.ston.fi/v1"

# Known token addresses (TON mainnet)
TOKENS = {
    'TON': 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
    'USDT': 'EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs',
    'ECOR': 'EQDc_nrm5oOVCVQM8GRJ5q_hr1jgpNQjsGkIGE-uztt26_Ep',
    'UTYA': 'EQBaCgUwOoc6gHCNln_oJzb0mVs79YG7wYoavh-o1ItaneLA',
    'STON': 'EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO',
    'tsTON': 'EQC98_qAmNEptUtPc7W6xdHh_ZHrBUFpw5Ft_IzNU20QAJav',
    'GRAM': 'EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O',
    'DUST': 'EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE',
}
