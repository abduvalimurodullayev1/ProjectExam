from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from aiogram.utils.i18n import gettext as _  # Import gettext for translation

from apps.bot.models import CarModel, CarBrand
from apps.bot.utils.callback_data import cb_main_menu_callback_data, MainMenuAction, cb_select_language_callback_data, \
    SelectLanguage, cb_back_to_main_menu_callback_data, select_active_menu_callback_data, DetectionActiveMainMenuAction, \
    create_detection_callback_data, CreateDetectionAction, CreateDetectionCallbackData, BackToMainMenuAction, \
    SelectLanguageCallbackData


def inline_main_menu():
    inline_keyboard = InlineKeyboardBuilder()

    inline_keyboard.button(text=_('🗞Yangi detektsiya yaratish.'),
                           callback_data=cb_main_menu_callback_data(action=MainMenuAction.CREATE_DETECTION))
    inline_keyboard.button(text=_('🔄Faol detektsiyalar'),
                           callback_data=cb_main_menu_callback_data(action=MainMenuAction.ACTIVE))
    inline_keyboard.button(text=_('⚙️Sozlamalar'),
                           callback_data=cb_main_menu_callback_data(action=MainMenuAction.SETTINGS))

    inline_keyboard.adjust(2)

    return inline_keyboard.as_markup()


def inline_languages():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text="O'zbek", callback_data=SelectLanguageCallbackData(language="uz").pack()
    )
    inline_keyboard.button(
        text="Русский", callback_data=SelectLanguageCallbackData(language="ru").pack()
    )
    inline_keyboard.button(
        text="English", callback_data=SelectLanguageCallbackData(language="en").pack()
    )
    return inline_keyboard.as_markup()


def inline_settings():
    inline_keyboard = InlineKeyboardBuilder()

    inline_keyboard.button(text=_("Muloqot tili"), callback_data='settings')
    inline_keyboard.button(text=_("Telefon"), callback_data='phone')
    inline_keyboard.button(text=_("Asosiy menu"),
                           callback_data=cb_back_to_main_menu_callback_data(BackToMainMenuAction.BACK))
    inline_keyboard.adjust(3)

    return inline_keyboard.as_markup()


def create_detection_keyboard(detection):
    inline = InlineKeyboardBuilder()

    if detection.is_active:
        inline.button(
            text=_("❌ Faolsizlantirish"),
            callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.DEACTIVATED, detection.id)
        )
    else:
        inline.button(
            text=_("✅ Faol qilish"),
            callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.ACTIVE, detection.id)
        )

    inline.button(
        text=_("🔧 Filtrlarni o'zgartirish"),
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.FILTER, detection.id)
    )

    inline.button(
        text=_("📊 Hisobot"),
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.REPORT, detection.id)
    )

    inline.button(
        text=_("🗑 O'chirish"),
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.DELETED, detection.id)
    )

    inline.adjust(1)

    return inline


def build_color_keyboard():
    colors = ['Черный', 'белый', 'Красный', 'Я в порядке', 'Зеленый']
    builder = InlineKeyboardBuilder()
    for color in colors:
        builder.button(text=color, callback_data=f"color:{color}")
    builder.button(text=_("✅ Tanlashni tugatish"), callback_data="color:done")
    return builder.as_markup()


def get_price_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    prices = ['0-3,000 y.e', '4,000 y.e-21,000 y.e']
    for price in prices:
        kb.button(text=price, callback_data=f"price:{price}")
    kb.button(text=_("✅ Tanlashni tugatish"), callback_data="price:done")
    return kb.as_markup()


async def build_models_keyboard(brand):
    models = await sync_to_async(get_models_for_brand)(brand)
    builder = InlineKeyboardBuilder()
    for model in models:
        builder.button(text=model, callback_data=f"model:{model}")

    return builder.as_markup()


async def build_brands_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    async for brand in CarBrand.objects.all():
        keyboard_builder.button(
            text=brand.name,
            callback_data=CreateDetectionCallbackData(
                action=CreateDetectionAction.ACTIVE,
                brand_id=brand.id,
                model_id=None
            ).pack()
        )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


@sync_to_async
def get_models_for_brand_sync(brand_id: int):
    return list(CarModel.objects.filter(brand_id=brand_id))


async def get_models_for_brand(brand_id: int):
    models = await get_models_for_brand_sync(brand_id)
    keyboard_builder = InlineKeyboardBuilder()

    for model in models:
        keyboard_builder.button(
            text=model.name,
            callback_data=CreateDetectionCallbackData(
                action=CreateDetectionAction.FILTER,
                brand_id=brand_id,
                model_id=model.id
            ).pack()
        )

    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


def get_mileage_keyboard():
    builder = InlineKeyboardBuilder()
    options = [
        (_("0-10 ming km"), "mileage:0-10"),
        (_("10-50 ming km"), "mileage:10-50"),
        (_("50-100 ming km"), "mileage:50-100"),
        (_("100 ming km+"), "mileage:100+")
    ]
    for text, callback_data in options:
        builder.button(text=text, callback_data=callback_data)
    builder.button(text=_("✅ Tamom"), callback_data="mileage:done")
    builder.adjust(2)
    return builder.as_markup()


import logging

logger = logging.getLogger(__name__)


def inline_after_detection(detection):
    inline = InlineKeyboardBuilder()
    inline.button(
        text=_('🔎 Filtrlarni ishga tushrish'),
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.FILTER, detection.id)
    )
    inline.button(
        text=_('Deteksiyani ishga tushurish'),
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.RUN_DETECTION, detection.id)
    )
    inline.button(
        text=_('Ortga'),
        callback_data=cb_back_to_main_menu_callback_data(BackToMainMenuAction.BACK)
    )
    logger.info('Inline klaviatura yaratildi.')
    return inline.as_markup()

def inline_back_to_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("🔙 Asosiy menu"),
        callback_data=cb_back_to_main_menu_callback_data(BackToMainMenuAction.BACK)
    )
    return builder.as_markup()
