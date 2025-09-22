import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import start, admin, teacher, student

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """Start the bot."""
    # Get token from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("No BOT_TOKEN provided. Set it in the .env file.")

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Include routers from handler files
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(teacher.router)
    dp.include_router(student.router)

    # This will skip any updates that were received while the bot was offline
    await bot.delete_webhook(drop_pending_updates=True)
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())
