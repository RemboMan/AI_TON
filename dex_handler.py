import asyncio
from wallet import TonWallet
from typing import Dict
from pytoniq_core import Address, begin_cell, Cell
import config


class DEXHandler:
    def __init__(self, wallet: TonWallet):
        self.wallet = wallet

    async def get_jetton_wallet_address(
        self, jetton_master: str, owner_address: str
    ) -> str:
        """Get user's jetton wallet address for a specific token"""
        try:
            from pytoniq_core import begin_cell

            # Build get_wallet_address payload
            # This queries the jetton master contract for the user's wallet
            payload = begin_cell().store_address(Address(owner_address)).end_cell()

            # Query jetton master contract
            result = await self.wallet.client.run_get_method(
                address=jetton_master,
                method="get_wallet_address",
                stack=[payload.begin_parse()],
            )

            # Extract wallet address from result
            wallet_address = result[0].load_address()
            return wallet_address.to_str()

        except Exception as e:
            print(f"[X] Failed to get jetton wallet: {e}")
            raise

    async def send_jetton_transfer(
        self,
        jetton_wallet: str,
        amount: int,
        destination: str,
        forward_amount: int,
        forward_payload: Cell,
    ) -> bool:
        """Send jetton transfer with forward payload"""
        try:
            # Build jetton transfer payload
            # op::transfer = 0xf8a7ea5
            transfer_payload = (
                begin_cell()
                .store_uint(0xF8A7EA5, 32)  # op::transfer
                .store_uint(0, 64)  # query_id
                .store_coins(amount)  # jetton amount
                .store_address(Address(destination))  # destination (vault)
                .store_address(self.wallet.wallet.address)  # response_destination
                .store_uint(0, 1)  # custom_payload (nothing)
                .store_coins(forward_amount)  # forward_ton_amount
                .store_uint(1, 1)  # forward_payload (something)
                .store_ref(forward_payload)  # forward_payload as ref
                .end_cell()
            )

            # Send to jetton wallet with 0.3 TON for gas
            await self.wallet.send_transaction(
                destination=jetton_wallet, amount=0.3, payload=transfer_payload
            )

            return True

        except Exception as e:
            print(f"[X] Jetton transfer failed: {e}")
            return False

    async def get_dedust_pool_address(self, token_address: str) -> str:
        """Get DeDust pool address for TON/Token pair"""
        # Known pool addresses (verified from DeDust API on 2026-03-19)
        KNOWN_POOLS = {
            "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs": "EQA-X_yo3fzzbDbJ_0bzFWKqtRuZFIRa1sJsveZJ1YpViO3r",  # TON/USDT
            "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE": "EQDcm06RlreuMurm-yik9WbL6kI617B77OrSRF_ZjoCYFuny",  # TON/DUST
            "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO": "EQDix3nDPJCieD45fQgP-ik_YZyeEBOa2E3IL0mvjmOQPKp_",  # TON/STON
        }

        # Return known pool if available
        if token_address in KNOWN_POOLS:
            return KNOWN_POOLS[token_address]

        # Otherwise would need to query factory (not implemented)
        raise Exception(f"Pool address not found for token {token_address}")

    async def execute_trade_dedust(self, token_pair: str, amount: float) -> bool:
        """Execute trade on DeDust"""
        print(f"[TRADE] Executing trade on DeDust: {amount} TON for {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print("[!] SIMULATION MODE - Would swap on DeDust")
            await asyncio.sleep(1)
            return True

        # DeDust Native Vault address (mainnet)
        DEDUST_NATIVE_VAULT = "EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_"

        try:
            # Parse token pair
            tokens = token_pair.split("/")
            if len(tokens) != 2:
                print(f"[X] Invalid token pair format: {token_pair}")
                return False

            from_token, to_token = tokens

            if from_token != "TON":
                print("[X] Only TON -> Token swaps supported currently")
                return False

            # Get token address
            to_token_address = config.TOKENS.get(to_token)
            if not to_token_address:
                print(f"[X] Unknown token: {to_token}")
                return False

            # Get pool address
            try:
                pool_address = await self.get_dedust_pool_address(to_token_address)
            except Exception as e:
                print(f"[X] Failed to get pool address: {e}")
                return False

            # Build DeDust swap payload (based on official SDK)
            # op::swap = 0xea06185d (correct opcode from DeDust SDK)
            amount_nano = int(amount * 1e9)
            min_out = int(amount * 0.85 * 1e9)  # 15% slippage tolerance

            # Build swap params ref (required)
            swap_params = (
                begin_cell()
                .store_uint(0, 32)  # deadline (0 = no deadline)
                .store_address(self.wallet.wallet.address)  # recipient address
                .store_uint(0, 2)  # referral address (addr_none)
                .store_uint(0, 1)  # fulfill payload (nothing)
                .store_uint(0, 1)  # reject payload (nothing)
                .end_cell()
            )

            # Build main swap payload
            swap_payload = (
                begin_cell()
                .store_uint(0xEA06185D, 32)  # op::swap (correct opcode)
                .store_uint(0, 64)  # query_id
                .store_coins(amount_nano)  # swap amount
                .store_address(Address(pool_address))  # pool address
                .store_uint(0, 1)  # flag
                .store_coins(min_out)  # limit (min output)
                .store_uint(0, 1)  # next (no multi-hop - nothing)
                .store_ref(swap_params)  # swap params (required ref)
                .end_cell()
            )

            print(f"[SWAP] Swapping {amount} TON to {to_token} on DeDust...")
            print(f"       Pool: {pool_address}")
            print(f"       Min output: {min_out / 1e9:.4f} tokens (15% slippage)")
            print(f"       Recipient: {self.wallet.wallet.address.to_str()}")
            print("       Gas: 0.2 TON")

            # Send transaction to native vault
            # Total amount = swap amount + gas (0.2 TON as per SDK)
            await self.wallet.send_transaction(
                destination=DEDUST_NATIVE_VAULT,
                amount=amount + 0.2,
                payload=swap_payload,
            )

            print("[OK] DeDust swap transaction sent!")
            return True

        except Exception as e:
            print(f"[X] DeDust trade failed: {e}")
            return False

    async def execute_trade_stonfi(self, token_pair: str, amount: float) -> bool:
        """Execute trade on STON.fi"""
        print(f"[TRADE] Executing trade on STON.fi: {amount} TON for {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print(
                "[!] SIMULATION MODE - Set ENABLE_REAL_TRADING=true in .env for real trades"
            )
            await asyncio.sleep(1)
            return True

        # STON.fi router V2 address (mainnet)
        STONFI_ROUTER = "EQB3ncyBUTjZUA5EnFKR5_EnOMI9V1tTEAAPaiU71gc4TiUt"

        try:
            # Parse token pair
            tokens = token_pair.split("/")
            if len(tokens) != 2:
                print(f"[X] Invalid token pair format: {token_pair}")
                return False

            from_token, to_token = tokens

            if from_token != "TON":
                print("[X] Only TON -> Token swaps supported currently")
                return False

            # Get token address from config
            to_token_address = config.TOKENS.get(to_token)
            if not to_token_address:
                print(f"[X] Unknown token: {to_token}")
                return False

            # Build STON.fi V2 swap payload
            # op::swap = 0x25938561
            min_out = int(amount * 0.90 * 1e9)  # 10% slippage tolerance

            # Build forward payload for router
            swap_payload = (
                begin_cell()
                .store_uint(0x25938561, 32)  # op::swap for V2
                .store_address(
                    Address(to_token_address)
                )  # token_wallet (jetton we want)
                .store_coins(min_out)  # min_out
                .store_address(self.wallet.wallet.address)  # to_address (recipient)
                .store_uint(0, 1)  # has_referral_address = false
                .end_cell()
            )

            print(f"[SWAP] Swapping {amount} TON to {to_token} on STON.fi...")
            print(f"       Min output: {min_out / 1e9:.4f} tokens (10% slippage)")
            print(f"       Router: {STONFI_ROUTER}")

            # Send transaction to router with 0.3 TON for gas
            await self.wallet.send_transaction(
                destination=STONFI_ROUTER,
                amount=amount + 0.3,  # swap amount + gas
                payload=swap_payload,
            )

            print("[OK] STON.fi swap transaction sent!")
            return True

        except Exception as e:
            print(f"[X] STON.fi trade failed: {e}")
            return False

    async def sell_token_dedust(self, token_pair: str, token_amount: float) -> bool:
        """Sell tokens back to TON on DeDust"""
        print(f"[TRADE] Selling tokens for TON on DeDust: {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print("[!] SIMULATION MODE - Would sell on DeDust")
            await asyncio.sleep(1)
            return True

        # TODO: Implement jetton selling
        # Requires finding correct jetton vault addresses from Factory contract
        print("[!] Jetton selling not implemented yet")
        print("[!] Only TON -> Token swaps are supported currently")
        return False

    async def execute_trade(self, decision: Dict) -> bool:
        """Execute trade based on AI decision"""
        dex = decision.get("dex", "").lower()
        token_pair = decision.get("token_pair", "")
        amount = decision.get("amount", 0)
        trade_type = decision.get("type", "buy")  # 'buy' or 'sell'

        if trade_type == "sell":
            # Selling tokens back to TON
            if dex == "dedust":
                return await self.sell_token_dedust(token_pair, amount)
            elif dex == "stonfi":
                print("[!] STON.fi sell not implemented yet")
                return False
            else:
                print(f"[X] Unknown DEX: {dex}")
                return False
        else:
            # Buying tokens with TON
            if dex == "dedust":
                return await self.execute_trade_dedust(token_pair, amount)
            elif dex == "stonfi":
                return await self.execute_trade_stonfi(token_pair, amount)
            else:
                print(f"[X] Unknown DEX: {dex}")
                return False
