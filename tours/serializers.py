from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import Booking, Category, Comment, Profile, Tour

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "phone"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        phone = validated_data.pop("phone", "")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, phone=phone)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TourSerializer(serializers.ModelSerializer):
    # категории передаются по названию: ["конный", "пеший"]
    categories = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Category.objects.all(),
        many=True,
        allow_empty=False,
    )

    class Meta:
        model = Tour
        fields = ["id", "title", "description", "price", "duration_hours", "categories"]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = ["id", "user", "tour", "date", "time", "created_at"]
        read_only_fields = ["created_at"]
        # свой валидатор ниже, чтобы вернуть понятное сообщение
        validators = []

    def validate(self, data):
        start = timezone.make_aware(datetime.combine(data["date"], data["time"]))
        if start <= timezone.now():
            raise serializers.ValidationError("Нельзя купить тур на прошедшее время.")

        busy = Booking.objects.filter(
            user=data["user"], date=data["date"], time=data["time"]
        ).exists()
        if busy:
            raise serializers.ValidationError(
                "У вас уже куплен тур на этот день и время."
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ["id", "user", "username", "tour", "text", "rating", "created_at"]
        read_only_fields = ["created_at"]

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Комментарий не может быть пустым.")
        return value

    def validate(self, data):
        # комментировать можно только тур, в котором человек уже был
        now = timezone.localtime()
        was_there = Booking.objects.filter(user=data["user"], tour=data["tour"]).filter(
            Q(date__lt=now.date()) | Q(date=now.date(), time__lte=now.time())
        )
        if not was_there.exists():
            raise serializers.ValidationError(
                "Оставить комментарий можно только к туру, в котором вы уже были."
            )
        return data
