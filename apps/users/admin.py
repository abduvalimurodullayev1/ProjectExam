from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User
from ..bot.models import Detection, CarListing, CarBrand, CarModel


# Registering Models to Admin Site
admin.site.register(User)
# admin.site.register(CarBrandAdmin)
# admin.site.register(CarModel, CarModelAdmin)
