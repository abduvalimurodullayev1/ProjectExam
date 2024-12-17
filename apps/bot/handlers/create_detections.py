from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as tr
from apps.bot.task import scrape_and_save_listings
from apps.bot.utils.callback_data import (
    CreateDetectionCallbackData,
    CreateDetectionAction,
    ActiveMainMenuCallbackData,
    DetectionActiveMainMenuAction,
    MainMenuAction, MainMenuCallbackData, BackToMainMenuCallbackData, BackToMainMenuAction
)
from apps.bot.keyboards.inline import (
    build_brands_keyboard,
    get_models_for_brand,
    build_color_keyboard,
    get_mileage_keyboard,
    inline_after_detection
)
from apps.bot.models import CarBrand, CarModel, Detection, User
from apps.bot.utils.states import MenuStateGroup

router = Router()


@router.callback_query(MainMenuCallbackData.filter(F.action == MainMenuAction.CREATE_DETECTION))
async def create_detection_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    brand_keyboard = await build_brands_keyboard()
    await callback.message.edit_text(
        text=tr("🔍 Qaysi avtomobil brendini tanlaysiz?"),
        reply_markup=brand_keyboard
    )
    await state.set_state(MenuStateGroup.select_brand)


@router.callback_query(MenuStateGroup.select_brand,
                       CreateDetectionCallbackData.filter(F.action == CreateDetectionAction.ACTIVE))
async def handle_select_brand(callback: CallbackQuery, callback_data: CreateDetectionCallbackData, state: FSMContext):
    brand_id = callback_data.brand_id
    await state.update_data(brand_id=brand_id)
    model_keyboard = await get_models_for_brand(brand_id)
    await callback.message.edit_text(
        text=tr("🚗 Qaysi modelni tanlaysiz?"),
        reply_markup=model_keyboard
    )
    await state.set_state(MenuStateGroup.select_model)


@router.callback_query(MenuStateGroup.select_model,
                       CreateDetectionCallbackData.filter(F.action == CreateDetectionAction.FILTER))
async def handle_select_model(callback: CallbackQuery, callback_data: CreateDetectionCallbackData, state: FSMContext):
    model_id = callback_data.model_id
    await state.update_data(model_id=model_id)

    data = await state.get_data()
    telegram_user_id = callback.from_user.id
    user, _ = await User.objects.aget_or_create(telegram_id=telegram_user_id)

    brand_id = data.get("brand_id")
    model_id = data.get("model_id")
    brand = await CarBrand.objects.aget(id=brand_id)
    model = await CarModel.objects.aget(id=model_id)

    detection = await Detection.objects.acreate(
        user=user,
        brand=brand,
        model=model,
        filters={}
    )

    await callback.message.answer(text=tr("Quyidagilardan birini tanlang"),
                                  reply_markup=inline_after_detection(detection))


@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.RUN_DETECTION))
async def run_detection(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    telegram_user_id = callback_query.from_user.id
    user, _ = await User.objects.aget_or_create(telegram_id=telegram_user_id)

    brand_id = data.get("brand_id")
    model_id = data.get("model_id")
    brand = await CarBrand.objects.aget(id=brand_id)
    model = await CarModel.objects.aget(id=model_id)
    detection = await Detection.objects.acreate(
        user=user,
        brand=brand,
        model=model,
        filters={}
    )

    scrape_and_save_listings.delay(detection.id)

    await callback_query.message.edit_text(
        text=tr("✅ Yangi detektsiya yaratildi:\n"
                "🔹 **Brend**: {brand}\n"
                "🔹 **Model**: {model}\n"
                "🔹 Ma'lumotlar yig'ilmoqda...").format(brand=brand.name, model=model.name)
    )


@router.callback_query(MenuStateGroup.select_model,
                       CreateDetectionCallbackData.filter(F.action == CreateDetectionAction.FILTER))
async def handle_select_model(callback: CallbackQuery, callback_data: CreateDetectionCallbackData, state: FSMContext):
    model_id = callback_data.model_id
    await state.update_data(model_id=model_id)
    await callback.message.edit_text(
        text=tr("🔧 Filtrlarni tanlang:"),
        reply_markup=inline_after_detection()
    )


@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.FILTER))
async def filter_options(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text=tr("🟦 Mashinaning rangini tanlang:"),
        reply_markup=build_color_keyboard()
    )
    await state.set_state(MenuStateGroup.select_color)


@router.callback_query(MenuStateGroup.select_color)
async def handle_color(callback: CallbackQuery, state: FSMContext):
    color = callback.data.split(":")[1]
    if color == "done":
        await callback.message.answer(tr("📏 Yurgan masofa oralig'ini tanlang:"), reply_markup=get_mileage_keyboard())
        await state.set_state(MenuStateGroup.set_mileage)
    else:
        await state.update_data(color=color)
        await callback.answer(tr("{} tanlandi!").format(color))


@router.callback_query(MenuStateGroup.set_mileage)
async def handle_mileage(callback: CallbackQuery, state: FSMContext):
    mileage = callback.data.split(":")[1]
    if mileage == "done":
        await callback.message.answer(tr("📅 Yilni kiriting (masalan: 2010-2020):"))
        await state.set_state(MenuStateGroup.select_year)
    else:
        await state.update_data(mileage=mileage)
        await callback.answer(tr("{} oraligi tanlandi!").format(mileage))


from django.core.exceptions import ObjectDoesNotExist


@router.message(MenuStateGroup.select_year)
async def handle_year(message: types.Message, state: FSMContext):
    year = message.text
    await state.update_data(year=year)
    user_data = await state.get_data()

    color = user_data.get("color", "").lower()
    mileage = user_data.get("mileage", "")
    year_range = user_data.get("year", "")
    brand_id = user_data.get("brand_id")
    model_id = user_data.get("model_id")

    try:
        brand = await CarBrand.objects.aget(id=brand_id)
    except CarBrand.DoesNotExist:
        await message.answer(tr("❌ Brend topilmadi. Iltimos, qayta urinib ko'ring."))
        await state.clear()
        return

    try:
        model = await CarModel.objects.aget(id=model_id)
    except CarModel.DoesNotExist:
        await message.answer(tr("❌ Model topilmadi. Iltimos, qayta urinib ko'ring."))
        await state.clear()
        return

    telegram_user_id = message.from_user.id
    user, _ = await User.objects.aget_or_create(telegram_id=telegram_user_id)

    detection = await Detection.objects.acreate(
        user=user,
        brand=brand,
        model=model,
        filters={
            "mileage": mileage,
            "year": year_range
        },
        color=color,
    )

    scrape_and_save_listings.delay(detection.id)

    await message.answer(
        text=tr("✅ Detektsiya yaratildi:\n"
                "🔹 Brend: {brand}\n"
                "🔹 Model: {model}\n"
                "🔹 Filtrlar: Rang - {color}, Masofa - {mileage}, Yil - {year}\n"
                "🕵️ Ma'lumotlar yig'ilmoqda...").format(
            brand=brand.name, model=model.name, color=color, mileage=mileage, year=year_range
        )
    )

    await state.clear()
