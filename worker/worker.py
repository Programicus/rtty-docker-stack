import asyncio
import os
import signal
import asyncpg
import interop

async def listen_for_notifications(conn, queued_count):
    def increment_queued_count(*args):
        nonlocal queued_count
        queued_count += 1

    await conn.add_listener('new_queue_entry', increment_queued_count)

async def process_existing_pending(conn, lock):
    async with conn.transaction():
        rows = await conn.fetch("""
            SELECT * FROM Queue
            WHERE status = 'PRINTING'
            ORDER BY timestamp
            FOR UPDATE SKIP LOCKED
        """)

        for row in rows:
            interop.process_row(conn, row, lock)
        
        queued_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM Queue
            WHERE status = 'QUEUED'
        """)

    return queued_count

async def process_row(conn, lock):
    async with conn.transaction():
        row = await conn.fetchrow("""
            SELECT * FROM Queue
            WHERE status = 'QUEUED'
            ORDER BY timestamp
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        """)

        if row:
            await do_some.work(conn, row, lock)

async def main():
    try:
        conn = await asyncpg.connect(
            user=os.environ.get('POSTGRES_USER', 'defaultuser'),
            password=os.environ.get('POSTGRES_PASSWORD', 'defaultpassword'),
            database=os.environ.get('POSTGRES_DB', 'defaultdatabase'),
            host='db'
        )

        await conn.execute("""
            PREPARE mark_done AS
            UPDATE Queue
            SET status = 'FINISHED'
            WHERE timestamp = $1
        """)

        await conn.execute("""
            PREPARE mark_printing AS
            UPDATE Queue
            SET status = 'PRINTING'
            WHERE timestamp = $1
        """)

        # Create a lock to ensure only one process_row runs at a time
        lock = asyncio.Lock()

        # First handle existing pending rows and get the count of queued rows
        queued_count = await process_existing_pending(conn, lock)
        print(f"Number of rows marked as QUEUED: {queued_count}")


        # Then set up the listener for new rows
        await listen_for_notifications(conn, queued_count)

        while True:
            if queued_count > 0:
                await process_row(conn, lock)
                queued_count -= 1
            else:
                await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Worker has been cancelled")
    finally:
        await conn.close()
        print("Worker has shut down gracefully")

def shutdown(loop):
    print("Received shutdown signal")
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()