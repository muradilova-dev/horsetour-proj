from django.urls import reverse

from tours.models import Profile

from .base import BaseTest, User


class RegisterTest(BaseTest):
    url = "/api/register/"

    def test_register_ok_creates_profile(self):
        r = self.client.post(self.url, {"username": "newbie", "password": "verystrong987", "phone": "+996555000111"})
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("password", r.data)
        user = User.objects.get(username="newbie")
        self.assertEqual(user.profile.phone, "+996555000111")

    def test_register_without_phone_ok(self):
        r = self.client.post(self.url, {"username": "nophone", "password": "verystrong987"})
        self.assertEqual(r.status_code, 201)

    def test_register_duplicate_username(self):
        r = self.client.post(self.url, {"username": "ramina", "password": "verystrong987"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.data)

    def test_register_weak_password(self):
        r = self.client.post(self.url, {"username": "weak", "password": "123"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("password", r.data)

    def test_register_missing_fields(self):
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.data)
        self.assertIn("password", r.data)

    def test_token_login_ok(self):
        r = self.client.post("/api/token/", {"username": "ramina", "password": "strongpass123"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.data)

    def test_token_wrong_password(self):
        r = self.client.post("/api/token/", {"username": "ramina", "password": "wrong"})
        self.assertEqual(r.status_code, 400)
