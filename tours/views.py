from rest_framework import mixins, permissions, viewsets
from rest_framework.generics import CreateAPIView

from .models import Booking, Category, Comment, Tour
from .serializers import (
    BookingSerializer,
    CategorySerializer,
    CommentSerializer,
    RegisterSerializer,
    TourSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class RegisterView(CreateAPIView):
    """Регистрация пользователя (создаётся User и связанный Profile)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class TourViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Список туров. Фильтр по категории: `?category=конный`."""

    serializer_class = TourSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Tour.objects.prefetch_related("categories").order_by("id")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(categories__name=category)
        return qs


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Бронирования текущего пользователя."""

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()
        return Booking.objects.filter(user=self.request.user)


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Комментарии к турам. Фильтр: `?tour=<id>`."""

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.select_related("user")
        tour = self.request.query_params.get("tour")
        if tour:
            qs = qs.filter(tour_id=tour)
        return qs
