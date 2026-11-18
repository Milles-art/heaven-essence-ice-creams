from rest_framework import serializers
from .models import ContactMessage, EventEnquiry, Order


def validate_phone(value):
    cleaned = "".join(c for c in value if c.isdigit() or c == "+")
    if len(cleaned) < 9:
        raise serializers.ValidationError("Enter a valid phone number.")
    return value


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=30, validators=[validate_phone])
    quantity = serializers.IntegerField(min_value=1, max_value=500)

    class Meta:
        model = Order
        fields = [
            "id", "customer_name", "phone", "flavour", "product_type",
            "quantity", "notes", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class EventEnquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=30, validators=[validate_phone])
    guests = serializers.IntegerField(min_value=1, max_value=10000, required=False, allow_null=True)

    class Meta:
        model = EventEnquiry
        fields = [
            "id", "name", "phone", "event_type", "event_date", "guests",
            "flavours", "message", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class ContactMessageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=120)
    message = serializers.CharField(min_length=5)

    class Meta:
        model = ContactMessage
        fields = ["id", "name", "phone", "email", "subject", "message", "created_at"]
        read_only_fields = ["id", "created_at"]
