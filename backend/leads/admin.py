from django.contrib import admin
from .models import ContactMessage, EventEnquiry, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "flavour", "product_type", "quantity", "status", "created_at")
    list_filter = ("status", "product_type")
    search_fields = ("customer_name", "phone", "flavour")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(EventEnquiry)
class EventEnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "event_type", "event_date", "guests", "status", "created_at")
    list_filter = ("status", "event_type")
    search_fields = ("name", "phone", "message")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subject", "phone", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
