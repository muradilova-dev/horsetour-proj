from django.db import IntegrityError, transaction

from tours.models import Booking, Category, Profile

from .base import BaseTest, User


class RelationsTest(BaseTest):
    def test_one_to_one_user_profile(self):
        self.assertEqual(self.user.profile.user, self.user)
        # второй профиль для того же пользователя создать нельзя
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profile.objects.create(user=self.user)

    def test_one_to_many_tour_has_many_bookings(self):
        self.make_booking(self.user, self.tour, self.future, "10:00")
        self.make_booking(self.other, self.tour, self.future, "10:00")
        self.assertEqual(self.tour.bookings.count(), 2)

    def test_one_to_many_user_has_many_bookings(self):
        self.make_booking(self.user, self.tour, self.future, "10:00")
        self.make_booking(self.user, self.tour2, self.future, "14:00")
        self.assertEqual(self.user.bookings.count(), 2)

    def test_many_to_many_tour_categories(self):
        self.tour.categories.add(self.moto)
        self.assertEqual(self.tour.categories.count(), 2)
        # и обратно: в категории может быть много туров
        self.tour2.categories.add(self.horse)
        self.assertEqual(self.horse.tours.count(), 2)

    def test_many_to_many_tour_participants(self):
        self.make_booking(self.user, self.tour, self.future)
        self.make_booking(self.other, self.tour, self.future)
        self.make_booking(self.user, self.tour2, self.future, "15:00")
        self.assertEqual(self.tour.participants.count(), 2)
        self.assertEqual(self.user.booked_tours.count(), 2)

    def test_category_name_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name="конный")

    def test_db_blocks_double_booking_same_slot(self):
        self.make_booking(self.user, self.tour, self.future, "10:00")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_booking(self.user, self.tour2, self.future, "10:00")
