
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ai_content_platform.app.shared.dependencies import get_db, require_permission
from ai_content_platform.app.modules.content.schemas import ArticleCreate, ArticleUpdate, ArticleOut, TagCreate, TagOut
from ai_content_platform.app.modules.content import services
from ai_content_platform.app.shared.logging import get_logger
logger = get_logger(__name__)

content_router = APIRouter(prefix="/content", tags=["content"])

@content_router.post("/articles/", response_model=ArticleOut)
async def create_article(article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Creating article: {article.title}")
    try:
        obj = await services.create_article(db, article.title, article.content, article.summary, article.tag_names)
        return obj
    except Exception as e:
        logger.error(f"API: Error creating article: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create article")

@content_router.get("/articles/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Fetching article: {article_id}")
    try:
        obj = await services.get_article(db, article_id)
        if not obj:
            logger.warning(f"API: Article not found: {article_id}")
            raise HTTPException(404, "Article not found")
        return obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error fetching article {article_id}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to fetch article")

@content_router.put("/articles/{article_id}", response_model=ArticleOut)
async def update_article(article_id: int, update: ArticleUpdate, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Updating article: {article_id}")
    try:
        obj = await services.update_article(db, article_id, **update.dict(exclude_unset=True))
        if not obj:
            logger.warning(f"API: Article not found for update: {article_id}")
            raise HTTPException(404, "Article not found")
        return obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error updating article {article_id}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to update article")

@content_router.delete("/articles/{article_id}")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Deleting article: {article_id}")
    try:
        ok = await services.delete_article(db, article_id)
        if not ok:
            logger.warning(f"API: Article not found for delete: {article_id}")
            raise HTTPException(404, "Article not found")
        return {"detail": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error deleting article {article_id}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to delete article")

@content_router.get("/articles/", response_model=List[ArticleOut])
async def list_articles(db: AsyncSession = Depends(get_db)):
    logger.info("API: Listing all articles")
    try:
        return await services.list_articles(db)
    except Exception as e:
        logger.error(f"API: Error listing articles: {e}", exc_info=True)
        raise HTTPException(500, "Failed to list articles")

@content_router.post("/tags/", response_model=TagOut)
async def create_tag(tag: TagCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Creating tag: {tag.name}")
    try:
        return await services.create_tag(db, tag.name)
    except Exception as e:
        logger.error(f"API: Error creating tag {tag.name}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create tag")

@content_router.get("/tags/", response_model=List[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    logger.info("API: Listing all tags")
    try:
        return await services.list_tags(db)
    except Exception as e:
        logger.error(f"API: Error listing tags: {e}", exc_info=True)
        raise HTTPException(500, "Failed to list tags")

@content_router.get("/articles/search/", response_model=List[ArticleOut])
async def search_articles(q: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: Searching articles with query: {q}")
    try:
        return await services.search_articles(db, q)
    except Exception as e:
        logger.error(f"API: Error searching articles with query '{q}': {e}", exc_info=True)
        raise HTTPException(500, "Failed to search articles")




# AI-powered content generation (permission-based)
@content_router.post(
    "/articles/generate/",
    response_model=ArticleOut,
    dependencies=[Depends(require_permission("generate_content"))]
)
async def generate_article_ai(article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: AI generate article for title: {article.title}")
    try:
        obj = await services.ai_generate_article(db, article.title, article.content, article.summary, article.tag_names)
        return obj
    except Exception as e:
        logger.error(f"API: Error in AI generate article: {e}", exc_info=True)
        raise HTTPException(500, "Failed to generate article with AI")



# AI-powered summarization (permission-based)
@content_router.post(
    "/articles/{article_id}/summarize/",
    response_model=str,
    dependencies=[Depends(require_permission("summarize_content"))]
)
async def summarize_article_ai(article_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"API: AI summarize article for article_id: {article_id}")
    try:
        obj = await services.ai_summarize_article(db, article_id)
        if not obj:
            logger.warning(f"API: Article not found for summarization: {article_id}")
            raise HTTPException(404, "Article not found")
        return obj.summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Error in AI summarize article: {e}", exc_info=True)
        raise HTTPException(500, "Failed to summarize article with AI")
