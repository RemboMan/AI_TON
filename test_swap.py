"""
Test script for trying small token swaps and checking balances
"""

import asyncio
from pytoniq import LiteBalancer, WalletV5R1
from pytoniq_core import Address, begin_cell
import config

# Test tokens to try (small amounts)
TEST_TOKENS = {
    "STON": {
        "address": "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO",
        "pool": "EQDix3nDPJCieD45fQgP-ik_YZyeEBOa2E3IL0mvjmOQPKp_",  # DeDust TON/STON
    },
    "DUST": {
        "address": "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE",
        "pool": "EQDcm06RlreuMurm-yik9WbL6kI617B77OrSRF_ZjoCYFuny",  # DeDust TON/DUST
    },
}

# DeDust Native Vault (for TON swaps)
DEDUST_NATIVE_VAULT = "EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_"


class SwapTester:
    def __init__(self):
        self.mnemonic = config.WALLET_MNEMONIC.split()
        self.wallet = None
        self.client = None

    async def connect(self):
        """Connect to TON network"""
        print("[CONNECT] Connecting to TON mainnet...")
        self.client = LiteBalancer.from_mainnet_config(trust_level=2)
        await self.client.start_up()

        self.wallet = await WalletV5R1.from_mnemonic(
            self.client, self.mnemonic, network_global_id=-239
        )
        print(f"[OK] Connected: {self.wallet.address.to_str()}\n")

    async def get_ton_balance(self):
        """Get TON balance"""
        account_state = await self.client.get_account_state(self.wallet.address)
        return account_state.balance / 1e9

    async def get_jetton_wallet(self, jetton_master_address: str):
        """Get user's jetton wallet address for a specific token"""
        try:
            # Call get_wallet_address method on jetton master
            result = await self.client.run_get_method(
                address=jetton_master_address,
                method="get_wallet_address",
                stack=[self.wallet.address.to_cell().begin_parse()],
            )

            if result and len(result) > 0:
                jetton_wallet_address = result[0].load_address()
                return jetton_wallet_address
        except Exception as e:
            print(f"[!] Error getting jetton wallet: {e}")
        return None

    async def get_jetton_balance(self, jetton_master_address: str):
        """Get jetton balance for a specific token"""
        try:
            jetton_wallet = await self.get_jetton_wallet(jetton_master_address)
            if not jetton_wallet:
                return 0

            # Get balance from jetton wallet
            result = await self.client.run_get_method(
                address=jetton_wallet.to_str(), method="get_wallet_data", stack=[]
            )

            if result and len(result) > 0:
                # get_wallet_data returns: (balance, owner, jetton_master, jetton_wallet_code)
                balance = int(result[0])
                # Try different decimal places
                if balance > 1e9:
                    return balance / 1e9  # 9 decimals
                elif balance > 1e6:
                    return balance / 1e6  # 6 decimals
                else:
                    return balance
        except Exception:
            # Token wallet doesn't exist = 0 balance
            return 0
        return 0

    async def check_all_balances(self):
        """Check all token balances"""
        print("[BALANCES]")
        ton_balance = await self.get_ton_balance()
        print(f"  TON: {ton_balance:.4f}")

        for symbol, token_info in TEST_TOKENS.items():
            balance = await self.get_jetton_balance(token_info["address"])
            if balance > 0:
                print(f"  {symbol}: {balance:.4f}")
        print()

    async def send_transaction(self, destination: str, amount: float, payload):
        """Send a transaction"""
        try:
            await self.wallet.transfer(
                destination=destination,
                amount=int(amount * 1e9),
                body=payload,
            )
            print("[OK] Transaction sent")
            await asyncio.sleep(3)  # Wait for confirmation
            return True
        except Exception as e:
            print(f"[X] Transaction failed: {e}")
            return False

    async def test_dedust_swap(
        self, token_symbol: str, token_info: dict, amount: float = 0.1
    ):
        """Test DeDust swap: TON -> Token"""
        print(f"\n{'=' * 60}")
        print(f"[TEST] DeDust: {amount} TON -> {token_symbol}")
        print(f"{'=' * 60}")

        pool_address = token_info["pool"]
        token_address = token_info["address"]

        # Build DeDust swap payload according to TL-B schema
        # swap#ea06185d query_id:uint64 amount:Coins _:SwapStep swap_params:^SwapParams

        amount_nano = int(amount * 1e9)
        min_out = 1  # Minimal output requirement

        # Build SwapParams as reference
        # swap_params#_ deadline:Timestamp recipient_addr:MsgAddressInt referral_addr:MsgAddress
        #               fulfill_payload:(Maybe ^Cell) reject_payload:(Maybe ^Cell)
        swap_params = (
            begin_cell()
            .store_uint(0, 32)  # deadline (0 = no deadline)
            .store_address(self.wallet.address)  # recipient_addr
            .store_address(None)  # referral_addr (none)
            .store_uint(0, 1)  # fulfill_payload (Maybe = 0 = none)
            .store_uint(0, 1)  # reject_payload (Maybe = 0 = none)
            .end_cell()
        )

        # Build main swap payload
        # SwapStep is stored INLINE (not as reference)
        # step#_ pool_addr:MsgAddressInt params:SwapStepParams
        # step_params#_ kind:SwapKind limit:Coins next:(Maybe ^SwapStep)
        swap_payload = (
            begin_cell()
            .store_uint(0xEA06185D, 32)  # op::swap
            .store_uint(0, 64)  # query_id
            .store_coins(amount_nano)  # amount
            # SwapStep (inline):
            .store_address(Address(pool_address))  # pool_addr
            # SwapStepParams (inline):
            .store_uint(0, 1)  # kind: given_in (assuming 0 bit for given_in)
            .store_coins(min_out)  # limit (min output)
            .store_uint(0, 1)  # next: Maybe ^SwapStep (0 = none, no multi-hop)
            # swap_params as reference:
            .store_ref(swap_params)
            .end_cell()
        )

        # Send to DeDust Native Vault
        total_amount = amount + 0.25  # amount + gas
        print(f"[SEND] {total_amount} TON to DeDust Native Vault")
        print(f"[INFO] Pool: {pool_address}")
        print(f"[INFO] Min output: {min_out}")

        success = await self.send_transaction(
            destination=DEDUST_NATIVE_VAULT, amount=total_amount, payload=swap_payload
        )

        if success:
            print("[WAIT] Waiting 15 seconds for swap to complete...")
            await asyncio.sleep(15)

            # Check if we got tokens
            balance_after = await self.get_jetton_balance(token_address)
            print(f"[RESULT] {token_symbol} balance after swap: {balance_after:.4f}")

            if balance_after > 0:
                print(f"[SUCCESS] Got {token_symbol} tokens!")
                return True
            else:
                print(f"[FAILED] No {token_symbol} tokens received")
                return False

        return False

    async def run_tests(self):
        """Run all swap tests"""
        await self.connect()

        print("[START] Initial balances:")
        await self.check_all_balances()

        # Test only STON first (safest option)
        print("\n[INFO] Testing with STON token on DeDust...")
        print("[INFO] Using minimal amount (0.1 TON)")

        try:
            success = await self.test_dedust_swap(
                "STON", TEST_TOKENS["STON"], amount=0.1
            )

            if success:
                print("\n[OK] STON swap SUCCESSFUL! DeDust payload works!")
                print("[INFO] You can now test other tokens")
            else:
                print("\n[X] STON swap FAILED - checking transaction...")

            # Check balances after test
            await self.check_all_balances()

        except Exception as e:
            print(f"[X] Test error: {e}")
            import traceback

            traceback.print_exc()

        print("\n[DONE] Test completed")
        await self.client.close_all()


async def main():
    tester = SwapTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
