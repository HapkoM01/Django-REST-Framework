# Django + DRF — Курсы и Уроки

Проект выполнен по домашнему заданию.

## Структура

- `users` — кастомная модель пользователя (email как USERNAME_FIELD)
- `materials` — модели Course и Lesson + CRUD

## Установка

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Эндпоинты

### Курсы (ViewSet)
- `GET    /api/courses/`          — список курсов
- `POST   /api/courses/`          — создание курса
- `GET    /api/courses/{id}/`     — один курс
- `PUT    /api/courses/{id}/`     — полное обновление
- `PATCH  /api/courses/{id}/`     — частичное обновление
- `DELETE /api/courses/{id}/`     — удаление

### Уроки (Generic APIViews)
- `GET    /api/lessons/`          — список уроков
- `POST   /api/lessons/`          — создание урока
- `GET    /api/lessons/{id}/`     — один урок
- `PUT    /api/lessons/{id}/`     — полное обновление
- `PATCH  /api/lessons/{id}/`     — частичное обновление
- `DELETE /api/lessons/{id}/`     — удаление

### Пользователи (доп. задание, ViewSet)
- `GET    /api/users/`
- `POST   /api/users/`
- `GET    /api/users/{id}/`
- `PUT    /api/users/{id}/`
- `PATCH  /api/users/{id}/`
- `DELETE /api/users/{id}/`

## Примеры запросов (Postman)

**Создание курса (POST /api/courses/):**
```json
{
  "title": "Python Backend",
  "description": "Курс по Django и DRF"
}
```

**Создание урока (POST /api/lessons/):**
```json
{
  "course": 1,
  "title": "Введение в DRF",
  "description": "Сериализаторы и ViewSets",
  "video_url": "https://example.com/video1"
}
```

**Обновление профиля (PATCH /api/users/1/):**
```json
{
  "phone": "+79001112233",
  "city": "Москва"
}
```

Авторизация на этом этапе **не требуется** (AllowAny).

## 👨‍💻 Код написал:

### 𝑯𝒂𝒑𝒌𝒐𝑴 - 𝑩𝒆𝒈𝒊𝒏𝒏𝒆𝒓 𝑷𝒚𝒕𝒉𝒐𝒏-𝒅𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓!
