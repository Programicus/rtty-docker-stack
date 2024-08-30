import asyncio

async def process_row(conn, row, lock):
    async with lock:
        # Simulate processing the row
        print(f"Processing row: {row['source']}, {row['message']}")
        await conn.execute("""
            EXECUTE mark_printing($1)
        """, row['timestamp'])

        await asyncio.sleep(5)  # Simulate work

        await conn.execute("""
            EXECUTE mark_done($1)
        """, row['timestamp'])

        print(f"Finished processing row: {row['source']}, {row['message']}")