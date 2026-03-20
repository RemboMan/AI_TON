import asyncio
from pytoniq import LiteBalancer, WalletV5R1
from pytoniq_core import Address
import config


class TonWallet:
    def __init__(self):
        self.mnemonic = config.WALLET_MNEMONIC.split()
        self.wallet = None
        self.client = None

    async def connect(self):
        """Connect to TON network and initialize wallet"""
        # Try connecting with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client = LiteBalancer.from_mainnet_config(trust_level=2)
                await self.client.start_up()

                # Create wallet from mnemonic (WalletV5R1 for TonKeeper)
                self.wallet = await WalletV5R1.from_mnemonic(
                    self.client,
                    self.mnemonic,
                    network_global_id=-239,  # Mainnet
                )

                # Load wallet state from blockchain
                try:
                    account_state = await self.client.get_account_state(
                        self.wallet.address
                    )
                    balance = account_state.balance / 1e9

                    if account_state.state.type_ == "active":
                        print(f"[OK] Wallet connected: {self.wallet.address.to_str()}")
                    elif balance > 0:
                        print(
                            f"[!] Wallet has balance but not deployed: {self.wallet.address.to_str()}"
                        )
                        print(
                            f"    Balance: {balance:.4f} TON - Send a transaction to deploy it"
                        )
                    else:
                        print(
                            f"[!] Wallet not deployed: {self.wallet.address.to_str()}"
                        )
                        print("    Send some TON to this address to deploy it")
                except Exception as e:
                    print(f"[!] Could not verify wallet state: {e}")

                return  # Success

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[!] Connection attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2)
                else:
                    print(f"[X] Failed to connect after {max_retries} attempts: {e}")
                    raise

    async def get_balance(self):
        """Get current TON balance"""
        if not self.wallet:
            await self.connect()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get account state directly from blockchain
                account_state = await self.client.get_account_state(self.wallet.address)
                balance = account_state.balance
                return balance / 1e9  # Convert from nanotons
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    print(f"[!] Error getting balance: {e}")
                    return 0.0

    async def get_jetton_balance(
        self, jetton_master: str, token_name: str = None
    ) -> float:
        """Get balance of a specific jetton"""
        try:
            from pytoniq_core import begin_cell

            # Get jetton wallet address for this user
            payload = begin_cell().store_address(self.wallet.address).end_cell()

            result = await self.client.run_get_method(
                address=jetton_master,
                method="get_wallet_address",
                stack=[payload.begin_parse()],
            )

            jetton_wallet_address = result[0].load_address()

            # Get balance from jetton wallet
            balance_result = await self.client.run_get_method(
                address=jetton_wallet_address.to_str(),
                method="get_wallet_data",
                stack=[],
            )

            # get_wallet_data returns: balance, owner, jetton_master, jetton_wallet_code
            balance = balance_result[0]

            # Adjust for token decimals
            if token_name == "USDT":
                return int(balance) / 1e6  # USDT has 6 decimals
            elif token_name == "GOMINING":
                return int(balance) / 1e18  # GOMINING has 18 decimals
            else:
                return int(balance) / 1e9  # Most tokens have 9 decimals

        except Exception:
            # Token not found or no balance
            return 0.0

    async def get_all_balances(self):
        """Get TON and all jetton balances"""
        balances = {}

        # Get TON balance
        ton_balance = await self.get_balance()
        balances["TON"] = ton_balance

        # Get jetton balances
        for token_name, token_address in config.TOKENS.items():
            if token_name != "TON":
                try:
                    balance = await self.get_jetton_balance(token_address, token_name)
                    if balance > 0:
                        balances[token_name] = balance
                except:
                    pass

        return balances

    async def deploy_wallet(self):
        """Deploy wallet contract if not deployed"""
        if not self.wallet:
            await self.connect()

        account_state = await self.client.get_account_state(self.wallet.address)

        if account_state.state.type_ == "active":
            print("[OK] Wallet already deployed")
            return True

        balance = account_state.balance / 1e9
        if balance < 0.05:
            raise Exception(
                f"Insufficient balance to deploy: {balance:.4f} TON (need at least 0.05 TON)"
            )

        print("[!] Deploying WalletV5R1 contract...")

        try:
            # Use deploy_via_external for V5 wallets
            await self.wallet.deploy_via_external()
            print("[OK] Deployment transaction sent!")

            # Wait for deployment to complete
            print("    Waiting for confirmation...")
            await asyncio.sleep(5)

            # Verify deployment
            account_state = await self.client.get_account_state(self.wallet.address)
            if account_state.state.type_ == "active":
                print("[OK] Wallet deployed successfully!")
                return True
            else:
                print("[!] Wallet deployment pending, waiting longer...")
                await asyncio.sleep(5)
                account_state = await self.client.get_account_state(self.wallet.address)
                if account_state.state.type_ == "active":
                    print("[OK] Wallet deployed successfully!")
                    return True
                else:
                    raise Exception("Wallet deployment timed out")

        except Exception as e:
            raise Exception(f"Failed to deploy wallet: {e}")

    async def send_transaction(self, destination: str, amount: float, payload=None):
        """Send TON transaction"""
        if not self.wallet:
            await self.connect()

        # Check if wallet is deployed, deploy if needed
        account_state = await self.client.get_account_state(self.wallet.address)
        if account_state.state.type_ != "active":
            print("[!] Wallet not deployed, deploying first...")
            await self.deploy_wallet()
            # Refresh account state after deployment
            account_state = await self.client.get_account_state(self.wallet.address)

        # Check balance
        balance = account_state.balance / 1e9
        gas_reserve = 0.05

        if balance < amount + gas_reserve:
            raise Exception(
                f"Insufficient balance: {balance:.4f} TON (need {amount + gas_reserve:.4f} TON)"
            )

        amount_nano = int(amount * 1e9)
        dest_address = Address(destination)

        await self.wallet.transfer(
            destination=dest_address, amount=amount_nano, body=payload
        )
        print(f"[OK] Sent {amount} TON to {destination}")

    async def close(self):
        """Close connection"""
        if self.client:
            await self.client.close_all()
