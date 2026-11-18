from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import ContactMessage, EventEnquiry, Order
from .serializers import ContactMessageSerializer, EventEnquirySerializer, OrderSerializer


class PublicCreateMixin:
    """Anyone can submit; only staff can list/read the submitted leads."""
    def get_permissions(self):
        if self.action == "create":
            return []
        return [IsAdminUser()]


class OrderViewSet(PublicCreateMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=400)
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)


class EventEnquiryViewSet(PublicCreateMixin, viewsets.ModelViewSet):
    serializer_class = EventEnquirySerializer
    queryset = EventEnquiry.objects.all()

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def status(self, request, pk=None):
        enquiry = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(EventEnquiry.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=400)
        enquiry.status = new_status
        enquiry.save(update_fields=["status"])
        return Response(EventEnquirySerializer(enquiry).data)


class ContactMessageViewSet(PublicCreateMixin, viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.all()


class DashboardView(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        return Response({
            "orders": Order.objects.count(),
            "new_orders": Order.objects.filter(status="new").count(),
            "enquiries": EventEnquiry.objects.count(),
            "new_enquiries": EventEnquiry.objects.filter(status="new").count(),
            "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
            "orders_by_status": dict(Order.objects.values_list("status").annotate(n=Count("id"))),
        })
