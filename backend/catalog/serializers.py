from rest_framework import serializers
from .models import Category, FAQ, Flavour, GalleryImage, SiteSetting, Testimonial


class CategorySerializer(serializers.ModelSerializer):
    flavour_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "flavour_count"]


class FlavourSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    notes_list = serializers.ListField(read_only=True)

    class Meta:
        model = Flavour
        fields = [
            "id", "name", "swahili_name", "slug", "description", "category",
            "category_name", "image", "accent_color", "notes", "notes_list",
            "price_per_scoop", "sort_order",
        ]


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ["id", "title", "image", "category", "sort_order"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "quote", "author", "location", "flavour_tag", "rating"]


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ["key", "value"]
