# API Documentation

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Pagination](#pagination)
- [Rate Limiting](#rate-limiting)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication-endpoints)
  - [Users](#user-endpoints)
  - [Content](#content-endpoints)
  - [Chat](#chat-endpoints)
  - [Notifications](#notification-endpoints)
  - [Admin](#admin-endpoints)
- [Webhooks](#webhooks)
- [SDK & Examples](#sdk--examples)

## Overview

The AI Content Platform API is a RESTful API that provides programmatic access to all platform features. The API uses JSON for request and response payloads and follows standard HTTP methods and status codes.

### API Version

Current version: **v1**

### Features

- **RESTful Design**: Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
- **JSON Format**: All requests and responses use JSON
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Different permissions for Admin, Creator, and Viewer roles
- **Pagination**: Efficient data retrieval with cursor-based pagination
- **Rate Limiting**: Protection against abuse
- **Comprehensive Errors**: Detailed error messages with error codes
- **OpenAPI/Swagger**: Interactive API documentation
- **Versioning**: API versioning for backward compatibility

## Base URL

### Development
```
http://localhost:8000/api/v1
```

### Production
```
https://your-domain.com/api/v1
```

### Interactive Documentation

- **Swagger UI**: `{BASE_URL}/docs`
- **ReDoc**: `{BASE_URL}/redoc`
- **OpenAPI Schema**: `{BASE_URL}/openapi.json`

## Authentication

### Overview

The API uses JWT (JSON Web Tokens) for authentication. Tokens are obtained through the login endpoint and must be included in the Authorization header for protected endpoints.

### Authentication Flow

```
1. User registers or logs in
2. Server returns access_token and refresh_token
3. Client includes access_token in Authorization header
4. When access_token expires, use refresh_token to get new tokens
```

### Token Types

#### Access Token
- **Purpose**: Authenticate API requests
- **Lifetime**: 30 minutes (configurable)
- **Storage**: Memory or secure storage (never localStorage for web apps)

#### Refresh Token
- **Purpose**: Obtain new access tokens
- **Lifetime**: 7 days (configurable)
- **Storage**: Secure, HTTP-only cookie or secure storage

### Making Authenticated Requests

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Example Request

```bash
curl -X GET "https://api.example.com/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Token Refresh

When the access token expires (401 Unauthorized with "Token expired" message), use the refresh token:

```bash
curl -X POST "https://api.example.com/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## Error Handling

### Error Response Format

All errors return a consistent JSON structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE_CONSTANT",
  "status_code": 400,
  "timestamp": "2025-01-31T10:30:00Z",
  "path": "/api/v1/content/articles",
  "request_id": "req_abc123xyz"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Success with no response body |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

```python
# Authentication Errors
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
INVALID_TOKEN = "INVALID_TOKEN"
USER_NOT_FOUND = "USER_NOT_FOUND"

# Authorization Errors
INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
ACCOUNT_DISABLED = "ACCOUNT_DISABLED"

# Validation Errors
VALIDATION_ERROR = "VALIDATION_ERROR"
INVALID_EMAIL = "INVALID_EMAIL"
WEAK_PASSWORD = "WEAK_PASSWORD"
DUPLICATE_EMAIL = "DUPLICATE_EMAIL"

# Resource Errors
RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"

# Rate Limiting
RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

# AI Errors
AI_TOKEN_LIMIT_EXCEEDED = "AI_TOKEN_LIMIT_EXCEEDED"
AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
```

### Error Examples

#### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters",
      "type": "value_error.str.min_length"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "status_code": 422
}
```

#### Unauthorized Error (401)

```json
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN",
  "status_code": 401
}
```

#### Forbidden Error (403)

```json
{
  "detail": "You don't have permission to perform this action",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "status_code": 403
}
```

## Pagination

### Query Parameters

```
?page=1&size=20&sort_by=created_at&order=desc
```

- **page**: Page number (default: 1)
- **size**: Items per page (default: 20, max: 100)
- **sort_by**: Field to sort by
- **order**: Sort order (asc or desc)

### Response Format

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### Example

```bash
curl -X GET "https://api.example.com/api/v1/content/articles?page=2&size=10&sort_by=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Rate Limiting

### Limits

| User Type | Per Minute | Per Hour | Per Day |
|-----------|------------|----------|---------|
| Anonymous | 20 | 100 | 500 |
| Authenticated | 60 | 1000 | 10000 |
| Premium | 120 | 2000 | 50000 |

### Rate Limit Headers

Response headers indicate rate limit status:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1643723400
```

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "status_code": 429,
  "retry_after": 30
}
```

## API Endpoints

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "creator"
}
```

**Response** (201 Created):
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

**cURL Example**:
```bash
curl -X POST "https://api.example.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "role": "creator"
  }'
```

---

### Login

Authenticate and receive access tokens.

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "creator"
  }
}
```

**cURL Example**:
```bash
curl -X POST "https://api.example.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint**: `POST /auth/refresh`

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### Get Current User

Get authenticated user's information.

**Endpoint**: `GET /auth/me`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "creator",
  "avatar_url": "https://example.com/avatars/user.jpg",
  "is_active": true,
  "created_at": "2025-01-31T10:30:00Z",
  "updated_at": "2025-01-31T10:30:00Z"
}
```

---

### Logout

Invalidate current access token.

**Endpoint**: `POST /auth/logout`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (204 No Content)

---

### Change Password

Change user password.

**Endpoint**: `PUT /auth/change-password`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

## User Endpoints

### List Users

Get a paginated list of users (Admin only).

**Endpoint**: `GET /users`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `role` (string, optional): Filter by role
- `is_active` (boolean, optional): Filter by active status
- `search` (string, optional): Search by name or email

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "creator",
      "avatar_url": "https://example.com/avatars/user.jpg",
      "is_active": true,
      "created_at": "2025-01-31T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

### Get User by ID

Get specific user details.

**Endpoint**: `GET /users/{user_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "creator",
  "avatar_url": "https://example.com/avatars/user.jpg",
  "bio": "Content creator and AI enthusiast",
  "is_active": true,
  "created_at": "2025-01-31T10:30:00Z",
  "updated_at": "2025-01-31T10:30:00Z",
  "stats": {
    "articles_count": 25,
    "total_views": 10500,
    "conversations_count": 15
  }
}
```

---

### Update User

Update user profile.

**Endpoint**: `PUT /users/{user_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "full_name": "John Smith",
  "bio": "Updated bio text",
  "avatar_url": "https://example.com/avatars/new-avatar.jpg"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "John Smith",
  "bio": "Updated bio text",
  "avatar_url": "https://example.com/avatars/new-avatar.jpg",
  "updated_at": "2025-01-31T11:00:00Z"
}
```

---

### Upload Avatar

Upload user avatar image.

**Endpoint**: `POST /users/{user_id}/avatar`

**Headers**: 
- `Authorization: Bearer {access_token}`
- `Content-Type: multipart/form-data`

**Request Body** (form-data):
- `file`: Image file (JPG, PNG, GIF, WEBP, max 5MB)

**Response** (200 OK):
```json
{
  "avatar_url": "https://example.com/avatars/user-uuid.jpg",
  "message": "Avatar uploaded successfully"
}
```

---

### Delete User

Delete user account (Admin only or self).

**Endpoint**: `DELETE /users/{user_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (204 No Content)

## Content Endpoints

### List Articles

Get a paginated list of articles.

**Endpoint**: `GET /content/articles`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `status` (string, optional): draft, published
- `author_id` (uuid, optional): Filter by author
- `tag` (string, optional): Filter by tag
- `search` (string, optional): Full-text search

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "Introduction to AI",
      "slug": "introduction-to-ai",
      "content": "Article content...",
      "excerpt": "Short excerpt...",
      "status": "published",
      "author": {
        "id": "uuid-string",
        "full_name": "John Doe",
        "avatar_url": "https://example.com/avatars/user.jpg"
      },
      "tags": [
        {"id": "uuid-string", "name": "AI"},
        {"id": "uuid-string", "name": "Technology"}
      ],
      "views": 1250,
      "created_at": "2025-01-31T10:30:00Z",
      "updated_at": "2025-01-31T10:30:00Z",
      "published_at": "2025-01-31T11:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

---

### Get Article by ID

Get specific article details.

**Endpoint**: `GET /content/articles/{article_id}`

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Introduction to AI",
  "slug": "introduction-to-ai",
  "content": "Full article content in markdown...",
  "excerpt": "Short excerpt...",
  "status": "published",
  "author": {
    "id": "uuid-string",
    "full_name": "John Doe",
    "email": "john@example.com",
    "avatar_url": "https://example.com/avatars/user.jpg"
  },
  "tags": [
    {"id": "uuid-string", "name": "AI"},
    {"id": "uuid-string", "name": "Technology"}
  ],
  "views": 1250,
  "reading_time": 8,
  "created_at": "2025-01-31T10:30:00Z",
  "updated_at": "2025-01-31T10:30:00Z",
  "published_at": "2025-01-31T11:00:00Z"
}
```

---

### Create Article

Create a new article.

**Endpoint**: `POST /content/articles`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "My New Article",
  "content": "Full article content...",
  "excerpt": "Brief description...",
  "status": "draft",
  "tags": ["AI", "Technology", "Tutorial"]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "title": "My New Article",
  "slug": "my-new-article",
  "content": "Full article content...",
  "excerpt": "Brief description...",
  "status": "draft",
  "author": {
    "id": "uuid-string",
    "full_name": "John Doe"
  },
  "tags": [
    {"id": "uuid-string", "name": "AI"},
    {"id": "uuid-string", "name": "Technology"},
    {"id": "uuid-string", "name": "Tutorial"}
  ],
  "created_at": "2025-01-31T10:30:00Z"
}
```

---

### Update Article

Update an existing article.

**Endpoint**: `PUT /content/articles/{article_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "status": "published",
  "tags": ["AI", "Machine Learning"]
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Updated Title",
  "slug": "updated-title",
  "content": "Updated content...",
  "status": "published",
  "updated_at": "2025-01-31T11:00:00Z",
  "published_at": "2025-01-31T11:00:00Z"
}
```

---

### Delete Article

Delete an article.

**Endpoint**: `DELETE /content/articles/{article_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (204 No Content)

---

### AI Generate Content

Generate article content using AI.

**Endpoint**: `POST /content/generate`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "prompt": "Write an article about the future of AI in healthcare",
  "max_length": 1000,
  "temperature": 0.7,
  "style": "professional"
}
```

**Response** (200 OK):
```json
{
  "content": "Generated article content...",
  "title_suggestion": "The Future of AI in Healthcare",
  "excerpt_suggestion": "Exploring how artificial intelligence...",
  "tokens_used": 850,
  "generation_time": 3.5
}
```

---

### AI Summarize Content

Summarize long-form content using AI.

**Endpoint**: `POST /content/summarize`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "content": "Long article or text to summarize...",
  "max_length": 200,
  "style": "bullet_points"
}
```

**Response** (200 OK):
```json
{
  "summary": "Summarized content...",
  "key_points": [
    "First key point",
    "Second key point",
    "Third key point"
  ],
  "tokens_used": 250,
  "original_length": 2500,
  "summary_length": 180
}
```

---

### Search Articles

Full-text search across articles.

**Endpoint**: `GET /content/search`

**Query Parameters**:
- `q` (string, required): Search query
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `status` (string, optional): Filter by status

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "Introduction to AI",
      "excerpt": "...highlighted search terms...",
      "relevance_score": 0.95,
      "author": {
        "id": "uuid-string",
        "full_name": "John Doe"
      },
      "created_at": "2025-01-31T10:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 20
}
```

---

### Get Tags

List all available tags.

**Endpoint**: `GET /content/tags`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 50)
- `sort_by` (string, default: usage_count): name, usage_count

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "name": "AI",
      "slug": "ai",
      "article_count": 45,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": "uuid-string",
      "name": "Technology",
      "slug": "technology",
      "article_count": 38,
      "created_at": "2025-01-16T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 50
}
```

## Chat Endpoints

### Create Conversation

Start a new AI conversation.

**Endpoint**: `POST /chat/conversations`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "Help with Python",
  "initial_message": "Can you help me understand decorators in Python?"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "title": "Help with Python",
  "user_id": "uuid-string",
  "message_count": 1,
  "created_at": "2025-01-31T10:30:00Z",
  "updated_at": "2025-01-31T10:30:00Z",
  "last_message": {
    "role": "user",
    "content": "Can you help me understand decorators in Python?",
    "created_at": "2025-01-31T10:30:00Z"
  }
}
```

---

### List Conversations

Get user's conversation history.

**Endpoint**: `GET /chat/conversations`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `sort_by` (string, default: updated_at)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "Help with Python",
      "message_count": 12,
      "created_at": "2025-01-31T10:30:00Z",
      "updated_at": "2025-01-31T11:45:00Z",
      "last_message": {
        "role": "assistant",
        "content": "I hope that clarifies decorators for you!",
        "created_at": "2025-01-31T11:45:00Z"
      }
    }
  ],
  "total": 8,
  "page": 1,
  "size": 20
}
```

---

### Get Conversation

Get specific conversation details.

**Endpoint**: `GET /chat/conversations/{conversation_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Help with Python",
  "user_id": "uuid-string",
  "message_count": 12,
  "total_tokens": 3500,
  "created_at": "2025-01-31T10:30:00Z",
  "updated_at": "2025-01-31T11:45:00Z"
}
```

---

### Send Message

Send a message in a conversation.

**Endpoint**: `POST /chat/message`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "conversation_id": "uuid-string",
  "message": "Can you give me an example?"
}
```

**Response** (200 OK):
```json
{
  "user_message": {
    "id": "uuid-string",
    "role": "user",
    "content": "Can you give me an example?",
    "tokens": 8,
    "created_at": "2025-01-31T11:50:00Z"
  },
  "assistant_message": {
    "id": "uuid-string",
    "role": "assistant",
    "content": "Certainly! Here's a simple decorator example...",
    "tokens": 150,
    "created_at": "2025-01-31T11:50:01Z"
  },
  "conversation": {
    "id": "uuid-string",
    "message_count": 14,
    "total_tokens": 3658
  }
}
```

---

### Stream Chat Response

Send message and receive streaming response.

**Endpoint**: `POST /chat/stream`

**Headers**: 
- `Authorization: Bearer {access_token}`
- `Accept: text/event-stream`

**Request Body**:
```json
{
  "conversation_id": "uuid-string",
  "message": "Explain async/await in Python"
}
```

**Response** (Server-Sent Events):
```
event: start
data: {"message_id": "uuid-string"}

event: token
data: {"token": "Async"}

event: token
data: {"token": "/await"}

event: token
data: {"token": " in"}

event: complete
data: {"message_id": "uuid-string", "tokens": 245}
```

---

### Get Conversation History

Get all messages in a conversation.

**Endpoint**: `GET /chat/history/{conversation_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 50)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "role": "user",
      "content": "Can you help me understand decorators?",
      "tokens": 8,
      "created_at": "2025-01-31T10:30:00Z"
    },
    {
      "id": "uuid-string",
      "role": "assistant",
      "content": "Of course! Decorators in Python...",
      "tokens": 125,
      "created_at": "2025-01-31T10:30:05Z"
    }
  ],
  "total": 12,
  "page": 1,
  "size": 50,
  "conversation": {
    "id": "uuid-string",
    "title": "Help with Python"
  }
}
```

---

### Delete Conversation

Delete a conversation and all its messages.

**Endpoint**: `DELETE /chat/conversations/{conversation_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (204 No Content)

## Notification Endpoints

### Get Notifications

Get user's notifications.

**Endpoint**: `GET /notifications`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `unread_only` (boolean, default: false)
- `type` (string, optional): Filter by type

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "type": "article_published",
      "title": "Your article was published",
      "message": "Your article 'Introduction to AI' is now live!",
      "is_read": false,
      "link": "/articles/introduction-to-ai",
      "created_at": "2025-01-31T10:30:00Z"
    },
    {
      "id": "uuid-string",
      "type": "new_comment",
      "title": "New comment on your article",
      "message": "John Doe commented on 'Introduction to AI'",
      "is_read": true,
      "link": "/articles/introduction-to-ai#comments",
      "created_at": "2025-01-31T09:15:00Z"
    }
  ],
  "total": 25,
  "unread_count": 5,
  "page": 1,
  "size": 20
}
```

---

### Mark as Read

Mark notification as read.

**Endpoint**: `PUT /notifications/{notification_id}/read`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "is_read": true,
  "read_at": "2025-01-31T11:00:00Z"
}
```

