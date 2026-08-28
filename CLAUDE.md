# it_sobes — полный контекст для Claude

Этот файл — источник правды по проекту. Читай его целиком перед любой правкой. Курируй автора на русском, код пиши на английском, комментарии в коде не оставляй, если не попросили.

Дата актуализации: 2026-08-25.

---

## Что это

Backend для IT-собеседований: пользователь приходит из Telegram, создаёт сессию интервью, внутри сессии идут ходы (вопрос → ответ → оценка).

Фронта нет. Gateway нет. JWT между сервисами нет. HTTP-вызовов auth ↔ interview нет.

---

## Как устроено

Два независимых FastAPI-сервиса, у каждого своя PostgreSQL 16.

Слои везде одинаковые:

```
router → service → repository → SQLAlchemy model
              ↑
         Protocol (*_abc.py)
```

Роутер руками собирает service (`get_service(session)`). DI-контейнера нет.

Сессия БД: `SessionDep = Annotated[AsyncSession, Depends(get_session)]`.
Рантайм: SQLAlchemy async + asyncpg. Alembic ходит sync URL `postgresql+psycopg2://...`.

Запуск из корня: `docker compose up -d --build`.

Код приложения копируется в образ при build. Volume только на `migrations`. После правок Python нужен rebuild сервиса.

Старт контейнера: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`.

| Сервис | Код | Контейнер | С хоста | Postgres контейнер | Postgres с хоста | БД |
|---|---|---|---|---|---|---|
| auth | `backend/auth` | `auth_interview` | `localhost:8001` | `interview_auth_pg` | `localhost:5433` | `auth_db` |
| interview | `backend/interview` | `interview_module` | `localhost:8002` | `interview_pg` | `localhost:5434` | `interview_db` |

Сети: `auth-network`, `interview-network`, общая `app-shared-network` (пока не используется для запросов).

Postgres user/password в compose: `admin` / `admin`. Env файлы: `backend/auth/.env`, `backend/interview/.env` (в git не лежат).

Внутри контейнера сервисы слушают `:8000`. С хоста порты 8001 / 8002.

---

## Все HTTP-пути

OpenAPI: `http://localhost:8001/docs` и `http://localhost:8002/docs`.

Префиксы недавно сменили на `/api/v1/...`. Старые `/auth/api/v1` и `/interview/api/v1` больше не существуют.

### Auth — база `http://localhost:8001`

| Метод | Путь | Вход | Ответ | Ошибки |
|---|---|---|---|---|
| GET | `/health` | — | `{"status":"ok"}` | — |
| POST | `/api/v1/auth/` | query `username`, `tg_id` (не JSON) | `UserResponseSchema` | 409 username занят |
| GET | `/api/v1/auth/tg/{tg_id}` | path | один пользователь | 404 |
| GET | `/api/v1/auth/username/{username}` | path | один пользователь | 404 |
| GET | `/api/v1/auth/users` | — | список | — |

Пример создания: `POST http://localhost:8001/api/v1/auth/?username=max&tg_id=123`

`UserResponseSchema`: `id` UUID, `username`, `tg_id`, `is_active`, `is_staff`. Поля `created_at` в ответе нет.

Роутер: `backend/auth/app/routes/auth.py`.

### Interview — база `http://localhost:8002`

| Метод | Путь | Вход | Ответ | Ошибки |
|---|---|---|---|---|
| GET | `/health` | — | `{"status":"OK"}` | — |
| POST | `/api/v1/interview/` | JSON `InterviewCreateSchema` | `InterviewResponseSchema` | 422 |
| GET | `/api/v1/interview/user/{user_id}` | path, строка | список интервью | пустой список, не 404 |
| GET | `/api/v1/interview/{interview_id}` | path UUID | одно интервью | 404 |
| PATCH | `/api/v1/interview/{interview_id}` | path UUID + JSON `InterviewUpdateSchema` | обновлённое | 404 |
| GET | `/api/v1/interview/{id}/turns` | path | список ходов | задумано 404, см. баги |
| POST | `/api/v1/interview/{id}/turns` | path + JSON `TurnCreateSchema` | созданный ход | — |
| PATCH | `/api/v1/interview/turns/{id}` | path UUID хода + JSON `TurnUpdateSchema` | обновлённый ход | — |

