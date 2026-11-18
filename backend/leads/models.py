from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    PRODUCT_CHOICES = [
        ("cup", "Cup"),
        ("tub", "Tub"),
        ("party-pack", "Party pack"),
    ]
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    flavour = models.CharField(max_length=80, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES, default="cup")
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.customer_name} ({self.quantity}x {self.flavour or self.product_type})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    flavour = models.CharField(max_length=80)
    product_type = models.CharField(max_length=20, default="cup")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.flavour} ({self.product_type})"


class EventEnquiry(models.Model):
    EVENT_CHOICES = [
        ("wedding", "Wedding"),
        ("birthday", "Birthday"),
        ("school", "School event"),
        ("office", "Office party"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("quoted", "Quoted"),
        ("booked", "Booked"),
        ("closed", "Closed"),
    ]
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default="other")
    event_date = models.DateField(null=True, blank=True)
    guests = models.PositiveIntegerField(null=True, blank=True)
    flavours = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Event enquiry"
        verbose_name_plural = "Event enquiries"

    def __str__(self):
        return f"#{self.pk} — {self.name} ({self.event_type})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.name}: {self.subject or self.message[:40]}"
