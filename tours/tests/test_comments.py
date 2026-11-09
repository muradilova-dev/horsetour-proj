from tours.models import Comment

from .base import BaseTest


class CommentTest(BaseTest):
    url = "/api/comments/"

    def body(self, tour=None, text="Отличный тур!", rating=5):
        return {"tour": (tour or self.tour).pk, "text": text, "rating": rating}

    def test_anonymous_cannot_comment(self):
        r = self.client.post(self.url, self.body())
        self.assertIn(r.status_code, (401, 403))

    def test_comment_after_visit_ok(self):
        self.make_booking(self.user, self.tour, self.past)
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["username"], "ramina")

    def test_several_comments_to_same_tour_ok(self):
        self.make_booking(self.user, self.tour, self.past)
        self.client.force_authenticate(self.user)
        for i in range(3):
            r = self.client.post(self.url, self.body(text=f"Комментарий {i}"))
            self.assertEqual(r.status_code, 201)
        self.assertEqual(Comment.objects.filter(user=self.user, tour=self.tour).count(), 3)

    def test_comments_to_several_tours_ok(self):
        self.make_booking(self.user, self.tour, self.past, "10:00")
        self.make_booking(self.user, self.tour2, self.past, "15:00")
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(self.url, self.body(tour=self.tour)).status_code, 201)
        self.assertEqual(self.client.post(self.url, self.body(tour=self.tour2)).status_code, 201)
        self.assertEqual(Comment.objects.filter(user=self.user).count(), 2)

    def test_comment_without_booking_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_to_tour_not_visited_rejected(self):
        # был в одном туре, комментирует другой
        self.make_booking(self.user, self.tour, self.past)
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body(tour=self.tour2))
        self.assertEqual(r.status_code, 400)

    def test_comment_before_tour_happened_rejected(self):
        self.make_booking(self.user, self.tour, self.future)
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 400)

    def test_other_users_booking_does_not_count(self):
        self.make_booking(self.other, self.tour, self.past)
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, self.body())
        self.assertEqual(r.status_code, 400)

    def test_empty_text_rejected(self):
        self.make_booking(self.user, self.tour, self.past)
        self.client.force_authenticate(self.user)
        for text in ("", "   "):
            r = self.client.post(self.url, self.body(text=text))
            self.assertEqual(r.status_code, 400)
            self.assertIn("text", r.data)

    def test_rating_out_of_range_rejected(self):
        self.make_booking(self.user, self.tour, self.past)
        self.client.force_authenticate(self.user)
        for rating in (0, 6, -1):
            r = self.client.post(self.url, self.body(rating=rating))
            self.assertEqual(r.status_code, 400)
            self.assertIn("rating", r.data)

    def test_missing_fields_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {})
        self.assertEqual(r.status_code, 400)

    def test_unknown_tour_rejected(self):
        self.client.force_authenticate(self.user)
        r = self.client.post(self.url, {"tour": 9999, "text": "x", "rating": 5})
        self.assertEqual(r.status_code, 400)

    def test_list_is_public_and_filter_by_tour(self):
        Comment.objects.create(user=self.user, tour=self.tour, text="a", rating=5)
        Comment.objects.create(user=self.user, tour=self.tour2, text="b", rating=4)
        r = self.client.get(self.url)
        self.assertEqual(len(r.data), 2)
        r = self.client.get(self.url, {"tour": self.tour.pk})
        self.assertEqual(len(r.data), 1)
