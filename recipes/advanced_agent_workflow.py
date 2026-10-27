import asyncio
from browserbridge.engine import BrowserSession
from browserbridge.core.receipts_engine import DurableReceiptsEngine

async def main():
    receipts = DurableReceiptsEngine()
    session = BrowserSession(headless=True)
    await session.start()
    try:
        await session.navigate("https://example.com")
        receipt = receipts.record_action(action="navigate", target="https://example.com", status="success")
        print("Recorded durable action receipt:", receipt.receipt_id)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
