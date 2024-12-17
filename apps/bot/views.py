import json
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from aiogram import Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from apps.bot.config.bot import dp


class TelegramWebhook(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        bot = Bot(token='7686619121:AAEUTTGCO6gd5BLUXqzLJOqwgoCRztuIhGI',
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        try:
            data = json.loads(request.body)
            print(data)
            await dp.feed_update(bot=bot, update=types.Update(**data))
        except json.JSONDecodeError:
            print('error')
            return HttpResponse("Invalid JSON", status=400)
        return HttpResponse('Webhook updated successfully')
