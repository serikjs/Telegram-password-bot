import logging
import asyncio
from aiogram import types

async def delete_message_after_delay(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logging.info(f"Could not delete message: {e}")