---

### Mark All as Read

Mark all notifications as read.

**Endpoint**: `PUT /notifications/read-all`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

---

### Delete Notification

Delete a notification.

**Endpoint**: `DELETE /notifications/{notification_id}`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (204 No Content)

---

### Get Notification Preferences

Get user's notification preferences.

**Endpoint**: `GET /notifications/preferences`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "email_notifications": true,
  "in_app_notifications": true,
  "notification_types": {
    "article_published": true,
    "new_comment": true,
    "new_follower": false,
    "system_updates": true
  }
}
```

---

### Update Notification Preferences

Update notification preferences.

**Endpoint**: `POST /notifications/preferences`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "email_notifications": true,
  "in_app_notifications": true,
  "notification_types": {
    "article_published": true,
    "new_comment": false,
    "new_follower": false,
    "system_updates": true
  }
}
```

**Response** (200 OK):
```json
{
  "message": "Preferences updated successfully",
  "preferences": {
    "email_notifications": true,
    "in_app_notifications": true,
    "notification_types": {
      "article_published": true,
      "new_comment": false,
      "new_follower": false,
      "system_updates": true
    }
  }
}
```

## Admin Endpoints

### Get Dashboard Analytics

Get platform analytics (Admin only).

**Endpoint**: `GET /admin/analytics`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `period` (string, default: 30d): 7d, 30d, 90d, 1y
- `metrics` (array, optional): Specific metrics to retrieve

