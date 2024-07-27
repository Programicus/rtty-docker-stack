import asyncio
import os
import signal
import psycopg2

running = True

async def main():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'defaultdatabase'),
        user=os.environ.get('POSTGRES_USER', 'defaultuser'),
        password=os.environ.get('POSTGRES_PASSWORD', 'defaultpassword'),
        host='db'
    )
    cursor = conn.cursor()
    
    while running:
        cursor.execute("SELECT 1")
        print("Worker is running and connected to the database")
        await asyncio.sleep(1)

    cursor.close()
    conn.close()
    print("Worker has shut down gracefully")

def shutdown(signal, frame):
    global running
    print("Received shutdown signal")
    running = False

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    asyncio.run(main())
