from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    """Связь 1 к 1: у каждого пользователя ровно один профиль."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)

    def __str__(self):
        return f"Профиль {self.user}"


class Category(models.Model):
    """Категория тура: «конный», «пеший», «мото»."""

    name = models.CharField("Название", max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Tour(models.Model):
    title = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField(
        "Цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    duration_hours = models.PositiveSmallIntegerField(
        "Длительность, ч", default=2, validators=[MinValueValidator(1)]
    )
    # Многие ко многим: тур <-> категории
    categories = models.ManyToManyField(Category, related_name="tours")
    # Многие ко многим: тур <-> пользователи (через таблицу бронирований)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Booking", related_name="booked_tours"
    )

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"

    def __str__(self):
        return self.title


class Booking(models.Model):
    """Покупка тура. Один человек — один тур на конкретные день и время."""

    # Один ко многим: у пользователя и у тура может быть много бронирований
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField("Дата")
    time = models.TimeField("Время")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["date", "time"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date", "time"], name="one_tour_per_user_per_slot"
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.tour} ({self.date} {self.time})"


class Comment(models.Model):
    """Комментарий. Один человек может оставить несколько комментариев."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField("Текст")
    rating = models.PositiveSmallIntegerField(
        "Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} о {self.tour}: {self.rating}/5"
