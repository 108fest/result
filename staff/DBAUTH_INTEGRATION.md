# Интеграция Staff Portal с db-auth

## Обзор

Staff Portal теперь поддерживает единую систему авторизации с db-auth. Пользователи из обеих систем могут:
- Входить по общей сессионной cookie
- Использовать свои учётные данные (email/username + password)
- Иметь доступ к общим данным

## Архитектура

### Единая таблица пользователей (`users`)

| Поле | Portal | db-auth | Описание |
|------|--------|---------|----------|
| `id` | auto-increment | random 1000+ | PK, без конфликтов |
| `email` | email | NULL | Для portal пользователей |
| `username` | NULL | username | Для db-auth пользователей |
| `password_hash` | SHA256 | "" или SHA256 | Для portal пользователей |
| `password_plain` | NULL | plaintext | Для db-auth миграции |
| `auth_source` | "portal" | "dbauth" | Источник создания |
| `level` | 0 | level | Уровень из db-auth |
| `kpi_score` | KPI | kpi | Общее поле KPI |

### Единая таблица сессий (`user_sessions`)

Поддерживает оба формата:
- **Staff Portal**: `session_token` + `expires_at`
- **db-auth**: `token` + TTL 24ч от `created_at`

## Вход в систему

### По email (Staff Portal пользователи)
```json
POST /api/auth/login
{
  "email": "admin@astra.stf",
  "password": "admin123"
}
```

### По username (db-auth пользователи)
```json
POST /api/auth/login
{
  "username": "gosha.cringer",
  "password": "hard_AF_password234123@Fw34$%^&"
}
```

### Через UI
На странице логина можно ввести:
- Email (содержит `@`) — вход как Staff Portal пользователь
- Username (без `@`) — вход как db-auth пользователь

## Миграция данных

### Автоматический импорт при старте

Если задана переменная `DBAUTH_DATABASE_URL`, при старте backend:
1. Импортируются пользователи из db-auth
2. Импортируются активные сессии
3. Создаются записи с `auth_source="dbauth"`

### Настройка

```bash
# .env
DATABASE_URL=postgresql+psycopg://staff:staff@localhost:5432/staff
DBAUTH_DATABASE_URL=postgresql+psycopg2://postgres:Astra_DB_S3cr3t_99!@localhost:5432/bhack
```

### Docker Compose

```yaml
backend:
  environment:
    DATABASE_URL: postgresql+psycopg://staff:staff@db:5432/staff
    DBAUTH_DATABASE_URL: ${DBAUTH_DATABASE_URL:-}
```

## Cookie и сессии

Обе системы используют:
- **Имя cookie**: `staff_session` (настраивается)
- **Domain**: должен совпадать для обоих сервисов
- **Path**: `/`
- **HttpOnly**: `true`
- **Secure**: `false` (для local dev)
- **SameSite**: `lax`

## Проверка работы

### 1. Логин db-auth пользователем
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"gosha.cringer","password":"hard_AF_password234123@Fw34$%^&"}'
```

### 2. Проверка сессии
```bash
curl http://localhost:8000/api/auth/me \
  -b cookies.txt
```

### 3. Доступ к защищённым ресурсам
```bash
curl http://localhost:8000/api/leaderboard \
  -b cookies.txt
```

## Ограничения

1. **Пароли db-auth**: хранятся в plaintext в `password_plain`, проверяются напрямую
2. **TTL сессий db-auth**: 24 часа от `created_at`, не обновляется при использовании
3. **KPI синхронизация**: односторонняя (db-auth → Staff Portal при импорте)

## Безопасность

- Для db-auth пользователей рекомендуется сменить пароль после первого входа
- В production установить `COOKIE_SECURE=true`
- Использовать HTTPS для обоих сервисов
