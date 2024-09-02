import asyncio

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_mark_done = None
_mark_printing = None

async def prepare_statements(conn):
    global _mark_done
    global _mark_printing
    _mark_done = await conn.prepare("""
        UPDATE Queue
        SET status = 'FINISHED'
        WHERE timestamp = $1
    """)

    _mark_printing = await conn.prepare("""
        UPDATE Queue
        SET status = 'PRINTING'
        WHERE timestamp = $1
    """)


async def process_row(conn, row, lock):
    global _mark_done
    global _mark_printing
    async with lock:
        # Simulate processing the row
        logger.info(f"Processing row: {row['source']}, {row['message']}")
        logger.info(row)
        await _mark_printing.fetch(row['timestamp'])

        await asyncio.sleep(5)  # Simulate work

        await _mark_done.fetch(row['timestamp'])

        logger.info(f"Finished processing row: {row['source']}, {row['message']}")