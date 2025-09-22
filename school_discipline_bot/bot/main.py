import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided. Set it in the .env file.")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    This handler will be called when a user sends the /start command
    """
    await message.reply("Hi!\nI'm the School Discipline Bot!\nPowered by aiogram.")


async def main():
    """Start the bot."""
    # This will skip any updates that were received while the bot was offline
    await bot.delete_webhook(drop_pending_updates=True)
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())
