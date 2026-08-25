# it_sobes — контекст для Claude

Документ для курирования разработки. Цель продукта: сервис IT-собеседований (пользователь из Telegram + сессии интервью). Сейчас только backend, фронта нет.

Общайся с автором на русском. Код — на английском. Комментарии в коде не оставлять, если автор явно не попросил.

---

## Архитектура

Два независимых FastAPI-сервиса, у каждого своя PostgreSQL. Общая сеть `app-shared-network` есть, но HTTP-вызовов между сервисами пока нет. `user_id` в interview — обычная строка, FK на auth нет.

| Сервис | Код | Контейнер | Хост | БД контейнер | БД порт хоста | БД имя |
|---|---|---|---|---|---|---|
| auth | `backend/auth` | `auth_interview` | `localhost:8001` | `interview_auth_pg` | `5433` | `auth_db` |
| interview | `backend/interview` | `interview_module` | `localhost:8002` | `interview_pg` | `5434` | `interview_db` |

Учётные данные Postgres в compose: `admin` / `admin`.

Запуск: `docker compose up -d --build` из корня.

Код приложения в контейнер копируется на build (volume только на `migrations`). После правок Python — пересобрать сервис.

Старт контейнера: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`.

Слои (одинаковые в обоих сервисах):

```
router → service → repository → SQLAlchemy model
              ↑
         Protocol (abc)
```

Сессия: `SessionDep` = `Annotated[AsyncSession, Depends(get_session)]`. Роутер собирает service вручную (`get_service(session)`), DI-контейнера нет.

Async SQLAlchemy + asyncpg. Alembic ходит в БД через sync URL (`postgresql+psycopg2://...`).

---

## Все HTTP-пути

База внутри контейнера — порт 8000. С хоста префиксы ниже.

### Auth — `http://localhost:8001`

| Метод | Путь | Тело / параметры | Ответ | Ошибки |
|---|---|---|---|---|
| GET | `/health` | — | `{"status":"ok"}` | — |
| POST | `/auth/api/v1/` | query: `username`, `tg_id` (не JSON body) | `UserResponseSchema` | 409 если username занят |
| GET | `/auth/api/v1/tg/{tg_id}` | path | один пользователь | 404 |
| GET | `/auth/api/v1/username/{username}` | path | один пользователь | 404 |
| GET | `/auth/api/v1/users` | — | `list[UserResponseSchema]` | — |

`UserResponseSchema`: `id` (UUID), `username`, `tg_id`, `is_active`, `is_staff`. `created_at` в ответе нет.

Создание пользователя — query-параметры FastAPI, не JSON. Пример: `POST /auth/api/v1/?username=max&tg_id=123`.

OpenAPI: `http://localhost:8001/docs`.

### Interview — `http://localhost:8002`

| Метод | Путь | Тело / параметры | Ответ | Ошибки |
|---|---|---|---|---|
| GET | `/health` | — | `{"status":"OK"}` | — |
| POST | `/interview/api/v1/` | JSON `InterviewCreateSchema` | `InterviewResponseSchema` | 422 |
| GET | `/interview/api/v1/user/{user_id}` | path, `user_id` — строка | список интервью | пустой список, не 404 |
| GET | `/interview/api/v1/{interview_id}` | path UUID | одно интервью | 404 |
| PATCH | `/interview/api/v1/{interview_id}` | path UUID + JSON `InterviewUpdateSchema` | обновлённое | 404 |

`InterviewCreateSchema`: `{ "user_id": str, "position": str }`

`InterviewResponseSchema`: `{ "id": UUID, "user_id": str, "level": int|null, "position": str, "status": str }`

`InterviewUpdateSchema` (все поля optional, `exclude_unset`): `{ "level": int|null, "position": str|null, "status": str|null }`

При создании: `status="active"`, `level=null`. Связи с auth нет — любой `user_id` пройдёт.

OpenAPI: `http://localhost:8002/docs`.

---

## Модели БД

### auth.`users`

- `id` UUID PK, default uuid4
- `username` String(500) unique indexed
- `tg_id` String(200) unique indexed
- `is_active` bool default true
- `is_staff` bool default false
- `created_at` timestamptz server_default now()

