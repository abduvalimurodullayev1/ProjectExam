from django.contrib import admin
from .models import (
    TelegramBotConfiguration,
    User,
    CarListing,
    CarImage,
    Detection,
    TaskLog,
    CarBrand,
    CarModel
)
from django.db.models import Count
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
import weasyprint
from django.conf import settings

from .task import scrape_and_save_listings


@admin.register(TelegramBotConfiguration)
class TelegramBotConfigurationAdmin(admin.ModelAdmin):
    list_display = ("bot_token", "webhook_url", "admin")
    search_fields = ("bot_token", "webhook_url")
    list_editable = ("webhook_url", "admin")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'language', 'detections_count_display', 'last_active_at', 'pdf_export_link')
    search_fields = ('name', 'phone_number')
    list_filter = ('language', 'last_active_at')
    readonly_fields = ('detections_count_display',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(detections_total=Count('detection'))

    def detections_count_display(self, obj):
        return obj.detections_total

    detections_count_display.short_description = 'Detektsiyalar soni'

    def pdf_export_link(self, obj):
        return f'<a href="{obj.id}/export/pdf/">PDF chiqish</a>'

    pdf_export_link.allow_tags = True
    pdf_export_link.short_description = 'PDF Export'


@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'brand', 'model', 'mileage', 'created_at')
    search_fields = ('title', 'brand', 'model')
    list_filter = ('brand', 'model', 'created_at')


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'brand', 'model',
        'scrape_button')
    actions = ['run_scrape_task']

    def run_scrape_task(self, request, queryset):
        for detection in queryset:
            scrape_and_save_listings.apply_async(args=[detection.id])
            self.message_user(request, f"Scraping task for Detection ID {detection.id} has been scheduled.")

    run_scrape_task.short_description = "Run Scrape Data Task"

    def scrape_button(self, obj):
        return f'<a href="/admin/bot/detection/{obj.id}/run_scrape_task/">Scrape Data</a>'

    scrape_button.allow_tags = True
    scrape_button.short_description = 'Run Scrape Task'


# Unregister old Detection admin and register the new one
# admin.site.unregister(Detection)  # Ensure old admin is unregistered first
# admin.site.register(DetectionAdmin)  # Register the updated admin


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ('detection', 'status', 'created_at', 'message')
    list_filter = ('status', 'created_at')
    search_fields = ('detection__id', 'status')


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')
    search_fields = ('name', 'brand__name')
    list_filter = ('brand',)


def export_pdf(request, queryset):
    template = get_template('admin/export_pdf_template.html')
    html = template.render({'object': queryset})

    result = BytesIO()
    weasyprint.HTML(string=html).write_pdf(result)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="export.pdf"'
    return response


export_pdf.short_description = 'Eksport PDF'

UserAdmin.actions = [export_pdf]