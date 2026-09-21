# Django + DRF — LMS

Проект LMS на Django REST Framework. Объединяет домашние задания 1–3:
CRUD, платежи, фильтрация, JWT-авторизация, права модераторов и владельцев.

---

## Структура проекта

```
├── config/                 # настройки проекта
│   ├── settings.py         # DRF, JWT, django-filter, AUTH_USER_MODEL
│   └── urls.py
├── users/                  # пользователи и платежи
│   ├── models.py           # User (AbstractBaseUser), Payment
│   ├── serializers.py      # регистрация, публичный/полный профиль, платежи
│   ├── views.py            # UserViewSet, PaymentViewSet, регистрация
│   ├── permissions.py      # IsModerator, IsOwner, IsOwnerOrModerator, IsOwnerProfile
│   ├── filters.py          # фильтрация платежей
│   ├── fixtures/           # groups.json, payments.json
│   └── management/commands/
│       ├── load_payments.py
│       └── create_moderators_group.py
├── materials/              # курсы и уроки
│   ├── models.py           # Course, Lesson (+ owner)
│   ├── serializers.py      # lessons_count, вложенные lessons
│   ├── views.py            # CourseViewSet, Generic APIViews для Lesson
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## Установка

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_moderators_group   # или: loaddata users/fixtures/groups.json
python manage.py load_payments             # тестовые данные + модератор
python manage.py runserver
```

### Тестовые аккаунты (после `load_payments`)

| Email | Пароль | Роль |
|-------|--------|------|
| user1@example.com | password123 | обычный пользователь |
| user2@example.com | password123 | обычный пользователь |
| moderator@example.com | password123 | модератор |

---

## Авторизация (JWT)

```
POST /api/auth/register/       — регистрация (без токена)
POST /api/auth/token/          — получить access + refresh
POST /api/auth/token/refresh/  — обновить access
```

**Регистрация:**
```json
POST /api/auth/register/
{
  "email": "new@test.com",
  "password": "password123",
  "password_confirm": "password123",
  "phone": "+79001112233",
  "city": "Москва"
}
```

**Логин:**
```json
POST /api/auth/token/
{
  "email": "user1@example.com",
  "password": "password123"
}
```

В Postman: **Authorization → Bearer Token** → вставь `access`.

Все остальные эндпоинты требуют JWT.

---

## Эндпоинты

### Курсы (ViewSet) — JWT

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/courses/` | список курсов |
| POST | `/api/courses/` | создание курса |
| GET | `/api/courses/{id}/` | один курс |
| PUT/PATCH | `/api/courses/{id}/` | обновление |
| DELETE | `/api/courses/{id}/` | удаление |

В ответе курса:
- `lessons_count` — количество уроков (`SerializerMethodField`)
- `lessons` — полный список уроков (вложенный сериализатор)
- `owner` — владелец

**Пример создания:**
```json
POST /api/courses/
{
  "title": "Python Backend",
  "description": "Курс по Django и DRF"
}
```
Поле `owner` заполняется автоматически (`perform_create`).

### Уроки (Generic APIViews) — JWT

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/lessons/` | список уроков |
| POST | `/api/lessons/` | создание урока |
| GET | `/api/lessons/{id}/` | один урок |
| PUT/PATCH | `/api/lessons/{id}/` | обновление |
| DELETE | `/api/lessons/{id}/` | удаление |

**Пример создания:**
```json
POST /api/lessons/
{
  "course": 1,
  "title": "Введение в DRF",
  "description": "Сериализаторы и ViewSets",
  "video_url": "https://example.com/video1"
}
```

### Пользователи — JWT

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/` | список (публичные данные) |
| GET | `/api/users/{id}/` | свой — полный (с payments); чужой — без payments |
| PUT/PATCH | `/api/users/{id}/` | только свой профиль |
| DELETE | `/api/users/{id}/` | только свой профиль |

Регистрация — через `/api/auth/register/` (без JWT).

**Пример обновления профиля:**
```json
PATCH /api/users/1/
{
  "phone": "+79001112233",
  "city": "Москва"
}
```

### Платежи — JWT

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/api/payments/` | список / создание |
| GET/PUT/PATCH/DELETE | `/api/payments/{id}/` | один платёж |

**Фильтрация и сортировка:**

| Параметр | Пример | Описание |
|----------|--------|----------|
| `ordering` | `?ordering=payment_date` | по возрастанию даты |
| `ordering` | `?ordering=-payment_date` | по убыванию даты |
| `paid_course` | `?paid_course=1` | фильтр по ID курса |
| `paid_lesson` | `?paid_lesson=2` | фильтр по ID урока |
| `payment_method` | `?payment_method=cash` | наличные |
| `payment_method` | `?payment_method=transfer` | перевод |

Примеры:
```
/api/payments/?ordering=-payment_date
/api/payments/?paid_course=1
/api/payments/?payment_method=cash
/api/payments/?paid_lesson=2&ordering=payment_date
```

---

## Права доступа

| Роль | Курсы / Уроки |
|------|----------------|
| **Обычный пользователь** | CRUD только **своих** объектов |
| **Модератор** | просмотр и редактирование **любых**; **нельзя** создавать и удалять |
| **Владелец** | полный CRUD своих объектов |

