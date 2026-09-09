# Django + DRF — LMS

Проект выполнен по домашним заданиям (CRUD + платежи, фильтрация, SerializerMethodField).

---

## Структура проекта

```
├── config/          
│   ├── settings.py  
│   └── urls.py
├── users/           
│   ├── models.py    
│   ├── serializers.py
│   ├── views.py     
│   ├── filters.py   
│   ├── fixtures/    
│   └── management/commands/load_payments.py
├── materials/      
│   ├── models.py    
│   ├── serializers.py
│   ├── views.py     
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
python manage.py load_payments    # загрузка тестовых данных
# или: python manage.py loaddata users/fixtures/payments.json
python manage.py runserver
```

---

## Эндпоинты

### Курсы (ViewSet)
- `GET    /api/courses/`          — список курсов
- `POST   /api/courses/`          — создание курса
- `GET    /api/courses/{id}/`     — один курс
- `PUT    /api/courses/{id}/`     — полное обновление
- `PATCH  /api/courses/{id}/`     — частичное обновление
- `DELETE /api/courses/{id}/`     — удаление

В ответе курса есть:
- `lessons_count` — количество уроков (`SerializerMethodField`)
- `lessons` — полный список уроков (вложенный сериализатор)

**Пример создания курса (POST /api/courses/):**
```json
{
  "title": "Python Backend",
  "description": "Курс по Django и DRF"
}
```

### Уроки (Generic APIViews)
- `GET    /api/lessons/`          — список уроков
- `POST   /api/lessons/`          — создание урока
- `GET    /api/lessons/{id}/`     — один урок
- `PUT    /api/lessons/{id}/`     — полное обновление
- `PATCH  /api/lessons/{id}/`     — частичное обновление
- `DELETE /api/lessons/{id}/`     — удаление

**Пример создания урока (POST /api/lessons/):**
```json
{
  "course": 1,
  "title": "Введение в DRF",
  "description": "Сериализаторы и ViewSets",
  "video_url": "https://example.com/video1"
}
```

### Пользователи (ViewSet)
- `GET    /api/users/`
- `POST   /api/users/`
- `GET    /api/users/{id}/`
- `PUT    /api/users/{id}/`
- `PATCH  /api/users/{id}/`
- `DELETE /api/users/{id}/`

В профиле пользователя выводится `payments` — история платежей.

**Пример обновления профиля (PATCH /api/users/1/):**
```json
{
  "phone": "+79001112233",
  "city": "Москва"
}
```

### Платежи (ViewSet)
- `GET    /api/payments/`
- `POST   /api/payments/`
- `GET    /api/payments/{id}/`
- `PUT    /api/payments/{id}/`
- `PATCH  /api/payments/{id}/`
- `DELETE /api/payments/{id}/`

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

## Модели

### User (приложение `users`)
- Наследуется от `AbstractBaseUser` + `PermissionsMixin`
- `USERNAME_FIELD = 'email'`
- Поля: `email`, `phone`, `city`, `avatar`

### Course (приложение `materials`)
- `title`, `preview` (картинка), `description`

### Lesson (приложение `materials`)
- `title`, `description`, `preview`, `video_url`
- Связь с курсом: `ForeignKey` → Course (`related_name='lessons'`)

### Payment (приложение `users`)
- `user` — ForeignKey на User
- `payment_date` — дата оплаты
- `paid_course` — ForeignKey на Course (nullable)
- `paid_lesson` — ForeignKey на Lesson (nullable)
- `amount` — сумма
- `payment_method` — `cash` (наличные) | `transfer` (перевод на счёт)

---

## Примечания

- Авторизация на данном этапе **не требуется** (`AllowAny`).
- Работу каждого эндпоинта можно проверять через Postman или Browsable API.
- Тестовые данные: `python manage.py load_payments` или фикстура `users/fixtures/payments.json`.

## 👨‍💻 Код написал:

### 𝑯𝒂𝒑𝒌𝒐𝑴 - 𝑩𝒆𝒈𝒊𝒏𝒏𝒆𝒓 𝑷𝒚𝒕𝒉𝒐𝒏-𝒅𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓!