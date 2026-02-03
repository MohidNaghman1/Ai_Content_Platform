# AI Content Platform API Documentation

## Overview

The AI Content Platform API is a RESTful service for content creation, user management, AI chat, notifications, and admin analytics. All endpoints use JSON and standard HTTP status codes.

## Base URL

Development: `http://localhost:8000/api/v1`
Production: `https://your-domain.com/api/v1`

Interactive Docs: `/docs` (Swagger UI), `/redoc` (ReDoc)

## Authentication

All protected endpoints require a JWT access token in the `Authorization: Bearer <token>` header. Obtain tokens via `/auth/login`.

**Example:**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Handling

All errors return a JSON object with `detail`, `error_code`, and `status_code`.

**Example:**

```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN",
  "status_code": 401
}
```

## Pagination

Paginated endpoints accept `page` and `size` query parameters. Responses include `items`, `total`, `page`, and `size`.

**Example:**

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20
}
```

## Rate Limiting

Rate limits apply per user type. Exceeding limits returns status 429 with a `retry_after` field.

**Headers:**

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1643723400
```

## API Endpoints (Summary)

### Authentication

- `POST /auth/register` — Register a new user
- `POST /auth/login` — Obtain JWT tokens
- `POST /auth/refresh` — Refresh access token
- `GET /auth/me` — Get current user info
- `POST /auth/logout` — Logout
- `PUT /auth/change-password` — Change password

### Users

- `GET /users` — List users (admin only)
- `GET /users/{user_id}` — Get user by ID
- `PUT /users/{user_id}` — Update user profile
- `POST /users/{user_id}/avatar` — Upload avatar
- `DELETE /users/{user_id}` — Delete user

### Content

- `GET /content/articles` — List articles
- `GET /content/articles/{article_id}` — Get article
- `POST /content/articles` — Create article
- `PUT /content/articles/{article_id}` — Update article
- `DELETE /content/articles/{article_id}` — Delete article
- `POST /content/generate` — AI generate content
- `POST /content/summarize` — AI summarize content
- `GET /content/search` — Search articles
- `GET /content/tags` — List tags

### Chat

- `POST /chat/conversations` — Start conversation
- `GET /chat/conversations` — List conversations
- `GET /chat/conversations/{conversation_id}` — Get conversation
- `POST /chat/message` — Send message
- `POST /chat/stream` — Stream chat response
- `GET /chat/history/{conversation_id}` — Get conversation history
- `DELETE /chat/conversations/{conversation_id}` — Delete conversation

### Notifications

- `GET /notifications` — List notifications
- `PUT /notifications/{notification_id}/read` — Mark as read
- `PUT /notifications/read-all` — Mark all as read
- `DELETE /notifications/{notification_id}` — Delete notification
- `GET /notifications/preferences` — Get notification preferences
- `POST /notifications/preferences` — Update preferences

### Admin

- `GET /admin/analytics` — Dashboard analytics
- `GET /admin/users` — List all users
- `PUT /admin/users/{user_id}/role` — Update user role
- `PUT /admin/users/{user_id}/status` — Activate/deactivate user
- `GET /admin/content/moderate` — Moderation queue
- `POST /admin/content/{article_id}/moderate` — Approve/reject content
- `GET /admin/system/health` — System health
- `GET /admin/logs` — System logs

## Example: Register User

**POST /auth/register**

Request:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "creator"
}
```

Response (201):

```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "creator",
  "is_active": true,
  "created_at": "2025-01-31T10:30:00Z"
}
```

## Support & Resources

- **Docs**: `/docs`
- **GitHub**: https://github.com/yourusername/ai-content-platform
- **Issues**: https://github.com/yourusername/ai-content-platform/issues
- **Email**: api-support@example.com

---
