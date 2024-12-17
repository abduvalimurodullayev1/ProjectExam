from django.db import models
from solo.models import SingletonModel
from django.utils.translation import gettext_lazy as _


# from apps.bot.models import CarBrand, CarModel


class TelegramBotConfiguration(SingletonModel):
    bot_token = models.CharField(max_length=255, default='token')
    secret_key = models.CharField(max_length=255, default='secret_key')
    webhook_url = models.URLField(max_length=255, default='https://api.telegram.org/')
    admin = models.IntegerField(default=1235678)


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    language = models.CharField(max_length=10, default='en')
    phone_number = models.CharField(max_length=16)
    name = models.CharField(max_length=255)
    last_active_at = models.DateTimeField(null=True, blank=True)
    detections_count = models.PositiveIntegerField(default=0)

    def str(self):
        return self.name


class CarListing(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    color = models.CharField(max_length=50, null=True, blank=True)  # Rang
    image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brand = models.CharField(max_length=122)
    model = models.CharField(max_length=122)
    mileage = models.CharField(max_length=50, null=True, blank=True)  # Masofa


    def str(self):
        return self.title


class CarImage(models.Model):
    car_listing = models.ForeignKey(CarListing, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()


class Detection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="detection")
    brand = models.ForeignKey(
        "CarBrand", on_delete=models.CASCADE, verbose_name=_("Car brand")
    )
    model = models.ForeignKey(
        "CarModel", on_delete=models.CASCADE, verbose_name=_("Model")
    )
    filters = models.JSONField(default=dict, blank=True)
    color = models.CharField(_("Color"), max_length=50, blank=True, null=True)
    year_from = models.PositiveIntegerField(blank=True, null=True)
    year_to = models.PositiveIntegerField(blank=True, null=True)
    mileage_from = models.PositiveIntegerField(blank=True, null=True)
    mileage_to = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Detektsiya {self.id} ({'Faol' if self.is_active else 'Faol emas'})"


class TaskLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Bajarildi'),
        ('failed', 'Xato'),
    ]
    detection = models.ForeignKey('Detection', on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task {self.id} ({self.get_status_display()})"


class CarBrand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
