import asyncio
from wallet import TonWallet
from typing import Dict
from pytoniq_core import Address, begin_cell
import config

class DEXHandler:
    def __init__(self, wallet: TonWallet):
        self.wallet = wallet

    async def execute_trade_dedust(self, token_pair: str, amount: float) -> bool:
        """Execute trade on DeDust"""
        print(f"[TRADE] Executing trade on DeDust: {amount} TON for {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print(f"[!] SIMULATION MODE - Set ENABLE_REAL_TRADING=true in .env for real trades")
            await asyncio.sleep(1)
            return True

        # DeDust Native Vault address (mainnet)
        DEDUST_VAULT = "EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_"

        try:
            # Parse token pair
            tokens = token_pair.split('/')
            if len(tokens) != 2:
                print(f"[X] Invalid token pair format: {token_pair}")
                return False

            from_token, to_token = tokens

            if from_token != 'TON':
                print(f"[X] Only TON -> Token swaps supported currently")
                return False

            # Build swap payload for DeDust
            # This is a simplified version - production needs proper pool lookup
            swap_payload = begin_cell().store_uint(0x9c610de3, 32).store_uint(0, 64).end_cell()

            print(f"[SWAP] Swapping {amount} TON to {to_token} on DeDust...")

            # Send transaction to vault
            await self.wallet.send_transaction(
                destination=DEDUST_VAULT,
                amount=amount,
                payload=swap_payload
            )

            print(f"[OK] DeDust swap transaction sent!")
            return True

        except Exception as e:
            print(f"[X] DeDust trade failed: {e}")
            return False

    async def execute_trade_stonfi(self, token_pair: str, amount: float) -> bool:
        """Execute trade on STON.fi"""
        print(f"[TRADE] Executing trade on STON.fi: {amount} TON for {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print(f"[!] SIMULATION MODE - Set ENABLE_REAL_TRADING=true in .env for real trades")
            await asyncio.sleep(1)
            return True

        # STON.fi router V2 address (mainnet)
        STONFI_ROUTER = "EQCM3B12QK1e4yZSf8GtBRT0aLMNyEsBc_DhVfRRtOEffLez"

        try:
            # Parse token pair
            tokens = token_pair.split('/')
            if len(tokens) != 2:
                print(f"[X] Invalid token pair format: {token_pair}")
                return False

            from_token, to_token = tokens

            if from_token != 'TON':
                print(f"[X] Only TON -> Token swaps supported currently")
                return False

            # Get token address from config
            to_token_address = config.TOKENS.get(to_token)
            if not to_token_address:
                print(f"[X] Unknown token: {to_token}")
                return False

            # Build STON.fi swap payload
            # op::swap_ton_to_jetton = 0x72aca8aa
            min_out = int(amount * 0.95 * 1e9)  # 5% slippage tolerance

            swap_payload = (
                begin_cell()
                .store_uint(0x72aca8aa, 32)  # op code for TON->Jetton swap
                .store_address(Address(to_token_address))  # token address
                .store_coins(min_out)  # minimum output amount
                .store_address(self.wallet.wallet.address)  # recipient
                .end_cell()
            )

            print(f"[SWAP] Swapping {amount} TON to {to_token} on STON.fi...")
            print(f"       Min output: {min_out / 1e9:.4f} tokens (5% slippage)")

            # Send transaction to router
            await self.wallet.send_transaction(
                destination=STONFI_ROUTER,
                amount=amount,
                payload=swap_payload
            )

            print(f"[OK] STON.fi swap transaction sent!")
            return True

        except Exception as e:
            print(f"[X] STON.fi trade failed: {e}")
            return False

    async def execute_trade(self, decision: Dict) -> bool:
        """Execute trade based on AI decision"""
        dex = decision.get('dex', '').lower()
        token_pair = decision.get('token_pair', '')
        amount = decision.get('amount', 0)

        if dex == 'dedust':
            return await self.execute_trade_dedust(token_pair, amount)
        elif dex == 'stonfi':
            return await self.execute_trade_stonfi(token_pair, amount)
        else:
            print(f"[X] Unknown DEX: {dex}")
            return False
