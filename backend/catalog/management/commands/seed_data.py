"""Populate the database with the real site content. Idempotent."""
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, FAQ, Flavour, GalleryImage, SiteSetting, Testimonial

FLAVOURS = [
    ("Vanilla", "Vanila", "Classic and creamy vanilla flavour, slow-churned with real vanilla pods.", "creamy-classics", "#F3DFA8", "Real vanilla pods, Fresh cream, Timeless", "/images/flavours/vanilla.webp", None),
    ("Chocolate", "Chokoleti", "Rich and smooth chocolate delight for the true cocoa lover.", "creamy-classics", "#8A5A3C", "Deep cocoa, Velvety, Indulgent", "/images/flavours/chocolate.webp", None),
    ("Strawberry", "Stroberi", "Sweet and fruity strawberry flavour, bursting with fresh berries.", "fresh-fruity", "#F2879A", "Fresh berries, Sweet, Fruity", "/images/flavours/strawberry.webp", None),
    ("Mango", "Embe", "Tropical mango made with real, sun-ripened Morogoro fruit.", "fresh-fruity", "#F7B23B", "Real mango, Tropical, Sunny", "/images/flavours/mango.webp", None),
    ("Ukwaju", "Ukwaju", "Sweet and tangy ukwaju (tamarind) flavour, a true taste of home.", "tanzanian-signatures", "#C98F5A", "Local tamarind, Tangy, Signature", "/images/flavours/ukwaju.webp", None),
    ("Cookies & Cream", "Biskuti na Krimu", "Creamy vanilla with generous cookie crunch in every spoonful.", "creamy-classics", "#6E6A70", "Cookie crunch, Creamy, Kids' favourite", "/images/flavours/cookies-cream.webp", None),
    ("Coconut", "Nazi", "Creamy coconut made with real coconut milk from the coast.", "creamy-classics", "#D9CFC0", "Real coconut milk, Smooth, Coastal", "/images/flavours/coconut.webp", None),
    ("Banana", "Ndizi", "Natural banana flavour for a soft, creamy taste.", "fresh-fruity", "#F1D77A", "Ripe bananas, Mellow, Natural", "/images/flavours/banana.webp", None),
    ("Mint Choc Chip", "Minti na Chokoleti", "Cool mint with dark chocolate chips. Refreshing on hot days.", "tanzanian-signatures", "#9ED3AE", "Fresh mint, Choc chips, Cooling", "/images/flavours/mint-choc-chip.webp", None),
    ("Passion Fruit", "Pasheni", "Refreshing passion fruit with a bright tropical twist.", "fresh-fruity", "#F4C13D", "Real passion, Zesty, Tropical", "/images/flavours/passion-fruit.webp", None),
]

FAQS = [
    ("What's in your ice cream?", "Fresh local milk and cream, real fruit, sugar and a little vanilla. That's the whole list — no artificial colours, flavours or preservatives."),
    ("Do you have dairy-free options?", "Our coconut flavour is made with real coconut milk and is naturally dairy-free. Let us know your needs when you order and we'll guide you through the options."),
    ("Are your flavours suitable for vegetarians?", "Yes, all ten flavours are vegetarian. We don't use gelatine or animal rennet."),
    ("Do you deliver outside Morogoro?", "We deliver across Morogoro town every day. For special event orders further afield, message us and we'll see what we can arrange."),
    ("How long does ice cream keep?", "Best enjoyed the day you get it. In a home freezer it keeps well for up to two weeks — just let it soften a few minutes before scooping."),
    ("Can I order a party tub?", "Absolutely. Our tubs come in 1-litre and 4-litre sizes, and you can mix flavours. WhatsApp us your date and guest count and we'll sort it out."),
    ("Do you cater weddings and events?", "We do! Scoop stations, party tubs and custom carts are all available. Head to the Events page or message us for a quote."),
    ("Can I request a custom flavour?", "For events we can often create a custom batch. Get in touch early and we'll talk through what you have in mind."),
    ("How do I pay?", "Payment is simple — pay on delivery or send it via mobile money. We'll confirm the details when you order."),
    ("What are your opening hours?", "Every day, 10:00 AM to 9:00 PM. Come by, or message us any time and we'll reply as soon as we can."),
]