Роутер: `backend/interview/app/routers/interview.py`.

Схемы интервью (`backend/interview/app/schemas/interview.py`):

```text
InterviewCreateSchema:  { user_id: str, position: str }
InterviewUpdateSchema:  { level?: int|null, position?: str|null, status?: str|null }  # exclude_unset
InterviewResponseSchema: { id: UUID, user_id: str, level: int|null, position: str, status: str }
```

При создании: `status="active"`, `level=null`. `user_id` не проверяется в auth.

Схемы ходов (`backend/interview/app/schemas/schemas.py`):

```text
TurnCreateSchema:  { question: str, turn_number: int }
TurnUpdateSchema:  { answer?: str|null, turn_number?: int|null, score?: int|null, feedback?: str|null }
TurnResponseSchema: { id, interview_id, question, turn_number, answer, score, feedback }
```

`TurnResponseSchema` объявлен, но на роутах turns `response_model` не стоит. В схеме `answer`/`score`/`feedback` обязательные, в модели они nullable — при подключении response_model сломается.

---

## Модели БД

### auth.`users`

Файл: `backend/auth/app/models/user.py`

- `id` UUID PK, python default uuid4
- `username` String(500) unique indexed
- `tg_id` String(200) unique indexed
- `is_active` bool default true
- `is_staff` bool default false
- `created_at` timestamptz server_default now()

Миграции `backend/auth/migrations/versions/`:
- `0001_create_users` — создаёт таблицу
- `d203c2424b60` (head) — пустая (`pass`)

### interview.`interviews`

Файл: `backend/interview/app/models/interview.py`

- `id` UUID PK, python default uuid4
- `user_id` String(200) indexed, **не FK** на auth
- `level` Integer nullable
- `position` String(500) not null
- `status` String(200) default `"active"` not null

### interview.`turns`

Файл: `backend/interview/app/models/turn.py`

- `id` UUID PK
- `interview_id` UUID FK → `interviews.id` ON DELETE CASCADE
- `question` String(500) not null
- `answer` String(500) nullable
- `turn_number` Integer nullable
- `score` Integer nullable
- `feedback` String(500) nullable
- `created_at` timestamptz server_default now()

Relationship ORM (`relationship(...)`) не объявлен.

Миграции `backend/interview/migrations/versions/`:
- `0bae4f9ae2ae` — `interviews`
- `9e5f7257d550` — пустая (`pass`), заголовок «made turns model»
- `61160fe68ae6` (head) — реально создаёт `turns`

Alembic env импортирует обе модели: `InterviewModel`, `TurnModel`.

---

## Карта файлов

### Auth `backend/auth/app/`

| Файл | Роль |
|---|---|
| `main.py` | FastAPI title=auth, health, include router |
| `routes/auth.py` | эндпоинты |
| `services/user_service.py` | логика, HTTPException |
| `services/user_abc.py` | Protocol `IUser` |
| `repositories/user_repository.py` | БД |
| `models/user.py` | ORM |
| `schemas/user.py` | `UserCreateSchema` есть, роут его не использует |
| `db/session.py`, `db/base.py` | async session, DeclarativeBase |
| `core/config.py` | pydantic-settings, `.env`, дефолты localhost |

### Interview `backend/interview/app/`

| Файл | Роль |
|---|---|
| `main.py` | FastAPI title=interview, health, include router |
| `routers/interview.py` | все эндпоинты interview + turns |
| `services/interview_service.py` | interview + turn в одном сервисе |
| `services/interview_abc.py` | `IInterview`, заготовка `IFreeInterview` |
| `services/turn_abc.py` | `ITurn` |
| `repositories/interview.py` | CRUD interviews |
| `repositories/turn.py` | CRUD turns |
| `repositories/free_interview.py` | заготовка, не подключена |
| `models/interview.py`, `models/turn.py` | ORM |
| `schemas/interview.py`, `schemas/schemas.py` | pydantic |
| `db/session.py`, `db/base.py` | как в auth |
| `core/config.py` | сырой `os.getenv`, без дефолтов |
| `core/security/depth.py` | пустой файл, заготовка под сложность |

