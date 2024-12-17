from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apps.bot.handlers.commands import start_command
from apps.bot.models import User
from apps.bot.keyboards.inline import inline_languages
from apps.bot.utils.callback_data import (
    MainMenuCallbackData, MainMenuAction,
    BackToMainMenuCallbackData, BackToMainMenuAction, cb_back_to_main_menu_callback_data,
)

router = Router()


#
@router.callback_query(MainMenuCallbackData.filter(F.action == MainMenuAction.SETTINGS))
async def settings(callback_query: CallbackQuery):
    user = callback_query.from_user
    user_data = await User.objects.filter(telegram_id=user.id).afirst()

    if not user_data:
        await callback_query.message.edit_text(
            "Iltimos avval ro'yxatdan o'ting \nTilni tanlang:",
            reply_markup=inline_languages()  # inline_languages() tugmalari bilan til tanlash
        )
        return

    lang = user_data.language
    language = "O'zbek" if lang == "uz" else "Русский" if lang == "ru" else "English"

    await callback_query.message.edit_text(
        f"<b>Muloqot tili: </b>{language}\n",
        parse_mode="HTML",
        reply_markup=inline_settings()
    )


def inline_settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🌐 Muloqot tili", callback_data="change_language")
    keyboard.button(text="🏠 Asosiy menyu",
                    callback_data=cb_back_to_main_menu_callback_data(
                        action=BackToMainMenuAction.BACK).pack())  # pack() qo'shilgan
    keyboard.adjust(1)
    return keyboard.as_markup()


def inline_languages():  # "inline_languages" nomi to'g'ri bo'lishi kerak
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🇺🇿 O'zbek", callback_data="set_language:uz")
    keyboard.button(text="🇷🇺 Русский", callback_data="set_language:ru")
    keyboard.button(text="🇬🇧 English", callback_data="set_language:en")
    keyboard.adjust(1)
    return keyboard.as_markup()


@router.callback_query(F.data == "change_language")
async def change_language(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "🌐 Tilni tanlang:",
        reply_markup=inline_languages()  # inline_languages()ni chaqirish
    )


# Tilni o'zgartirish
@router.callback_query(lambda c: c.data.startswith("set_language"))
async def set_language(callback: CallbackQuery):
    language_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    user = await User.objects.filter(telegram_id=user_id).afirst()
    if not user:
        await callback.answer("⚠️ Ro'yxatdan o'tmagansiz. Til tanlandi.", show_alert=True)
        return

    user.language = language_code
    await user.asave()

    text = "✅ Til muvaffaqiyatli O'zbek tiliga o'zgartirildi." if language_code == "uz" else \
        "✅ Язык успешно изменён на Русский." if language_code == "ru" else \
            "✅ Language successfully changed to English."
    await callback.message.edit_text(text=text,
                                     reply_markup=inline_settings())  # inline_settings() bilan qayta tahrirlash
