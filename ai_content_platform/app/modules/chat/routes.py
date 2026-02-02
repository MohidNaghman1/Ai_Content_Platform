from starlette.background import BackgroundTasks
from fastapi.responses import StreamingResponse
from ai_content_platform.app.modules.chat import services
from ai_content_platform.app.modules.chat.schemas import (
    ConversationCreate,
    ConversationOut,
    MessageCreate,
    MessageOut,
    TokenUsageOut,
)
from ai_content_platform.app.shared.dependencies import (
    get_db,
    get_current_user,
    require_permission,
)
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/conversations/",
    response_model=ConversationOut,
    dependencies=[Depends(require_permission("start_chat"))],
)
async def start_conversation(
    conv: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(f"Start conversation endpoint called for user: {user['sub']}")
    try:
        obj = await services.start_conversation(
            db, user_id=user["sub"], title=conv.title
        )
        logger.info(f"Conversation started for user: {user['sub']}")
        return obj
    except Exception as e:
        logger.error(f"Error in start_conversation: {e}", exc_info=True)
        raise


@chat_router.get(
    "/conversations/",
    response_model=List[ConversationOut],
    dependencies=[Depends(require_permission("view_chat"))],
)
async def list_conversations(
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    logger.info(f"List conversations endpoint called for user: {user['sub']}")
    try:
        return await services.get_user_conversations(db, user_id=user["sub"])
    except Exception as e:
        logger.error(f"Error in list_conversations: {e}", exc_info=True)
        raise


@chat_router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationOut,
    dependencies=[Depends(require_permission("view_chat"))],
)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(
        f"Get conversation endpoint called for user: {user['sub']}, conversation_id: {conversation_id}"
    )
    try:
        conv = await services.get_conversation(db, conversation_id)
        if not conv or conv.user_id != user["sub"]:
            logger.warning(
                f"Conversation not found: {conversation_id} for user: {user['sub']}"
            )
            raise HTTPException(404, "Conversation not found")
        return conv
    except Exception as e:
        logger.error(f"Error in get_conversation: {e}", exc_info=True)
        raise


# Streaming AI chat endpoint with context window control
# Improved streaming logic: StreamingResponse is returned immediately, DB
# save is handled after streaming
@chat_router.post(
    "/conversations/{conversation_id}/messages/stream/",
    dependencies=[Depends(require_permission("send_message"))],
)
async def stream_message(
    conversation_id: int,
    msg: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
    last_n: int = 10,
    use_summary: bool = True,
    retrieval_keywords: str = "",
):
    logger.info(
        f"Stream message endpoint called for user: {user['sub']}, conversation_id: {conversation_id}"
    )
    try:
        conv = await services.get_conversation(db, conversation_id)
        if not conv or conv.user_id != user["sub"]:
            logger.warning(
                f"Conversation not found: {conversation_id} for user: {user['sub']}"
            )
            raise HTTPException(404, "Conversation not found")
        # Add user message
        user_msg = await services.add_message(
            db, conversation_id, sender="user", content=msg.content
        )
        # Parse keywords
        keywords = (
            [k.strip() for k in retrieval_keywords.split(",") if k.strip()]
            if retrieval_keywords
            else []
        )

        # Streaming generator with safeguards
        MAX_RESPONSE_CHARS = 4000  # hard limit to prevent memory blowup

        async def ai_stream_accum():
            full_response = ""
            incomplete = False
            try:
                async for chunk in services.stream_ai_response(
                    db,
                    conversation_id,
                    msg.content,
                    last_n=last_n,
                    use_summary=use_summary,
                    retrieval_keywords=keywords,
                ):
                    if len(full_response) + len(chunk) > MAX_RESPONSE_CHARS:
                        # Truncate and stop streaming
                        full_response += chunk[
                            : MAX_RESPONSE_CHARS - len(full_response)
                        ]
                        incomplete = True
                        break
                    full_response += chunk
                    yield chunk
            except Exception as e:
                incomplete = True
                logger.error(f"Error in ai_stream_accum: {e}", exc_info=True)
                raise
            finally:
                ai_stream_accum.full_response = full_response
                ai_stream_accum.incomplete = incomplete

        ai_stream_accum.full_response = ""
        ai_stream_accum.incomplete = False

        async def save_ai_response_and_summary_bg():
            # Create a new DB session for the background task
            async for db_bg in get_db():
                try:
                    # Mark message as incomplete if needed
                    meta_content = ai_stream_accum.full_response
                    if ai_stream_accum.incomplete:
                        meta_content = "[INCOMPLETE] " + meta_content
                    await services.add_message(
                        db_bg, conversation_id, sender="assistant", content=meta_content
                    )
                    await services.track_token_usage(
                        db_bg,
                        conversation_id,
                        user["sub"],
                        tokens=len(msg.content) + len(ai_stream_accum.full_response),
                    )
                    # Only summarize if response is complete
                    if not ai_stream_accum.incomplete:
                        await services.update_conversation_summary(
                            db_bg, conversation_id
                        )
                except Exception as e:
                    logger.error(
                        f"Error in save_ai_response_and_summary_bg: {e}", exc_info=True
                    )
                finally:
                    await db_bg.close()
                break

        background_tasks = BackgroundTasks()
        background_tasks.add_task(save_ai_response_and_summary_bg)
        logger.info(f"Streaming response for conversation_id: {conversation_id}")
        return StreamingResponse(
            ai_stream_accum(), media_type="text/plain", background=background_tasks
        )
    except Exception as e:
        logger.error(f"Error in stream_message: {e}", exc_info=True)
        raise


async def get_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(
        f"Get messages endpoint called for user: {user['sub']}, conversation_id: {conversation_id}"
    )
    try:
        conv = await services.get_conversation(db, conversation_id)
        if not conv or conv.user_id != user["sub"]:
            logger.warning(
                f"Conversation not found: {conversation_id} for user: {user['sub']}"
            )
            raise HTTPException(404, "Conversation not found")
        return await services.get_conversation_messages(db, conversation_id)
    except Exception as e:
        logger.error(f"Error in get_messages: {e}", exc_info=True)
        raise


@chat_router.get(
    "/conversations/{conversation_id}/usage/",
    response_model=List[TokenUsageOut],
    dependencies=[Depends(require_permission("view_usage"))],
)
async def get_token_usage(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    logger.info(
        f"Get token usage endpoint called for user: {user['sub']}, conversation_id: {conversation_id}"
    )
    try:
        conv = await services.get_conversation(db, conversation_id)
        if not conv or conv.user_id != user["sub"]:
            logger.warning(
                f"Conversation not found: {conversation_id} for user: {user['sub']}"
            )
            raise HTTPException(404, "Conversation not found")
        usage_records = await services.get_token_usage(db, conversation_id)
        logger.info(
            f"Token usage records fetched for conversation_id: {conversation_id}"
        )
        return [
            TokenUsageOut(tokens_used=u.tokens_used, created_at=u.created_at)
            for u in usage_records
        ]
    except Exception as e:
        logger.error(f"Error in get_token_usage: {e}", exc_info=True)
        raise