Отдельного `TurnService` нет: методы ходов живут в `InterviewService`.

---

## Что уже реализовано

1. Каркас двух микросервисов + compose + две Postgres + Alembic на старте контейнера.
2. Auth: создать пользователя (query), найти по tg_id / username, список всех, 409 на занятый username, 404 если нет.
3. Interview: создать сессию, список по `user_id`, получить/патчить по UUID, 404 если нет.
4. Turns: модель + миграция, репозиторий, protocol, эндпоинты list/create/update.
5. Починенный базовый interview CRUD (не откатывать).

### Что чинили в interview CRUD (история)

500 на POST было из `await self._session.refresh()` без инстанса. Нужно `refresh(interview)`.

Заодно тогда:
- GET не `await` — в ответ уходил coroutine
- GET принимал `interview_id`, репозиторий фильтровал по `user_id`
- PATCH без типа id и без 404
- `level` в схемах был `str`, в модели Integer
- не было `response_model` / `from_attributes=True`

---

## Что сломано или сырое прямо сейчас

Это важно для курирования — не считать turns «готовыми».

1. **`InterviewService.__init__` требует `interview` и `turn`, роутер передаёт только `InterviewRepository`.** Любой вызов interview API должен падать (`TypeError: missing turn`). Нужно прокинуть `TurnRepository(session)` вторым аргументом.
2. PATCH turn: репозиторий может вернуть `None`, service не поднимает 404.
3. GET turns: `scalars().all()` всегда список, не `None` — ветка 404 «turns not found» почти мёртвая. Существование interview не проверяется.
4. POST/GET turns: path `id` без типа `uuid.UUID`.
5. `TurnResponseSchema` не подключён; nullable поля в схеме обязательные.
6. `created_at` хода в response-схеме нет.
7. Пустая миграция `9e5f7257d550` в середине цепочки — не удалять, иначе сломается history.
8. `UserCreateSchema` и `UserCreateSchema` в репозитории импортируется, но `add()` берёт kwargs, не схему.

---

## Чего нет (бэклог)

- фронт, gateway, CORS, тесты
- проверка, что `user_id` существует в auth
- генерация вопросов (LLM / банк) — `IFreeInterview.get_questions`
- логика грейда — `core/security/depth.py`
- удаление интервью/ходов, пагинация, фильтр по status
- уникальность `(interview_id, turn_number)`
- унификация конфига interview с pydantic-settings как в auth
- единообразие health: auth `"ok"`, interview `"OK"`
- auth POST через query, interview POST через JSON

---

## Как курировать автора

Держи стиль слоёв. Новые фичи interview — как auth: тонкий роутер, HTTPException в service, репозиторий только БД, Protocol в `*_abc.py`.

Не плодить новые сервисы/очереди без задачи. Пустые `free_interview.py` и `depth.py` — точки расширения, не сносить без причины.

Комментарии в коде не писать. Этот файл обновлять, если меняются пути, схемы или статус фич.

После правок `backend/*/app`: `docker compose up -d --build auth` или `interview`.

Проверка (после починки DI turns):

```text
POST http://localhost:8001/api/v1/auth/?username=max&tg_id=123

POST http://localhost:8002/api/v1/interview/
{"user_id":"<user uuid or any string>","position":"backend"}

GET  http://localhost:8002/api/v1/interview/user/{user_id}
GET  http://localhost:8002/api/v1/interview/{interview_id}
PATCH http://localhost:8002/api/v1/interview/{interview_id}
{"level":2,"status":"done"}

POST http://localhost:8002/api/v1/interview/{interview_id}/turns
{"question":"What is GIL?","turn_number":1}

GET  http://localhost:8002/api/v1/interview/{interview_id}/turns
PATCH http://localhost:8002/api/v1/interview/turns/{turn_id}
{"answer":"...","score":8,"feedback":"..."}
```
