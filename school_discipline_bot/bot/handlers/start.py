from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.keyboards.main_menu import main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    This handler will be called when user sends `/start` command.
    It sends a welcome message and the main menu keyboard.
    """
    text = (
        f"Hello, {message.from_user.full_name}!\n\n"
        "Welcome to the School Discipline Bot. "
        "Click the button below to open the application."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())
