
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ai_content_platform.app.modules.content.models import Article, Tag
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os
from ai_content_platform.app.modules.content.gemini_service import GeminiService
from ai_content_platform.app.shared.logging import get_logger
logger = get_logger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
gemini_service = GeminiService(api_key=GEMINI_API_KEY)



async def create_article(db: AsyncSession, title: str, content: str, summary: Optional[str], tag_names: Optional[List[str]] = None, flagged: bool = False):
    logger.info(f"Creating article: {title}")
    try:
        article = Article(title=title, content=content, summary=summary, flagged=flagged)
        tags = []
        if tag_names:
            tag_names = list({name.strip().lower() for name in tag_names if name.strip()})
            if tag_names:
                result = await db.execute(select(Tag).where(Tag.name.in_(tag_names)))
                existing_tags = result.scalars().all()
                existing_names = {t.name for t in existing_tags}
                new_tags = [Tag(name=name) for name in tag_names if name not in existing_names]
                db.add_all(new_tags)
                await db.flush()
                tags = existing_tags + new_tags
        article.tags = tags
        db.add(article)
        await db.commit()
        # Eagerly load tags before returning
        stmt = (
            select(Article)
            .options(selectinload(Article.tags))
            .where(Article.id == article.id)
        )
        result = await db.execute(stmt)
        article = result.scalars().first()
        logger.info(f"Article created: {title}, id: {article.id}")
        return article
    except Exception as e:
        logger.error(f"Error creating article {title}: {e}", exc_info=True)
        raise

async def get_article(db: AsyncSession, article_id: int):
    logger.info(f"Fetching article: {article_id}")
    try:
        stmt = (
            select(Article)
            .options(selectinload(Article.tags))
            .where(Article.id == article_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}", exc_info=True)
        raise

async def update_article(db: AsyncSession, article_id: int, **kwargs):
    logger.info(f"Updating article: {article_id}")
    try:
        stmt = (
                select(Article)
                .options(selectinload(Article.tags))  
                .where(Article.id == article_id)
            )  
        result = await db.execute(stmt)
        article = result.scalars().first()
        if not article:
            logger.warning(f"Article not found: {article_id}")
            return None
        tag_names = kwargs.pop("tag_names", None)
        for key, value in kwargs.items():
            if hasattr(article, key) and value is not None:
                setattr(article, key, value)
        if tag_names is not None:
            tag_names = list({name.strip().lower() for name in tag_names if name.strip()})
            result = await db.execute(select(Tag).where(Tag.name.in_(tag_names)))
            existing_tags = result.scalars().all()
            existing_names = {t.name for t in existing_tags}
            new_tags = [Tag(name=name) for name in tag_names if name not in existing_names]
            db.add_all(new_tags)
            await db.flush()
            article.tags = existing_tags + new_tags
        await db.commit()
        # Eagerly load tags before returning
        stmt = (
            select(Article)
            .options(selectinload(Article.tags))
            .where(Article.id == article.id)
        )
        result = await db.execute(stmt)
        logger.info(f"Article updated: {article_id}")
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error updating article {article_id}: {e}", exc_info=True)
        raise

async def delete_article(db: AsyncSession, article_id: int):
    logger.info(f"Deleting article: {article_id}")
    try:
        article = await db.get(Article, article_id)
        if not article:
            logger.warning(f"Article not found: {article_id}")
            return False
        await db.delete(article)
        await db.commit()
        logger.info(f"Article deleted: {article_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}", exc_info=True)
        raise

async def list_articles(db: AsyncSession):
    logger.info("Listing all articles")
    try:
        stmt = select(Article).options(selectinload(Article.tags))
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error listing articles: {e}", exc_info=True)
        raise

async def create_tag(db: AsyncSession, name: str):
    logger.info(f"Creating tag: {name}")
    try:
        tag = Tag(name=name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        logger.info(f"Tag created: {name}, id: {tag.id}")
        return tag
    except Exception as e:
        logger.error(f"Error creating tag {name}: {e}", exc_info=True)
        raise

async def list_tags(db: AsyncSession):
    logger.info("Listing all tags")
    try:
        result = await db.execute(select(Tag))
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error listing tags: {e}", exc_info=True)
        raise

async def search_articles(db: AsyncSession, query: str):
    logger.info(f"Searching articles with query: {query}")
    try:
        # Simple LIKE search; for production use FTS
        stmt = (
            select(Article)
            .options(selectinload(Article.tags))
            .where(Article.title.ilike(f"%{query}%") | Article.content.ilike(f"%{query}%"))
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error searching articles with query '{query}': {e}", exc_info=True)
        raise


async def ai_generate_article(db: AsyncSession, title: str, content: str, summary: Optional[str], tag_names: Optional[List[str]] = None, prompt: Optional[str] = None):
    """
    Generate article content and summary using Gemini AI, then create the article.
    Flagged=True for AI-generated content.
    """
    logger.info(f"AI generate article called for title: {title}")
    try:
        if not prompt:
            prompt = f"Generate a detailed article on the topic: '{title}'. Content: {content}"
        ai_content = await gemini_service.generate_text(prompt)
        ai_summary = await gemini_service.generate_text(f"Summarize the following article in 2-3 sentences: {ai_content}")
        return await create_article(db, title, ai_content, ai_summary, tag_names, flagged=True)
    except Exception as e:
        logger.error(f"Error in ai_generate_article for title '{title}': {e}", exc_info=True)
        raise

async def ai_summarize_article(db: AsyncSession, article_id: int):
    logger.info(f"AI summarize article called for article_id: {article_id}")
    try:
        article = await get_article(db, article_id)
        if not article:
            logger.warning(f"Article not found for summarization: {article_id}")
            return None
        summary_prompt = f"Summarize the following article in 2-3 sentences: {article.content}"
        ai_summary = await gemini_service.generate_text(summary_prompt)
        article.summary = ai_summary
        await db.commit()
        await db.refresh(article)
        logger.info(f"Article summarized: {article_id}")
        return article
    except Exception as e:
        logger.error(f"Error in ai_summarize_article for article_id {article_id}: {e}", exc_info=True)
        raise