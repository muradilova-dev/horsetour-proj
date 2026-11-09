from tours.models import Category, Tour

from .base import BaseTest


class CategoryTest(BaseTest):
    url = "/api/categories/"

    def test_list_is_public(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual({c["name"] for c in r.data}, {"конный", "пеший", "мото"})

    def test_admin_can_create(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, {"name": "лыжный"})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Category.objects.filter(name="лыжный").exists())

    def test_regular_user_cannot_create(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {"name": "лыжный"})
        self.assertEqual(r.status_code, 403)

    def test_anonymous_cannot_create(self):
        r = self.client.post(self.url, {"name": "лыжный"})
        self.assertIn(r.status_code, (401, 403))

    def test_duplicate_name_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, {"name": "конный"})
        self.assertEqual(r.status_code, 400)

    def test_empty_name_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, {"name": ""})
        self.assertEqual(r.status_code, 400)


class TourTest(BaseTest):
    url = "/api/tours/"

    def payload(self, **extra):
        data = {
            "title": "Мото по Боомскому ущелью",
            "description": "Целый день в седле",
            "price": "5000.00",
            "duration_hours": 6,
            "categories": ["мото"],
        }
        data.update(extra)
        return data

    def test_admin_creates_tour_with_categories(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, self.payload(categories=["мото", "пеший"]), format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(set(r.data["categories"]), {"мото", "пеший"})
        self.assertEqual(Tour.objects.get(pk=r.data["id"]).categories.count(), 2)

    def test_user_cannot_create_tour(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(r.status_code, 403)

    def test_unknown_category_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, self.payload(categories=["космический"]), format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("categories", r.data)

    def test_empty_categories_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, self.payload(categories=[]), format="json")
        self.assertEqual(r.status_code, 400)

    def test_negative_price_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, self.payload(price="-10"), format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("price", r.data)

    def test_zero_price_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post(self.url, self.payload(price="0"), format="json")
        self.assertEqual(r.status_code, 400)

    def test_missing_title_rejected(self):
        self.client.force_authenticate(self.admin)
        data = self.payload()
        del data["title"]
        r = self.client.post(self.url, data, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("title", r.data)

    def test_list_and_filter_by_category(self):
        r = self.client.get(self.url)
        self.assertEqual(len(r.data), 2)
        r = self.client.get(self.url, {"category": "конный"})
        self.assertEqual([t["title"] for t in r.data], ["Иссык-Куль верхом"])
        r = self.client.get(self.url, {"category": "мото"})
        self.assertEqual(r.data, [])
