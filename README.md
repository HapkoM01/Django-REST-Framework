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
