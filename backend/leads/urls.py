from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ContactMessageViewSet, DashboardView, EventEnquiryViewSet, HealthView, OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet)
router.register("enquiries", EventEnquiryViewSet)
router.register("contact", ContactMessageViewSet)
router.register("dashboard", DashboardView, basename="dashboard")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("", include(router.urls)),
]
