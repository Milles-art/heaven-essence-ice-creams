from django.contrib import admin
from .models import Category, FAQ, Flavour, GalleryImage, SiteSetting, Testimonial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Flavour)
class FlavourAdmin(admin.ModelAdmin):
    list_display = ("name", "swahili_name", "category", "price_per_scoop", "sort_order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "swahili_name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "sort_order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "sort_order", "is_active")
    search_fields = ("question", "answer")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "flavour_tag", "rating", "is_active")
    list_filter = ("rating", "is_active")


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
