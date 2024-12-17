from django.urls import path

from apps.bot.views import TelegramWebhook

app_name = "bot"
urlpatterns = [
    path('webhook/', TelegramWebhook.as_view(), name='telegram-webhook')
]
