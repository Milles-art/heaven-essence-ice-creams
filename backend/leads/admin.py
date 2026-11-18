import csv
from django.contrib import admin, messages
from django.http import HttpResponse
from .models import ContactMessage, EventEnquiry, Order


@admin.action(description="Export selected rows to CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{modeladmin.model._meta.model_name}.csv"'
    writer = csv.writer(response)
    fields = [f.name for f in modeladmin.model._meta.fields]
    writer.writerow(fields)
    for row in queryset.values_list(*fields):
        writer.writerow(row)
    messages.success(request, f"Exported {queryset.count()} rows.")
    return response


class OrderItemInline(admin.TabularInline):
    from .models import OrderItem
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("id", "customer_name", "phone", "flavour", "product_type", "quantity", "status", "created_at")
    list_filter = ("status", "product_type")
    search_fields = ("customer_name", "phone", "flavour")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = [export_csv]


@admin.register(EventEnquiry)
class EventEnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "event_type", "event_date", "guests", "status", "created_at")
    list_filter = ("status", "event_type")
    search_fields = ("name", "phone", "message")
    readonly_fields = ("created_at",)
    actions = [export_csv]
    date_hierarchy = "created_at"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subject", "phone", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    actions = [export_csv]
