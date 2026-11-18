from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Flavour(models.Model):
    name = models.CharField(max_length=80)
    swahili_name = models.CharField(max_length=80, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="flavours")
    image = models.CharField(max_length=255, help_text="Path or URL to the image")
    accent_color = models.CharField(max_length=20, blank=True)
    notes = models.CharField(max_length=255, blank=True, help_text="Comma-separated tasting notes")
    price_per_scoop = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def notes_list(self):
        return [n.strip() for n in self.notes.split(",") if n.strip()]


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ("flavours", "Flavours"),
        ("kitchen", "In the kitchen"),
        ("scoops", "Scoops & cone"),
    ]
    title = models.CharField(max_length=120)
    image = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="flavours")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=80)
    location = models.CharField(max_length=80, blank=True)
    flavour_tag = models.CharField(max_length=80, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "author"]

    def __str__(self):
        return f"{self.author} — {self.quote[:40]}"


class SiteSetting(models.Model):
    key = models.CharField(max_length=60, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} = {self.value[:40]}"
