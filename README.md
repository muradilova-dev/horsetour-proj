# HorseTour — стартап по турам (конные, пешие, мото)

Django + Django REST Framework. Документация API — drf-spectacular (Swagger UI / ReDoc).

## Запуск

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # админ, чтобы создавать категории и туры
python manage.py runserver
```

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Схема OpenAPI: http://127.0.0.1:8000/api/schema/
- Готовая документация без сервера: `docs/api-docs.html` (открыть в браузере), `docs/openapi.yaml`

Обновить документацию после изменений:
`python manage.py spectacular --file docs/openapi.yaml`

## Связи между моделями

| Связь | Где |
|---|---|
| 1 к 1 | `User` — `Profile` |
| 1 ко многим | `User` — `Booking`, `Tour` — `Booking`, `User` — `Comment`, `Tour` — `Comment` |
| Многие ко многим | `Tour` — `Category`; `Tour` — `User` (через `Booking`) |

## Правила

- Один человек может купить только один тур на конкретные день и время (`UniqueConstraint` в БД + проверка в сериализаторе).
- Один человек может оставить несколько комментариев к турам, в которых уже был (дата тура в прошлом).
- У тура есть категории: «конный», «пеший», «мото».

## Тесты

```bash
python manage.py test
```

58 тестов: модели и связи, регистрация и токен, категории, туры, бронирования, комментарии, документация.

## Основные эндпоинты

| Метод | URL | Кто |
|---|---|---|
| POST | /api/register/ | все |
| POST | /api/token/ | все |
| GET, POST | /api/categories/ | чтение — все, создание — админ |
| GET, POST | /api/tours/ (`?category=конный`) | чтение — все, создание — админ |
| GET, POST, DELETE | /api/bookings/ | авторизованные (только свои) |
| GET, POST | /api/comments/ (`?tour=1`) | чтение — все, создание — авторизованные |
