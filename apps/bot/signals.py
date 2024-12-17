import requests
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.cache import cache
from apps.bot.models import TelegramBotConfiguration, User


@receiver(pre_save, sender=TelegramBotConfiguration)
def update_bot_webhook_url(sender, instance, **kwargs):
    try:
        existing_object = sender.objects.get(pk=instance.pk)
        if existing_object.webhook_url != instance.webhook_url:
            telegram_webhook_url = f'https://api.telegram.org/bot{instance.bot_token}/setWebhook?url={instance.webhook_url}'
            return requests.get(url=telegram_webhook_url)
    except TelegramBotConfiguration.DoesNotExist:
        pass

import requests
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.core.cache import cache

from apps.bot.models import TelegramBotConfiguration, User


@receiver(pre_save, sender=TelegramBotConfiguration)
def update_bot_webhook_url(sender, instance, **kwargs):
    try:
        existing_object = sender.objects.get(pk=instance.pk)
        if existing_object.webhook_url != instance.webhook_url:
            telegram_webhook_url = f'https://api.telegram.org/bot{instance.bot_token}/setWebhook?url={instance.webhook_url}'
            return requests.get(url=telegram_webhook_url)
    except TelegramBotConfiguration.DoesNotExist:
        pass


@receiver(pre_save, sender=User)
def update_user_language_in_cache(sender, instance, **kwargs):
    user = sender.objects.filter(telegram_id=instance.telegram_id).first()
    if user and user.language != instance.language:
        cache.set('user_language', instance.language)
