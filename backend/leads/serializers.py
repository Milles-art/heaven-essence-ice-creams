from rest_framework import serializers
from .models import ContactMessage, EventEnquiry, Order, OrderItem


def validate_phone(value):
    cleaned = "".join(c for c in value if c.isdigit() or c == "+")
    if len(cleaned) < 9:
        raise serializers.ValidationError("Enter a valid phone number.")
    return value


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["flavour", "product_type", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=30, validators=[validate_phone])
    quantity = serializers.IntegerField(min_value=1, max_value=500, required=False, default=1)
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id", "customer_name", "phone", "flavour", "product_type",
            "quantity", "notes", "items", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
        if items:
            order.flavour = ", ".join(i["flavour"] for i in items)
            order.quantity = sum(i.get("quantity", 1) for i in items)
            order.save(update_fields=["flavour", "quantity"])
        return order


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
