import asyncio
import os
import signal
import asyncpg
import interop

import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def listen_for_notifications(conn, queued_count):
    def increment_queued_count(*args):
        nonlocal queued_count
        old_count = queued_count
        queued_count += 1
        logger.info(f'raising queued_count from {old_count} to {queued_count}')

    logger.info('about to create listener')
    await conn.add_listener('new_queue_entry', increment_queued_count)
    logger.info('created listener')

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
    logger.info('process_row')
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
    logger.info('starting worker')
    try:
        user = os.environ.get('POSTGRES_USER', 'defaultuser')
        password = os.environ.get('POSTGRES_PASSWORD', 'defaultpassword')
        database = os.environ.get('POSTGRES_DB', 'defaultdatabase')
        logger.info(f'connecting to {database} with user {user}')
        logger.debug(f'with password {password}') #if you are can see this log message then you already have access to the docker container
        
        #HACKY:add delay for pg to finish spinning up
        #TODO: find a better way
        logger.info('starting delay waiting for pg to be ready')
        await asyncio.sleep(15)
        
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host='db',
            loop=loop
        )
    except Exception as e:
        logger.error(f'Failed to connect to db {e}')
        return

    try:
        logger.info('connection created')

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

        logger.info('created prepared statements')

        # Create a lock to ensure only one process_row runs at a time
        lock = asyncio.Lock()

        # First handle existing pending rows and get the count of queued rows
        queued_count = await process_existing_pending(conn, lock)
        logger.info(f"Number of rows marked as QUEUED: {queued_count}")


        # Then set up the listener for new rows
        await listen_for_notifications(conn, queued_count)

        while True:
            if queued_count > 0:
                await process_row(conn, lock)
                queued_count -= 1
            else:
                await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.warn("Worker has been cancelled")
    finally:
        await conn.close()
        logger.info("Worker has shut down gracefully")

def shutdown(loop):
    logger.info("Received shutdown signal")
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