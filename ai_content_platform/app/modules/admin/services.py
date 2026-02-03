# Admin dashboard services for user management, content moderation,
# analytics, and system health monitoring
from ai_content_platform.app.shared.logging import get_logger
from fastapi import HTTPException
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.modules.users.models import User
from ai_content_platform.app.modules.users.schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from ai_content_platform.app.modules.users.services import (
    get_user_by_username,
    get_password_hash,
    create_user,
)
from ai_content_platform.app.modules.content.models import Article
from ai_content_platform.app.modules.content.services import (
    create_article,
    list_articles,
    update_article,
    delete_article,
)
from ai_content_platform.app.modules.content.gemini_service import GeminiService
from ai_content_platform.app.modules.content.schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleOut,
)
from ai_content_platform.app.modules.chat.models import Conversation
from ai_content_platform.app.modules.chat.services import get_token_usage
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import os
import traceback

logger = get_logger(__name__)

# User management


async def get_all_users():
    logger.info("Fetching all users from database")
    try:
        async for db in get_db():
            # Eager-load roles if UserOut expects them
            result = await db.execute(select(User).options(selectinload(User.roles)))
            users = result.scalars().all()
            logger.info(f"Fetched {len(users)} users")
            return [UserOut.model_validate(u) for u in users]
            break
    except Exception as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        raise


async def create_user_service(user: UserCreate):
    logger.info(f"Creating user: {user.username}")
    try:
        async for db in get_db():
            existing = await get_user_by_username(db, user.username)
            if existing:
                logger.error(f"Username already exists: {user.username}")
                raise HTTPException(status_code=400, detail="Username already exists")
            new_user = await create_user(db, user)
            logger.info(f"User created: {user.username}")
            return UserOut.model_validate(new_user)
            break
    except Exception as e:
        logger.error(f"Error creating user {user.username}: {e}", exc_info=True)
        raise


