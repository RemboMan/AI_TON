import asyncio
from market_data import MarketData


async def view_markets():
    """View current market data from DEXes"""
    print("TON DEX Market Overview\n")
    print("=" * 80)

    market = MarketData()
    await market.init_session()

    try:
        # Get DeDust pools
        print("\n[DeDust Pools]")
        print("-" * 80)
        dedust_pools = await market.get_dedust_pools()

        if dedust_pools:
            for i, pool in enumerate(dedust_pools[:10], 1):
                print(f"\n{i}. Pool: {pool.get('address', 'N/A')}")
                print(f"   Assets: {pool.get('assets', 'N/A')}")
                print(f"   Reserves: {pool.get('reserves', 'N/A')}")
        else:
            print("   No pools data available")

        # Get STON.fi pools
        print("\n\n[STON.fi Pools]")
        print("-" * 80)
        stonfi_pools = await market.get_stonfi_pools()

        if stonfi_pools:
            for i, pool in enumerate(stonfi_pools[:10], 1):
                print(f"\n{i}. Pool: {pool.get('address', 'N/A')}")
                print(f"   Token0: {pool.get('token0_address', 'N/A')}")
                print(f"   Token1: {pool.get('token1_address', 'N/A')}")
                print(f"   LP Supply: {pool.get('lp_total_supply', 'N/A')}")
        else:
            print("   No pools data available")

        print("\n" + "=" * 80)
        print(f"\n[OK] Total DeDust pools: {len(dedust_pools)}")
        print(f"[OK] Total STON.fi pools: {len(stonfi_pools)}")

    except Exception as e:
        print(f"\n[X] Error fetching market data: {e}")
    finally:
        await market.close_session()


if __name__ == "__main__":
    asyncio.run(view_markets())