**Response** (200 OK):
```json
{
  "period": "30d",
  "users": {
    "total": 1250,
    "new": 85,
    "active": 450,
    "growth_rate": 7.2
  },
  "content": {
    "total_articles": 850,
    "published": 750,
    "drafts": 100,
    "total_views": 125000,
    "avg_views_per_article": 166
  },
  "ai_usage": {
    "total_conversations": 2500,
    "total_messages": 15000,
    "tokens_used": 5000000,
    "avg_tokens_per_conversation": 2000
  },
  "engagement": {
    "avg_session_duration": 12.5,
    "bounce_rate": 35.2,
    "returning_users": 62.8
  }
}
```

---

### List All Users (Admin)

Get comprehensive user list with filters.

**Endpoint**: `GET /admin/users`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 50)
- `role` (string, optional)
- `is_active` (boolean, optional)
- `sort_by` (string, default: created_at)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "creator",
      "is_active": true,
      "article_count": 15,
      "conversation_count": 8,
      "last_login": "2025-01-31T09:00:00Z",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "size": 50
}
```

---

### Update User Role

Change user's role (Admin only).

**Endpoint**: `PUT /admin/users/{user_id}/role`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "role": "admin"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "role": "admin",
  "updated_at": "2025-01-31T11:00:00Z"
}
```

