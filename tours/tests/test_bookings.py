from datetime import timedelta

from django.utils import timezone

from tours.models import Booking

from .base import BaseTest


class BookingTest(BaseTest):
    url = "/api/bookings/"

    def body(self, tour=None, date=None, time="10:00"):
        return {
            "tour": (tour or self.tour).pk,
            "date": str(date or self.future),
            "time": time,
        }

    def test_anonymous_cannot_book(self):
        r = self.client.post(self.url, self.body())
        self.assertIn(r.status_code, (401, 403))
        self.assertEqual(Booking.objects.count(), 0)

    def test_book_ok(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 201)
        b = Booking.objects.get()
        self.assertEqual(b.user, self.user)
        self.assertEqual(b.tour, self.tour)

    def test_cannot_book_same_tour_twice_same_slot(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(self.url, self.body()).status_code, 201)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_cannot_book_two_different_tours_same_slot(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.body(tour=self.tour))
        r = self.client.post(self.url, self.body(tour=self.tour2))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)

    def test_same_day_different_time_ok(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.body(time="10:00"))
        r = self.client.post(self.url, self.body(tour=self.tour2, time="15:00"))
        self.assertEqual(r.status_code, 201)

    def test_same_time_different_day_ok(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.body(date=self.future))
        r = self.client.post(self.url, self.body(date=self.future + timedelta(days=1)))
        self.assertEqual(r.status_code, 201)

    def test_other_user_can_take_same_slot(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.body())
        self.client.force_authenticate(self.other)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 201)

    def test_cannot_book_past_date(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body(date=self.past))
        self.assertEqual(r.status_code, 400)

    def test_unknown_tour_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {"tour": 9999, "date": str(self.future), "time": "10:00"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("tour", r.data)

    def test_bad_date_and_time_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {"tour": self.tour.pk, "date": "не-дата", "time": "25:99"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("date", r.data)
        self.assertIn("time", r.data)

    def test_missing_fields_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)

    def test_user_field_in_body_is_ignored(self):
        """Нельзя забронировать тур за другого человека."""
        self.client.force_authenticate(self.user)
        body = self.body()
        body["user"] = self.other.pk
        r = self.client.post(self.url, body)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Booking.objects.get().user, self.user)

    def test_list_shows_only_own_bookings(self):
        self.make_booking(self.user, self.tour, self.future)
        self.make_booking(self.other, self.tour, self.future)
        self.client.force_authenticate(self.user)
        r = self.client.get(self.url)
        self.assertEqual(len(r.data), 1)

    def test_cannot_open_foreign_booking(self):
        foreign = self.make_booking(self.other, self.tour, self.future)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(f"{self.url}{foreign.pk}/").status_code, 404)
        self.assertEqual(self.client.delete(f"{self.url}{foreign.pk}/").status_code, 404)

    def test_cancel_booking_frees_slot(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(self.client.delete(f"{self.url}{r.data['id']}/").status_code, 204)
        r = self.client.post(self.url, self.body(tour=self.tour2))
        self.assertEqual(r.status_code, 201)