async def update_user_service(user_id: int, update: UserUpdate):
    logger.info(f"Updating user: {user_id}")
    try:
        async for db in get_db():
            user = await db.get(User, user_id)
            if not user:
                logger.error(f"User not found: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            if update.username:
                user.username = update.username
            if update.password:
                user.hashed_password = get_password_hash(update.password)
            if update.avatar:
                user.avatar = update.avatar
            await db.commit()
            await db.refresh(user)
            logger.info(f"User updated: {user_id}")
            return UserOut.model_validate(user)
            break
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        raise


async def delete_user_service(user_id: int):
    logger.info(f"Deleting user: {user_id}")
    try:
        async for db in get_db():
            user = await db.get(User, user_id)
            if not user:
                logger.error(f"User not found: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            await db.delete(user)
            await db.commit()
            logger.info(f"User deleted: {user_id}")
            return None
            break
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
        raise


# Article management


async def get_all_articles():
    logger.info("Fetching all articles from database")
    try:
        async for db in get_db():
            # Eager-load tags if ArticleOut expects them
            stmt = select(Article).options(selectinload(Article.tags))
            result = await db.execute(stmt)
            articles = result.scalars().all()
            logger.info(f"Fetched {len(articles)} articles")
            return [ArticleOut.model_validate(a) for a in articles]
            break
    except Exception as e:
        logger.error(f"Error fetching articles: {e}", exc_info=True)
        raise


async def create_article_service(article: ArticleCreate):
    logger.info(f"Creating article: {article.title}")
    try:
        async for db in get_db():
            new_article = await create_article(
                db, article.title, article.content, article.summary, article.tag_names
            )
            logger.info(f"Article created: {article.title}")
            return ArticleOut.model_validate(new_article)
            break
    except Exception as e:
        logger.error(f"Error creating article {article.title}: {e}", exc_info=True)
        raise


async def update_article_service(article_id: int, update: ArticleUpdate):
    logger.info(f"Updating article: {article_id}")
    try:
        async for db in get_db():
            updated = await update_article(
                db, article_id, **update.dict(exclude_unset=True)
            )
            if not updated:
                logger.error(f"Article not found: {article_id}")
                raise HTTPException(status_code=404, detail="Article not found")
            logger.info(f"Article updated: {article_id}")
            return ArticleOut.model_validate(updated)
            break
    except Exception as e:
        logger.error(f"Error updating article {article_id}: {e}", exc_info=True)
        raise


async def delete_article_service(article_id: int):
    logger.info(f"Deleting article: {article_id}")
    try:
        async for db in get_db():
            ok = await delete_article(db, article_id)
            if not ok:
                logger.error(f"Article not found: {article_id}")
                raise HTTPException(status_code=404, detail="Article not found")
            logger.info(f"Article deleted: {article_id}")
            return {"detail": "Deleted"}
            break
    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}", exc_info=True)
        raise


# Moderation


async def get_flagged_content():
    logger.info("Fetching flagged content")
    try:
        async for db in get_db():
            # Eager-load tags for flagged articles if needed
            result = await db.execute(
                select(Article)
                .options(selectinload(Article.tags))
                .where(Article.flagged)
            )
            flagged = result.scalars().all()
            logger.info(f"Fetched {len(flagged)} flagged articles")
            return [ArticleOut.model_validate(a) for a in flagged]
            break
    except Exception as e:
        logger.error(f"Error fetching flagged content: {e}", exc_info=True)
        raise


async def moderate_article_service(article_id: int, action: str):
    logger.info(f"Moderating article: {article_id} with action: {action}")
    try:
        async for db in get_db():
            # Eager-load tags for moderation if needed
            result = await db.execute(
                select(Article)
                .options(selectinload(Article.tags))
                .where(Article.id == article_id)
            )
            article = result.scalar_one_or_none()
            if not article:
                logger.error(f"Article not found: {article_id}")
                raise HTTPException(status_code=404, detail="Article not found")
            gemini_api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
            gemini_service = GeminiService(api_key=gemini_api_key)
            prompt = f"Should the following article be approved or rejected for publication?\nContent: {article.content}"
            ai_suggestion = await gemini_service.generate_text(prompt)
            if action == "approve":
                article.flagged = False
                article.summary = (article.summary or "") + "\n[Approved by admin]"
            elif action == "reject":
                article.flagged = True
                article.summary = (article.summary or "") + "\n[Rejected by admin]"
            else:
                logger.error(f"Invalid moderation action: {action}")
                raise HTTPException(status_code=400, detail="Invalid action")
            await db.commit()
            await db.refresh(article)
            article.summary += f"\n[AI Suggestion: {ai_suggestion}]"
            logger.info(
                f"Moderation complete for article: {article_id} with action: {action}"
            )
            return ArticleOut.model_validate(article)
            break
    except Exception as e:
        logger.error(f"Error moderating article {article_id}: {e}", exc_info=True)
        raise


# Analytics


async def get_analytics_stats():
    logger.info("Fetching analytics stats")
    try:
        async for db in get_db():
            user_count = (await db.execute(func.count(User.id))).scalar()
            article_count = (await db.execute(func.count(Article.id))).scalar()
            conv_result = await db.execute(select(Conversation.id))
            conversation_ids = [row[0] for row in conv_result.fetchall()]
            ai_usage = 0
            for conv_id in conversation_ids:
                token_usages = await get_token_usage(db, conv_id)
                ai_usage += sum(tu.tokens_used for tu in token_usages)
            logger.info(
                f"Analytics: users={user_count}, articles={article_count}, ai_usage={ai_usage}"
            )
            return {
                "users": user_count,
                "articles": article_count,
                "ai_usage": ai_usage,
            }
            break
    except Exception as e:
        logger.error(f"Error fetching analytics stats: {e}", exc_info=True)
        raise


# System health


async def get_system_health():
    logger.info("Checking system health")
    try:
        async for db in get_db():
            try:
                user_count = (await db.execute(func.count(User.id))).scalar()
                status = "healthy"
                details = f"User count: {user_count}"
                errors = []
                logger.info(f"System health: {status}, {details}")
            except Exception as e:
                status = "unhealthy"
                details = str(e)
                errors = [traceback.format_exc()]
                logger.error(f"System health check failed: {details}")
            return {"status": status, "details": details, "errors": errors}
            break
    except Exception as e:
        logger.error(f"Error checking system health: {e}", exc_info=True)
        raise
