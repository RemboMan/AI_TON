import asyncio
from wallet import TonWallet


async def check_balance():
    """Quick script to check wallet balance"""
    print("Checking TON Wallet Balance...\n")

    try:
        wallet = TonWallet()
        await wallet.connect()

        balance = await wallet.get_balance()

        print(f"Wallet Address: {wallet.wallet.address.to_str()}")
        print(f"Balance: {balance:.4f} TON")
        print(f"Balance (nanotons): {int(balance * 1e9)}")

        await wallet.close()

    except Exception as e:
        print(f"[X] Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_balance())
