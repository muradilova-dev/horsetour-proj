from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from tours.models import Booking, Category, Profile, Tour

User = get_user_model()


class BaseTest(APITestCase):
    """Общие данные для всех тестов."""

    def setUp(self):
        self.admin = User.objects.create_user("admin", password="adminpass123", is_staff=True)
        self.user = User.objects.create_user("ramina", password="strongpass123")
        self.other = User.objects.create_user("aibek", password="strongpass123")
        for u in (self.admin, self.user, self.other):
            Profile.objects.create(user=u)

        self.horse = Category.objects.create(name="конный")
        self.hiking = Category.objects.create(name="пеший")
        self.moto = Category.objects.create(name="мото")

        self.tour = Tour.objects.create(title="Иссык-Куль верхом", price="3500.00")
        self.tour.categories.add(self.horse)
        self.tour2 = Tour.objects.create(title="Ала-Арча пешком", price="1500.00")
        self.tour2.categories.add(self.hiking)

        self.future = (timezone.localtime() + timedelta(days=3)).date()
        self.past = (timezone.localtime() - timedelta(days=3)).date()

    def make_booking(self, user, tour, date, time="10:00"):
        return Booking.objects.create(user=user, tour=tour, date=date, time=time)
