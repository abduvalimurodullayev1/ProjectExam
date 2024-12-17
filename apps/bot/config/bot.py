from apps.bot.config import config
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio.client import Redis

from apps.bot.handlers import setup_handlers
from apps.bot.middlewares import setup_middlewares
from apps.bot.middlewares.i18n_middleware import CustomI18nMiddleware

redis = Redis.from_url(config.REDIS_URL)

dp = Dispatcher(storage=RedisStorage(redis=redis))
#
# # I18n sozlamalarini o'rnatish
i18n = I18n(path="locales", default_locale="en", domain="messages")
i18n_middleware = CustomI18nMiddleware(i18n=i18n)

# I18n Middleware-ni sozlash
i18n_middleware.setup(dp)

# Middleware va handlerlarni sozlash
setup_middlewares(dp)
setup_handlers(dp)