Миграции: `0001_create_users` создаёт таблицу; `d203c2424b60` (head) — пустая (`pass`).

### interview.`interviews`

- `id` UUID PK, default uuid4
- `user_id` String(200) indexed, не FK
- `level` Integer nullable
- `position` String(500) not null
- `status` String(200) default `"active"` not null

Миграция: `0bae4f9ae2ae` (head).

---

## Карта файлов

### Auth `backend/auth/app/`

- `main.py` — FastAPI, health, include router
- `routes/auth.py` — эндпоинты
- `services/user_service.py` — бизнес-логика, HTTPException
- `services/user_abc.py` — Protocol `IUser`
- `repositories/user_repository.py`
- `models/user.py`
- `schemas/user.py` — `UserCreateSchema` есть, роут его не использует
- `db/session.py`, `db/base.py`
- `core/config.py` — pydantic-settings, `.env`, дефолты localhost

### Interview `backend/interview/app/`

- `main.py`
- `routers/interview.py`
- `services/interview_service.py`
- `services/interview_abc.py` — `IInterview`, заготовка `IFreeInterview`
- `repositories/interview.py`
- `repositories/free_interview.py` — **пустой файл**
- `models/interview.py`
- `schemas/interview.py`
- `db/session.py`, `db/base.py`
- `core/config.py` — сырой `os.getenv`, без дефолтов (в отличие от auth)
- `core/security/depth.py` — **пустой файл** (заготовка под уровень сложности)

---

## Что уже сделано

1. Каркас двух микросервисов + docker-compose + отдельные Postgres + Alembic на старте.
2. Auth CRUD-минимум: регистрация, поиск по Telegram id / username, список всех, уникальность username.
3. Interview CRUD-минимум: создать сессию, список по пользователю, получить по id, патч level/position/status.
4. Починен interview API (см. ниже).

### Что чинили в interview (важно не откатить)

Причина 500 на POST: `await self._session.refresh()` без инстанса. Нужно `refresh(interview)`.

Заодно:

- GET не делал `await` — в ответ уходил coroutine.
- GET на `/` принимал `interview_id: UUID`, репозиторий фильтровал по `user_id: str`.
- PATCH без типа id, без 404.
- `level` в схемах был `str`, в модели `Integer`.
- Ответ без `response_model` / `from_attributes=True` — ORM плохо сериализовался.
- Пути приведены к REST: список по user отдельно от get/patch по UUID.

---

## Чего ещё нет (следующая работа)

- Нет фронта, нет API-gateway, нет JWT/сессий между сервисами.
- Interview не проверяет, что `user_id` существует в auth.
- Нет CORS.
- Нет тестов.
- `IFreeInterview` / `free_interview.py` / `depth.py` — заготовки под бесплатные вопросы и грейд. Не реализовано.
- Auth POST через query, interview POST через JSON — контракты разные.
- Health: auth `"ok"`, interview `"OK"`.
- `UserCreateSchema` мёртвый.
- Конфиг interview не унифицирован с auth (pydantic-settings).
- Код сервисов не в volume — локальные правки без rebuild в контейнере не видны.
- Нет удаления интервью, нет пагинации, нет фильтра по status.

---

## Как курировать автора

Стиль проекта: тонкие роутеры, логика и HTTPException в service, репозиторий только БД, Protocol в `*_abc.py`. Новые фичи interview делать так же, как auth.

Не раздувать: без новых сервисов/очередей, пока нет явной задачи. Пустые `free_interview.py` и `depth.py` — точка расширения для вопросов и сложности, не удалять зря.

Автор просил не оставлять комментарии в коде. Документацию обновлять здесь, если меняются пути или контракты.

Проверка interview после правок:

```text
POST http://localhost:8002/interview/api/v1/
{"user_id":"...", "position":"backend"}

GET  http://localhost:8002/interview/api/v1/user/{user_id}
GET  http://localhost:8002/interview/api/v1/{interview_id}
PATCH http://localhost:8002/interview/api/v1/{interview_id}
{"level": 2, "status": "done"}
```

После изменения `backend/interview/app` или `backend/auth/app`: `docker compose up -d --build <service>`.
