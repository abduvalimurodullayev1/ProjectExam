from typing import Dict, Any
from aiogram.types.base import TelegramObject
from aiogram.utils.i18n import I18nMiddleware
from aiogram import types
from asgiref.sync import sync_to_async
from django.core.cache import cache

from apps.bot.models import User

EVENT_FROM_USER = 'event_from_user'


class CustomI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]):
        user: types.User = data.get(EVENT_FROM_USER)

        if not user:
            return self.i18n.default_locale

        telegram_id = user.id

        cache_key = f"user_language_{telegram_id}"
        user_language = cache.get(cache_key)

        if not user_language:
            user_obj = await User.objects.filter(telegram_id=telegram_id).afirst()
            if user_obj and user_obj.language:
                user_language = user_obj.language
                await sync_to_async(cache.set)(cache_key, user_language, timeout=3600)
            else:
                user_language = self.i18n.default_locale

        return user_language
