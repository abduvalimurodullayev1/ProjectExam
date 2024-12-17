from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def reply_send_phone_number():
    reply_keyboard = ReplyKeyboardBuilder()

    reply_keyboard.button(text="Send phone", request_contact=True)

    return reply_keyboard.as_markup(resize_keyboard=True)
