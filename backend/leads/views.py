from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactMessage, EventEnquiry, Order
from .serializers import ContactMessageSerializer, EventEnquirySerializer, OrderSerializer


def notify(subject, message):
    """Best-effort email notification — never block a submission on mail."""
    try:
        send_mail(subject, message, None, [settings.EMAIL_TO], fail_silently=True)
    except Exception:
        pass


class PublicCreateMixin:
    """Anyone can submit; only staff can list/read the submitted leads."""
    def get_permissions(self):
        if self.action == "create":
            return []
        return [IsAdminUser()]


class OrderViewSet(PublicCreateMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def perform_create(self, serializer):
        order = serializer.save()
        notify(f"New order #{order.pk} — {order.customer_name}",
               f"Phone: {order.phone}\nFlavour: {order.flavour}\nQuantity: {order.quantity}\nNotes: {order.notes}")

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

    def perform_create(self, serializer):
        enquiry = serializer.save()
        notify(f"New event enquiry #{enquiry.pk} — {enquiry.name}",
               f"Phone: {enquiry.phone}\nEvent: {enquiry.event_type}\nDate: {enquiry.event_date}\n"
               f"Guests: {enquiry.guests}\nFlavours: {enquiry.flavours}\nMessage: {enquiry.message}")

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

    def perform_create(self, serializer):
        msg = serializer.save()
        notify(f"New contact message — {msg.name}",
               f"From: {msg.name} <{msg.email}> {msg.phone}\nSubject: {msg.subject}\n\n{msg.message}")

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def read(self, request, pk=None):
        msg = self.get_object()
        msg.is_read = True
        msg.save(update_fields=["is_read"])
        return Response(ContactMessageSerializer(msg).data)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({"status": "ok", "database": "connected"})


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
