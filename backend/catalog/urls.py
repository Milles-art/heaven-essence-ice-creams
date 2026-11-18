from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, FAQViewSet, FlavourViewSet, GalleryViewSet,
    SiteSettingViewSet, TestimonialViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("flavours", FlavourViewSet, basename="flavour")
router.register("gallery", GalleryViewSet, basename="gallery")
router.register("faqs", FAQViewSet)
router.register("testimonials", TestimonialViewSet)
router.register("settings", SiteSettingViewSet)

urlpatterns = [path("", include(router.urls))]
