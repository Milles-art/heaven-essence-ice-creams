from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase


class CatalogueTests(APITestCase):
    def setUp(self):
        call_command("seed_data", verbosity=0)

    def test_flavour_list(self):
        res = self.client.get("/api/catalog/flavours/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(f["name"] == "Vanilla" for f in res.json()["results"]))

    def test_category_filter(self):
        res = self.client.get("/api/catalog/flavours/?category=creamy-classics")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(all(f["category"] is not None for f in res.json()["results"]))

    def test_faqs_public(self):
        res = self.client.get("/api/catalog/faqs/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.json()["results"]), 5)

    def test_catalogue_is_read_only(self):
        res = self.client.post("/api/catalog/flavours/", {"name": "Hacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class LeadTests(APITestCase):
    def test_order_can_be_created_publicly(self):
        payload = {
            "customer_name": "Amina",
            "phone": "+255700000000",
            "flavour": "Ukwaju",
            "product_type": "tub",
            "quantity": 2,
            "notes": "Party on Saturday",
        }
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        self.assertEqual(res.json()["status"], "new")

    def test_order_requires_valid_phone(self):
        payload = {"customer_name": "Amina", "phone": "12", "quantity": 1}
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enquiry_can_be_created(self):
        payload = {"name": "Daniel", "phone": "0700000000", "event_type": "birthday", "guests": 30}
        res = self.client.post("/api/enquiries/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)

    def test_leads_are_private(self):
        self.client.post("/api/orders/", {"customer_name": "A", "phone": "0700000000"}, format="json")
        res = self.client.get("/api/orders/")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_dashboard_requires_staff(self):
        res = self.client.get("/api/dashboard/")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        User.objects.create_user("staff", password="pw", is_staff=True)
        self.client.login(username="staff", password="pw")
        res = self.client.get("/api/dashboard/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
