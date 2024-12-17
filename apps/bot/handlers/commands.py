from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _  # Import gettext for translation

from apps.bot.keyboards.inline import inline_main_menu, inline_languages
from apps.bot.middlewares import CheckRegistrationMiddleware
from apps.bot.utils.states import MenuStateGroup

router = Router()


@router.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer(_("Quyidagilardan birini tanlang"), reply_markup=inline_main_menu())


@router.message(Command('help'))
async def help_command(message: types.Message):
    await message.answer(_("Available commands:\n/start - Start the bot\n/help - Get help"))