---

### Deactivate/Activate User

Toggle user account status (Admin only).

**Endpoint**: `PUT /admin/users/{user_id}/status`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "is_active": false
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "is_active": false,
  "updated_at": "2025-01-31T11:00:00Z"
}
```

---

### Content Moderation Queue

Get articles pending moderation.

**Endpoint**: `GET /admin/content/moderate`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page` (integer, default: 1)
- `size` (integer, default: 20)
- `status` (string, optional): pending, approved, rejected

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "Article Title",
      "author": {
        "id": "uuid-string",
        "full_name": "John Doe"
      },
      "status": "pending",
      "ai_flags": {
        "inappropriate_content": false,
        "spam_likelihood": 0.15,
        "quality_score": 0.85
      },
      "created_at": "2025-01-31T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 20
}
```

---

### Approve/Reject Content

Moderate content (Admin only).

**Endpoint**: `POST /admin/content/{article_id}/moderate`

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "action": "approve",
  "reason": "Content meets quality standards"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "status": "approved",
  "moderated_by": "admin-uuid",
  "moderated_at": "2025-01-31T11:00:00Z",
  "reason": "Content meets quality standards"
}
```

---

### System Health

Get system health status.

**Endpoint**: `GET /admin/system/health`

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-31T11:00:00Z",
  "services": {
    "database": {
      "status": "up",
      "response_time": 5,
      "connections": {
        "active": 12,
        "idle": 8,
        "max": 20
      }
    },
    "redis": {
      "status": "up",
      "response_time": 2,
      "memory_usage": "45MB",
      "connected_clients": 5
    },
    "ai_service": {
      "status": "up",
      "response_time": 250,
      "quota_remaining": 75000
    }
  },
  "metrics": {
    "cpu_usage": 25.5,
    "memory_usage": 62.3,
    "disk_usage": 45.0
  }
}
```

---

### Get System Logs

Retrieve application logs (Admin only).

**Endpoint**: `GET /admin/logs`

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `level` (string, optional): DEBUG, INFO, WARNING, ERROR, CRITICAL
- `start_date` (datetime, optional)
- `end_date` (datetime, optional)
- `page` (integer, default: 1)
- `size` (integer, default: 100)

**Response** (200 OK):
```json
{
  "items": [
    {
      "timestamp": "2025-01-31T11:00:00Z",
      "level": "ERROR",
      "message": "Database connection timeout",
      "module": "database",
      "trace_id": "abc123",
      "user_id": "uuid-string"
    }
  ],
  "total": 500,
  "page": 1,
  "size": 100
}
```

## Webhooks

### Webhook Events

The platform can send webhooks for the following events:

- `user.created`: New user registration
- `user.updated`: User profile update
- `user.deleted`: User account deletion
- `article.created`: New article created
- `article.published`: Article published
- `article.updated`: Article updated
- `article.deleted`: Article deleted
- `conversation.created`: New chat conversation
- `message.created`: New chat message

### Webhook Payload Format

```json
{
  "event": "article.published",
  "timestamp": "2025-01-31T11:00:00Z",
  "data": {
    "id": "uuid-string",
    "title": "Article Title",
    "author_id": "uuid-string",
    "published_at": "2025-01-31T11:00:00Z"
  }
}
```

### Webhook Security

All webhooks include a signature header for verification:

```http
X-Webhook-Signature: sha256=abc123def456...
```

Verify using:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## SDK & Examples

### Python Example

```python
import requests

class AIContentPlatformClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def create_article(self, title, content, tags=None):
        response = self.session.post(
            f"{self.base_url}/content/articles",
            json={
                "title": title,
                "content": content,
                "tags": tags or []
            }
        )
        response.raise_for_status()
        return response.json()
    
    def chat(self, conversation_id, message):
        response = self.session.post(
            f"{self.base_url}/chat/message",
            json={
                "conversation_id": conversation_id,
                "message": message
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = AIContentPlatformClient(
    "https://api.example.com/api/v1",
    "your_access_token"
)

article = client.create_article(
    title="My Article",
    content="Article content...",
    tags=["AI", "Technology"]
)
```

### JavaScript/TypeScript Example

```typescript
class AIContentPlatformClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async createArticle(data: {
    title: string;
    content: string;
    tags?: string[];
  }) {
    return this.request('/content/articles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async chat(conversationId: string, message: string) {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });
  }
}

// Usage
const client = new AIContentPlatformClient(
  'https://api.example.com/api/v1',
  'your_access_token'
);

const article = await client.createArticle({
  title: 'My Article',
  content: 'Article content...',
  tags: ['AI', 'Technology'],
});
```

### cURL Examples

```bash
# Login
curl -X POST "https://api.example.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Create Article
curl -X POST "https://api.example.com/api/v1/content/articles" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Article",
    "content": "Content here...",
    "tags": ["AI", "Tech"]
  }'

# Send Chat Message
curl -X POST "https://api.example.com/api/v1/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "uuid",
    "message": "Hello AI!"
  }'
```

---

## Support & Resources

- **Interactive Documentation**: [Your URL]/docs
- **GitHub Repository**: https://github.com/yourusername/ai-content-platform
- **Issue Tracker**: https://github.com/yourusername/ai-content-platform/issues
- **Email Support**: api-support@example.com

## Changelog

### v1.0.0 (2025-01-31)
- Initial API release
- Authentication & user management
- Content creation and management
- AI chat functionality
- Notification system
- Admin dashboard

---

*Last Updated: January 31, 2025*