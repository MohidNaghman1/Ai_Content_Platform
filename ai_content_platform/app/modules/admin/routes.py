# Admin dashboard routes for user management, content moderation,
# analytics, and system health monitoring
from fastapi import APIRouter, Depends, status
from ai_content_platform.app.shared.dependencies import require_role
from ai_content_platform.app.modules.users.schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from ai_content_platform.app.modules.admin.services import (
    get_all_users,
    create_user_service,
    update_user_service,
    delete_user_service,
    get_all_articles,
    create_article_service,
    update_article_service,
    delete_article_service,
    get_flagged_content,
    get_analytics_stats,
    get_system_health,
    moderate_article_service,
)

# Content moderation endpoints

from ai_content_platform.app.modules.content.schemas import (
    ArticleOut,
    ArticleCreate,
    ArticleUpdate,
)

admin_router = APIRouter(prefix="/admin", tags=["admin"])


# List flagged articles
@admin_router.get(
    "/moderation/flagged",
    response_model=list[ArticleOut],
    dependencies=[Depends(require_role("admin"))],
)
async def list_flagged_articles():
    return await get_flagged_content()


# User management endpoints
@admin_router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_role("admin"))],
)
async def admin_list_users():
    return await get_all_users()


@admin_router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_create_user(user: UserCreate):
    return await create_user_service(user)


@admin_router.put(
    "/users/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_update_user(user_id: int, update: UserUpdate):
    return await update_user_service(user_id, update)


@admin_router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_delete_user(user_id: int):
    return await delete_user_service(user_id)


# Article management endpoints


@admin_router.get(
    "/articles",
    response_model=list[ArticleOut],
    dependencies=[Depends(require_role("admin"))],
)
async def admin_list_articles():
    return await get_all_articles()


@admin_router.post(
    "/articles",
    response_model=ArticleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_create_article(article: ArticleCreate):
    return await create_article_service(article)


@admin_router.put(
    "/articles/{article_id}",
    response_model=ArticleOut,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_update_article(article_id: int, update: ArticleUpdate):
    return await update_article_service(article_id, update)


@admin_router.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_delete_article(article_id: int):
    return await delete_article_service(article_id)


# List flagged articles (admin only)


@admin_router.get(
    "/moderation/flagged",
    response_model=list[ArticleOut],
    dependencies=[Depends(require_role("admin"))],
)
async def list_flagged_articles():
    return await get_flagged_content()


# Moderate article (approve/reject) with AI suggestion


@admin_router.post(
    "/moderation/{article_id}/review",
    response_model=ArticleOut,
    dependencies=[Depends(require_role("admin"))],
)
async def moderate_article(article_id: int, action: str):
    return await moderate_article_service(article_id, action)


# Analytics endpoint


@admin_router.get("/analytics", dependencies=[Depends(require_role("admin"))])
async def get_analytics():
    return await get_analytics_stats()


# System health monitoring endpoint


@admin_router.get("/health", dependencies=[Depends(require_role("admin"))])
async def system_health():
    return await get_system_health()
