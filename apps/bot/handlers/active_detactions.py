from aiogram import types, F
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db import transaction, DatabaseError
from apps.bot.utils.callback_data import MainMenuCallbackData, MainMenuAction, select_active_menu_callback_data, \
    DetectionActiveMainMenuAction, ActiveMainMenuCallbackData
from apps.bot.models import Detection

router = Router()


def create_detection_keyboard(detection):
    inline = InlineKeyboardBuilder()
    if detection.is_active:
        inline.button(
            text="❌ Faolsizlantirish",
            callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.DEACTIVATED, detection.id)
        )
    else:
        inline.button(
            text="✅ Faol qilish",
            callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.ACTIVE, detection.id)
        )
    inline.button(
        text="🗑 O'chirish",
        callback_data=select_active_menu_callback_data(DetectionActiveMainMenuAction.DELETED, detection.id)
    )
    inline.adjust(1)
    return inline


# Deteksiyani yangilash va saqlash uchun yordamchi funksiya
@sync_to_async
def update_detection_status(detection_id, is_active=None, delete=False):
    try:
        with transaction.atomic():
            detection = Detection.objects.select_related('brand', 'model').get(id=detection_id)
            if delete:
                detection.delete()
                return True
            elif is_active is not None:
                detection.is_active = is_active
                detection.save(update_fields=['is_active'])
                return detection
    except Detection.DoesNotExist:
        return None


# Deteksiya olish uchun helper funksiya
@sync_to_async
def get_user_detections(telegram_id):
    return list(Detection.objects.filter(user__telegram_id=telegram_id).select_related('brand', 'model'))


@router.callback_query(MainMenuCallbackData.filter(F.action == MainMenuAction.ACTIVE))
async def main_menu_callback(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    detections = await get_user_detections(telegram_id)

    if not detections:
        await callback_query.message.edit_text("❌ Sizning faol deteksiyalaringiz topilmadi.")
        return

    for detection in detections:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Nomalum'}\n"
            f"📅 Yil: {detection.year_from or 'Nomalum'} - {detection.year_to or 'Nomalum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)

        await callback_query.message.answer(
            detection_details,
            reply_markup=inline_keyboard.as_markup()
        )

    await callback_query.message.edit_text("📝 Sizning deteksiyalaringiz ro'yxati.")


# Callback funksiyasi: Faollashtirish
@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.ACTIVE))
async def activate_detection(callback_query: types.CallbackQuery, callback_data: MainMenuCallbackData):
    detection = await update_detection_status(callback_data.id, is_active=True)

    if detection:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Nomalum'}\n"
            f"📅 Yil: {detection.year_from or 'Nomalum'} - {detection.year_to or 'Nomalum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)
        await callback_query.message.edit_text(
            f"✅ Deteksiya faollashtirildi!\n{detection_details}",
            reply_markup=inline_keyboard.as_markup()
        )
    else:
        await callback_query.answer("❌ Deteksiya topilmadi.")


# Callback funksiyasi: Faolsizlantirish
@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.DEACTIVATED))
async def deactivate_detection(callback_query: types.CallbackQuery, callback_data: MainMenuCallbackData):
    detection = await update_detection_status(callback_data.id, is_active=False)

    if detection:
        detection_details = (
            f"🆔 ID: {detection.id}\n"
            f"🚗 Brande: {detection.brand.name}\n"
            f"🚗 Modeli: {detection.model.name}\n"
            f"🎨 Rang: {detection.color or 'Nomalum'}\n"
            f"📅 Yil: {detection.year_from or 'Nomalum'} - {detection.year_to or 'Nomalum'}"
        )
        inline_keyboard = create_detection_keyboard(detection)
        await callback_query.message.edit_text(
            f"❌ Deteksiya faolsizlantirildi!\n{detection_details}",
            reply_markup=inline_keyboard.as_markup()
        )
    else:
        await callback_query.answer("❌ Deteksiya topilmadi.")


@router.callback_query(ActiveMainMenuCallbackData.filter(F.action == DetectionActiveMainMenuAction.DELETED))
async def delete_detection(callback_query: types.CallbackQuery, callback_data: ActiveMainMenuCallbackData):
    detection_id = callback_data.id
    print(f"Tulayotgan detection_id: {detection_id}")

    # Deteksiyani o'chirish
    detection = await update_detection_status(detection_id, delete=True)

    if detection:
        await callback_query.message.edit_text(
            "✅ Deteksiya muvaffaqiyatli o'chirildi!",
            reply_markup=None
        )
    else:
        await callback_query.answer("❌ Deteksiya topilmadi yoki o'chirishda xato yuz berdi.")

    print(f"Detection o'chirildi: {detection}")
