from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.users.manager import UserManager


class User(AbstractUser):
    username = None
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('banned', _('Banned')),
    ]

    class Language(models.TextChoices):
        UZ = "uz", _("Uzbek")
        EN = "en", _("English")
        RU = "ru", _("Russian")

    phone_number = models.CharField(max_length=20, verbose_name=_("Phone number"), unique=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    telegram_id = models.BigIntegerField(verbose_name=_("Telegram ID"), null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name=_("Status"))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined"))
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.UZ, verbose_name=_("Language"))
    statistics = models.JSONField(default=dict, verbose_name=_("Statistics"))
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