TESTIMONIALS = [
    ("The ukwaju flavour tastes exactly like childhood. My kids ask for it every weekend!", "Amina J.", "Kihonda", "Ukwaju"),
    ("Creamy, fresh and you can taste the real mango. Best ice cream in Morogoro, hands down.", "Daniel M.", "Mazimbu", "Mango"),
    ("Ordered for my daughter's birthday and everyone loved it. Cookies & Cream disappeared first.", "Neema K.", "Boma Road", "Cookies & Cream"),
    ("Mint choc chip after a long hot day is pure heaven. Friendly service too.", "Joseph L.", "SUA Campus", "Mint Choc Chip"),
]

GALLERY = [
    ("Vanilla", "/images/flavours/vanilla.webp", "flavours"),
    ("Chocolate", "/images/flavours/chocolate.webp", "flavours"),
    ("Strawberry", "/images/flavours/strawberry.webp", "flavours"),
    ("Mango", "/images/flavours/mango.webp", "flavours"),
    ("Ukwaju", "/images/flavours/ukwaju.webp", "flavours"),
    ("Cookies & Cream", "/images/flavours/cookies-cream.webp", "flavours"),
    ("Coconut", "/images/flavours/coconut.webp", "flavours"),
    ("Banana", "/images/flavours/banana.webp", "flavours"),
    ("Mint Choc Chip", "/images/flavours/mint-choc-chip.webp", "flavours"),
    ("Passion Fruit", "/images/flavours/passion-fruit.webp", "flavours"),
    ("Our kitchen", "/images/story-kitchen.webp", "kitchen"),
    ("The cone", "/images/hero/cone.webp", "scoops"),
    ("Vanilla scoop", "/images/hero/scoop-vanilla.webp", "scoops"),
    ("Chocolate scoop", "/images/hero/scoop-chocolate.webp", "scoops"),
    ("Strawberry scoop", "/images/hero/scoop-strawberry.webp", "scoops"),
    ("Fresh strawberry", "/images/hero/strawberry.webp", "kitchen"),
    ("Mango cube", "/images/hero/mango-cube.webp", "kitchen"),
    ("Mint leaf", "/images/hero/mint-leaf.webp", "kitchen"),
    ("Dark chocolate chunk", "/images/hero/chocolate-chunk.webp", "kitchen"),
]

SETTINGS = [
    ("site_name", "Heaven Essence Ice Creams"),
    ("location", "Morogoro, Tanzania"),
    ("phone", "+255 700 000 000"),
    ("whatsapp", "255700000000"),
    ("instagram", "https://instagram.com"),
    ("opening_hours", "Daily, 10:00 AM – 9:00 PM"),
    ("delivery_area", "Across Morogoro town"),
]


class Command(BaseCommand):
    help = "Seed the catalogue with the real Heaven Essence content"

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for i, (name, slug, desc, order) in enumerate([
            ("Creamy classics", "creamy-classics", "Rich, smooth and timeless favourites.", 0),
            ("Fresh & fruity", "fresh-fruity", "Bright flavours made with real fruit.", 1),
            ("Tanzanian signatures", "tanzanian-signatures", "Local favourites with a taste of home.", 2),
        ]):
            cat, _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": desc, "sort_order": order}
            )
            categories[slug] = cat

        for i, (name, swahili, desc, cat, colour, notes, image, price) in enumerate(FLAVOURS):
            Flavour.objects.update_or_create(slug=name.lower().replace(" ", "-").replace("&", "and"), defaults={
                "name": name, "swahili_name": swahili, "description": desc,
                "category": categories[cat], "accent_color": colour, "notes": notes,
                "image": image, "price_per_scoop": price, "sort_order": i,
            })

        for i, (question, answer) in enumerate(FAQS):
            FAQ.objects.update_or_create(question=question, defaults={"answer": answer, "sort_order": i})

        for i, (quote, author, location, tag) in enumerate(TESTIMONIALS):
            Testimonial.objects.update_or_create(author=author, quote=quote, defaults={
                "location": location, "flavour_tag": tag, "sort_order": i,
            })

        for i, (title, image, cat) in enumerate(GALLERY):
            GalleryImage.objects.update_or_create(title=title, image=image, defaults={
                "category": cat, "sort_order": i,
            })

        for key, value in SETTINGS:
            SiteSetting.objects.update_or_create(key=key, defaults={"value": value})

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(FLAVOURS)} flavours, {len(FAQS)} FAQs, "
            f"{len(TESTIMONIALS)} testimonials, {len(GALLERY)} gallery images "
            f"and {len(SETTINGS)} settings."
        ))
