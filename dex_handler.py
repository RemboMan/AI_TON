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

            # Send to jetton wallet with 0.5 TON total (0.25 forward + 0.25 jetton wallet gas)
            await self.wallet.send_transaction(
                destination=jetton_wallet, amount=0.5, payload=transfer_payload
            )

            return True

        except Exception as e:
            print(f"[X] Jetton transfer failed: {e}")
            return False

    async def get_dedust_pool_address(self, token_address: str) -> str:
        """Get DeDust pool address for TON/Token pair"""
        # Known pool addresses (verified from DeDust API on 2026-03-20)
        KNOWN_POOLS = {
            "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs": "EQA-X_yo3fzzbDbJ_0bzFWKqtRuZFIRa1sJsveZJ1YpViO3r",  # TON/USDT
            "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE": "EQDcm06RlreuMurm-yik9WbL6kI617B77OrSRF_ZjoCYFuny",  # TON/DUST
            "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO": "EQDix3nDPJCieD45fQgP-ik_YZyeEBOa2E3IL0mvjmOQPKp_",  # TON/STON
            "EQB0SoxuGDx5qjVt0P_bPICFeWdFLBmVopHhjgfs0q-wsTON": "EQABt8YegyD7VJnZdFVwom8wwqp0E0X8tN2Y6NhrDmbrnSXP",  # TON/wsTON
            "EQD0laik0FgHV8aNfRhebi8GDG2rpDyKGXem0MBfya_Ew1-8": "EQDh9HoI_XrAYeuvUZLrlH2BGfYKvF4Jz_z67zkzG7_7uTgN",  # TON/GOMINING
        }

        # Return known pool if available
        if token_address in KNOWN_POOLS:
            return KNOWN_POOLS[token_address]

        # Otherwise would need to query factory (not implemented)
        raise Exception(f"Pool address not found for token {token_address}")

    async def get_pool_reserves(self, pool_address: str) -> tuple:
        """Get pool reserves from DeDust pool contract"""
        try:
            # Query pool contract for reserves
            # DeDust pools have get_assets method that returns reserves
            result = await self.wallet.client.run_get_method(
                address=pool_address, method="get_assets", stack=[]
            )

            # get_assets returns: [reserve0, reserve1]
            # Handle both int and Slice types
            if isinstance(result[0], int):
                reserve0 = result[0]
            else:
                # It's a Slice, load coins (VarUInteger 16)
                reserve0 = result[0].load_coins()

            if isinstance(result[1], int):
                reserve1 = result[1]
            else:
                reserve1 = result[1].load_coins()

            return (reserve0, reserve1)
        except Exception as e:
            print(f"[!] Could not query pool reserves: {e}")
            # Return None to indicate failure
            return None

    def calculate_output_amount(
        self, input_amount: int, reserve_in: int, reserve_out: int
    ) -> int:
        """Calculate expected output using constant product formula (x * y = k)"""
        # Formula: output = (input * reserve_out) / (reserve_in + input)
        # This is simplified AMM formula without fees
        # DeDust has 0.3% fee, so actual formula is:
        # input_with_fee = input * 997 / 1000
        # output = (input_with_fee * reserve_out) / (reserve_in + input_with_fee)

        input_with_fee = (input_amount * 997) // 1000  # 0.3% fee
        output = (input_with_fee * reserve_out) // (reserve_in + input_with_fee)

        return output

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

            # Build DeDust swap payload (based on official TLB scheme)
            # op::swap = 0xea06185d
            amount_nano = int(amount * 1e9)  # Actual swap amount in nanotons

            # Calculate min_out with 1% slippage
            min_out = 1  # Default fallback
            try:
                reserves = await self.get_pool_reserves(pool_address)
                if reserves:
                    reserve_ton, reserve_token = reserves
                    # Calculate expected output
                    expected_output = self.calculate_output_amount(
                        amount_nano, reserve_ton, reserve_token
                    )
                    # Apply 1% slippage tolerance
                    min_out = int(expected_output * 0.99)
                    print(
                        f"       Expected output: {expected_output / 1e9:.4f} {to_token}"
                    )
                    print(
                        f"       Min output (1% slippage): {min_out / 1e9:.4f} {to_token}"
                    )
                else:
                    print("       [!] Could not query reserves, using min_out = 1")
            except Exception as e:
                print(f"       [!] Reserve query failed: {e}, using min_out = 1")

            # Build swap params ref (required)
            swap_params = (
                begin_cell()
                .store_uint(0, 32)  # deadline (0 = no deadline)
                .store_address(self.wallet.wallet.address)  # recipient address
                .store_address(None)  # referral address (addr_none)
                .store_uint(0, 1)  # fulfill payload (nothing)
                .store_uint(0, 1)  # reject payload (nothing)
                .end_cell()
            )

            # Build main swap payload
            # TLB: swap#ea06185d query_id:uint64 amount:Coins _:SwapStep swap_params:^SwapParams
            # SwapStep: pool_addr:MsgAddressInt params:SwapStepParams
            # SwapStepParams: kind:SwapKind limit:Coins next:(Maybe ^SwapStep)
            swap_payload = (
                begin_cell()
                .store_uint(0xEA06185D, 32)  # op::swap
                .store_uint(0, 64)  # query_id
                .store_coins(amount_nano)  # amount
                # SwapStep (inline):
                .store_address(Address(pool_address))  # pool_addr
                # SwapStepParams (inline):
                .store_uint(0, 1)  # kind: 0 = given_in (we specify input amount)
                .store_coins(min_out)  # limit (minimum output)
                .store_uint(0, 1)  # next: Maybe = nothing (no multi-hop)
                # swap_params as reference:
                .store_ref(swap_params)
                .end_cell()
            )

            print(f"[SWAP] Swapping {amount} TON to {to_token} on DeDust...")
            print(f"       Pool: {pool_address}")
            print("       Gas: 0.3 TON")
            print(f"       Total sent: {amount + 0.3} TON")

            # Send transaction to native vault
            # Total amount = swap amount + gas (0.3 TON)
            await self.wallet.send_transaction(
                destination=DEDUST_NATIVE_VAULT,
                amount=amount + 0.3,
                payload=swap_payload,
            )

            print("[OK] DeDust swap transaction sent!")
            return True

        except Exception as e:
            print(f"[X] DeDust trade failed: {e}")
            return False

    async def sell_token_dedust(self, token_pair: str, token_amount: float) -> bool:
        """Sell tokens back to TON on DeDust"""
        print(f"[TRADE] Selling tokens for TON on DeDust: {token_pair}")

        if not config.ENABLE_REAL_TRADING:
            print("[!] SIMULATION MODE - Would sell on DeDust")
            await asyncio.sleep(1)
            return True

        try:
            # Parse token pair (e.g., "TON/USDT" means selling USDT for TON)
            tokens = token_pair.split("/")
            if len(tokens) != 2:
                print(f"[X] Invalid token pair format: {token_pair}")
                return False

            base_token, sell_token = tokens

            if base_token != "TON":
                print("[X] Only Token -> TON swaps supported currently")
                return False

            # Get token address
            sell_token_address = config.TOKENS.get(sell_token)
            if not sell_token_address:
                print(f"[X] Unknown token: {sell_token}")
                return False

            # Get pool address
            try:
                pool_address = await self.get_dedust_pool_address(sell_token_address)
            except Exception as e:
                print(f"[X] Failed to get pool address: {e}")
                return False

            # Get user's jetton wallet for this token
            print(f"[SELL] Getting jetton wallet for {sell_token}...")
            try:
                jetton_wallet = await self.get_jetton_wallet_address(
                    sell_token_address, self.wallet.wallet.address.to_str()
                )
                print(f"       Jetton wallet: {jetton_wallet}")
            except Exception as e:
                print(f"[X] Failed to get jetton wallet: {e}")
                return False

            # Calculate token amount based on decimals
            if sell_token == "USDT":
                token_amount_nano = int(token_amount * 1e6)  # USDT has 6 decimals
            elif sell_token == "GOMINING":
                token_amount_nano = int(token_amount * 1e18)  # GOMINING has 18 decimals
            else:
                token_amount_nano = int(
                    token_amount * 1e9
                )  # Most tokens have 9 decimals

            # Calculate min_out with 1% slippage
            min_ton_out = 1  # Default fallback
            try:
                reserves = await self.get_pool_reserves(pool_address)
                if reserves:
                    reserve_ton, reserve_token = reserves
                    # Calculate expected TON output
                    expected_ton = self.calculate_output_amount(
                        token_amount_nano, reserve_token, reserve_ton
                    )
                    # Apply 1% slippage tolerance
                    min_ton_out = int(expected_ton * 0.99)
                    print(f"       Expected TON output: {expected_ton / 1e9:.4f} TON")
                    print(
                        f"       Min TON output (1% slippage): {min_ton_out / 1e9:.4f} TON"
                    )
                else:
                    print("       [!] Could not query reserves, using min_out = 1")
            except Exception as e:
                print(f"       [!] Reserve query failed: {e}, using min_out = 1")

            # Build swap params for the forward payload
            swap_params = (
                begin_cell()
                .store_uint(0, 32)  # deadline
                .store_address(self.wallet.wallet.address)  # recipient
                .store_address(None)  # referral address (addr_none)
                .store_uint(0, 1)  # fulfill payload
                .store_uint(0, 1)  # reject payload
                .end_cell()
            )

            # Build swap payload (will be sent as forward_payload in jetton transfer)
            swap_payload = (
                begin_cell()
                .store_uint(0xEA06185D, 32)  # op::swap
                .store_uint(0, 64)  # query_id
                .store_coins(token_amount_nano)  # amount of tokens to swap
                .store_address(Address(pool_address))  # pool address
                .store_uint(0, 1)  # kind: given_in
                .store_coins(min_ton_out)  # minimum TON output
                .store_uint(0, 1)  # next: nothing
                .store_ref(swap_params)
                .end_cell()
            )

            print(f"[SWAP] Selling {token_amount} {sell_token} for TON on DeDust...")
            print(f"       Pool: {pool_address}")
            print(f"       Jetton wallet: {jetton_wallet}")
            print("       Gas: 0.5 TON (0.3 forward + 0.2 jetton wallet)")

            # Send jetton transfer with swap payload
            # This will transfer tokens to the vault and trigger the swap
            success = await self.send_jetton_transfer(
                jetton_wallet=jetton_wallet,
                amount=token_amount_nano,
                destination="EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_",  # Native vault
                forward_amount=int(0.3 * 1e9),  # Forward 0.3 TON for swap gas
                forward_payload=swap_payload,
            )

            if success:
                print("[OK] DeDust sell transaction sent!")
            return success

        except Exception as e:
            print(f"[X] DeDust sell failed: {e}")
            return False

    async def execute_trade(self, decision: Dict) -> bool:
        """Execute trade based on AI decision (DeDust only)"""
        token_pair = decision.get("token_pair", "")
        amount = decision.get("amount", 0)
        trade_type = decision.get("type", "buy")  # 'buy' or 'sell'

        if trade_type == "sell":
            # Selling tokens back to TON (DeDust only)
            return await self.sell_token_dedust(token_pair, amount)
        else:
            # Buying tokens with TON (DeDust only)
            return await self.execute_trade_dedust(token_pair, amount)
