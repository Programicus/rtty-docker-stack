import asyncio
from aiomqtt import Client
import asyncpg
import os

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = os.environ.get('MQTT_TOPIC')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

async def handle_message(message, conn):
    await conn.execute('INSERT INTO Queue (from_addr, source, message, status) VALUES ($1, $2, $3, $4);', ('mqtt', 'mqtt', message.payload.decode(), 'QUEUED'))

async def main():
    conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host='db',
    )
    async with Client(MQTT_BROKER) as client:
        await client.subscribe(MQTT_TOPIC)
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                handle_message(message, conn)


asyncio.run(main())