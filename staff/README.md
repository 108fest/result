# Staff Portal MVP

MVP корпоративного портала в стиле Bitrix с ключевыми разделами:

1. Главная страница с новостями-заглушками.
2. Страница лидерборда сотрудников по KPI.
3. Индивидуальная страница сотрудника.

## Stack

- Backend: FastAPI + SQLAlchemy
- DB: PostgreSQL
- Frontend: React + Vite + TypeScript
- Infra: Docker Compose

## Repo Structure

- `backend/` — FastAPI API, модели, auth и бизнес-логика.
- `frontend/` — React SPA с login, home, leaderboard и profile страницами.
- `infra/` — docker-compose для локального окружения.

## User Fields (DB)

- ФИО (`full_name`)
- Почта/логин (`email`)
- Пароль (`password_hash`, hash без соли по ТЗ)
- KPI (`kpi_score`)
- Фотка (`photo_url`, placeholder)

## Quick Start (Local, no Docker)

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend откроется на `http://localhost:5173`, backend на `http://localhost:8000`.

## Quick Start (Docker)

```bash
cd infra
docker compose up --build
```

Сервисы:

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000`
- Postgres: `localhost:5432`

## Seed Users

- Admin:
	- email: `admin@corp.local`
	- password: `admin123`
- Employee:
	- email: `ivan@corp.local`
	- password: `employee123`

## Implemented API (MVP)

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/home/news`
- `GET /api/leaderboard`
- `GET /api/users/me`
- `GET /api/users/{id}`
- `PATCH /api/admin/users/{id}/kpi` (admin only)

## Security Note

По текущему требованию пароль хешируется без соли. Для production это необходимо заменить на `bcrypt/argon2` с солью.

## db-auth Integration

Staff Portal поддерживает единую авторизацию с db-auth. Подробности в [DBAUTH_INTEGRATION.md](DBAUTH_INTEGRATION.md).

Быстрый старт:
```bash
# Добавить в .env
DBAUTH_DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db

# Перезапустить backend — пользователи импортируются автоматически
```

