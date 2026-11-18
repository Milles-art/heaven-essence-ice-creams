from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, FAQ, Flavour, GalleryImage, SiteSetting, Testimonial
from .serializers import (
    CategorySerializer, FAQSerializer, FlavourSerializer, GalleryImageSerializer,
    SiteSettingSerializer, TestimonialSerializer,
)


class ReadOnlyMixin:
    """Catalogue is public and read-only; staff edit it in Django admin."""
    http_method_names = ["get", "head", "options"]


class CategoryViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.annotate(flavour_count=Count("flavours"))


class FlavourViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FlavourSerializer

    def get_queryset(self):
        qs = Flavour.objects.filter(is_active=True).select_related("category")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @action(detail=False, url_path="grouped")
    def grouped(self, request):
        """Flavours grouped by category — handy for the menu page filters."""
        data = []
        for cat in Category.objects.all():
            items = self.get_serializer(
                cat.flavours.filter(is_active=True), many=True
            ).data
            data.append({"slug": cat.slug, "name": cat.name, "flavours": items})
        return Response(data)


class GalleryViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        qs = GalleryImage.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class FAQViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.filter(is_active=True)


class TestimonialViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = TestimonialSerializer
    queryset = Testimonial.objects.filter(is_active=True)


class SiteSettingViewSet(ReadOnlyMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteSettingSerializer
    queryset = SiteSetting.objects.all()
    lookup_field = "key"