| Действие | Обычный | Модератор | Владелец |
|----------|---------|-----------|----------|
| list / retrieve | свои | все | свои |
| create | ✅ | ❌ | ✅ |
| update | свои | любые | свои |
| delete | свои | ❌ | свои |

- Группа `moderators` — фикстура / `create_moderators_group`
- Назначение пользователей в группу — через админку
- Поле `owner` (FK на User) в моделях Course и Lesson
- При создании объекта `owner` = текущий пользователь

**Профиль:**
- любой авторизованный может **смотреть** любой профиль
- **редактировать** можно только свой
- чужой профиль — без пароля и без истории платежей

---

## Модели

### User (`users`)
- `AbstractBaseUser` + `PermissionsMixin`
- `USERNAME_FIELD = 'email'`
- Поля: `email`, `phone`, `city`, `avatar`

### Course (`materials`)
- `title`, `preview`, `description`, `owner`

### Lesson (`materials`)
- `title`, `description`, `preview`, `video_url`
- `course` → ForeignKey(Course)
- `owner` → ForeignKey(User)

### Payment (`users`)
- `user` → ForeignKey(User)
- `payment_date`
- `paid_course` → ForeignKey(Course, nullable)
- `paid_lesson` → ForeignKey(Lesson, nullable)
- `amount`
- `payment_method`: `cash` | `transfer`

---

## Permissions (классы)

| Класс | Назначение |
|-------|------------|
| `IsModerator` | пользователь в группе `moderators` |
| `IsOwner` | `obj.owner == request.user` |
| `IsOwnerOrModerator` | владелец или модератор (модератор не удаляет) |
| `IsOwnerProfile` | редактировать профиль может только сам пользователь |

Для ViewSet права задаются в `get_permissions()` по `self.action`.  
Для Generic — через `permission_classes` / `get_permissions()`.

---

## Зависимости

```
Django>=4.2,<7
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-filter>=23.0
Pillow>=10.0
```


---

## ДЗ 4: валидация, подписки, пагинация, тесты

### Валидатор YouTube
Файл `materials/validators.py` — разрешены только `youtube.com` / `youtu.be`.
Подключён к полю `video_url` в `LessonSerializer`.

### Подписка на курс
Модель `Subscription` (user + course, unique_together).

```
POST /api/subscriptions/toggle/
{"course_id": 1}
```
Ответ: `{"message": "Подписка добавлена"}` или `"Подписка удалена"`.

В ответе курса поле `is_subscribed` (bool) — подписан ли текущий пользователь.

### Пагинация
`materials/paginators.py` — `MaterialsPagination`:
- `page_size = 5`
- `page_size_query_param = 'page_size'`
- `max_page_size = 50`

Подключена к списку курсов и уроков.

### Тесты
```bash
python manage.py test materials
# покрытие:
coverage run --source='materials,users' manage.py test materials
coverage report -m > coverage.txt
coverage html   # HTML-отчёт в htmlcov/
```


---

## ДЗ 5: документация и Stripe

### Документация API (drf-spectacular)

| URL | Описание |
|-----|----------|
| http://127.0.0.1:8000/api/docs/ | Swagger UI |
| http://127.0.0.1:8000/api/redoc/ | ReDoc |
| http://127.0.0.1:8000/api/schema/ | OpenAPI schema (JSON) |

### Stripe — оплата курса

1. Зарегистрируй тестовый аккаунт: https://dashboard.stripe.com/register  
2. Ключи: https://dashboard.stripe.com/test/apikeys  
3. В `config/settings.py` или env:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

**Создание оплаты:**
```
POST /api/payments/stripe/checkout/
Authorization: Bearer <token>
{
  "course_id": 1,
  "success_url": "http://127.0.0.1:8000/success/",
  "cancel_url": "http://127.0.0.1:8000/cancel/"
}
```
Ответ: объект Payment с `payment_link` (ссылка на Stripe Checkout).

**Проверка статуса (доп.):**
```
GET /api/payments/stripe/status/<session_id>/
```

Цена курса берётся из `Course.price` (в рублях), в Stripe уходит в **копейках** (`amount * 100`).

Тестовые карты: https://stripe.com/docs/testing#cards  
Например: `4242 4242 4242 4242`


---

## ДЗ 6: Celery + Redis + рассылки

### Зависимости и .env

```bash
pip install -r requirements.txt
# Redis должен быть запущен: redis-server
```

`.env`:
```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Запуск (3 терминала)

```bash
# 1. Django
python manage.py runserver

# 2. Celery worker
celery -A config worker -l info

# 3. Celery beat (периодические задачи)
celery -A config beat -l info
```

### Задачи

| Задача | Когда |
|--------|--------|
| `materials.tasks.send_course_update_email` | после успешного update курса/урока, если `updated_at` старше 4 часов |
| `users.tasks.deactivate_inactive_users` | ежедневно (celery-beat): `is_active=False` если `last_login` > 30 дней |

Timezone Django и Celery: `Europe/Moscow`.

Письма в dev пишутся в консоль worker (`EMAIL_BACKEND = console`).

## 👨‍💻 Код написал:

### 𝑯𝒂𝒑𝒌𝒐𝑴 - 𝑩𝒆𝒈𝒊𝒏𝒏𝒆𝒓 𝑷𝒚𝒕𝒉𝒐𝒏-𝒅𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓!