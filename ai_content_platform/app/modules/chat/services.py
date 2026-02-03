from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ai_content_platform.app.modules.chat.models import (
    Conversation,
    Message,
    TokenUsage,
)
from ai_content_platform.app.modules.chat.models import TokenUsage
from ai_content_platform.app.modules.chat.gemini_service import gemini_service
from typing import List, Optional
from fastapi import HTTPException
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)


async def start_conversation(
    db: AsyncSession, user_id: int, title: Optional[str] = None
) -> Conversation:
    logger.info(f"Starting conversation for user: {user_id}")
    try:
        conv = Conversation(user_id=user_id, title=title)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        logger.info(
            f"Conversation started for user: {user_id}, conversation_id: {conv.id}"
        )
        return conv
    except Exception as e:
        logger.error(
            f"Error starting conversation for user {user_id}: {e}", exc_info=True
        )
        raise


async def add_message(
    db: AsyncSession, conversation_id: int, sender: str, content: str
) -> Message:
    logger.info(f"Adding message to conversation {conversation_id} from {sender}")
    try:
        msg = Message(conversation_id=conversation_id, sender=sender, content=content)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        logger.info(
            f"Message added to conversation {conversation_id}, message_id: {msg.id}"
        )
        return msg
    except Exception as e:
        logger.error(
            f"Error adding message to conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


async def get_conversation(
    db: AsyncSession, conversation_id: int
) -> Optional[Conversation]:
    logger.info(f"Fetching conversation {conversation_id}")
    try:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        # Force load messages to avoid lazy loading
        _ = getattr(conversation, "messages", None)
        return conversation
    except Exception as e:
        logger.error(
            f"Error fetching conversation {conversation_id}: {e}", exc_info=True
        )
        raise


async def get_user_conversations(db: AsyncSession, user_id: int) -> List[Conversation]:
    logger.info(f"Fetching conversations for user {user_id}")
    try:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.user_id == user_id)
        )
        conversations = result.scalars().all()
        # Force load messages for each conversation
        for conv in conversations:
            _ = getattr(conv, "messages", None)
        return conversations
    except Exception as e:
        logger.error(
            f"Error fetching conversations for user {user_id}: {e}", exc_info=True
        )
        raise


async def get_conversation_messages(
    db: AsyncSession, conversation_id: int, limit: Optional[int] = None
) -> List[Message]:
    logger.info(f"Fetching messages for conversation {conversation_id}")
    try:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
    except Exception as e:
        logger.error(
            f"Error fetching messages for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


async def get_summary_memory(db: AsyncSession, conversation_id: int) -> str:
    """
    Return the stored summary from the Conversation DB row. Never recompute in the response path.
    """
    logger.info(f"Fetching summary memory for conversation {conversation_id}")
    try:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalars().first()
        return conversation.summary or ""
    except Exception as e:
        logger.error(
            f"Error fetching summary memory for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


# Background summary update logic
async def update_conversation_summary(
    db: AsyncSession, conversation_id: int, threshold: int = 10
):
    logger.info(f"Updating conversation summary for conversation {conversation_id}")
    try:
        # Lock the conversation row for update to prevent concurrent summary
        # updates
        conv_result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        )
        conversation = conv_result.scalars().first()
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            raise HTTPException(status_code=404, detail="Conversation not found")
        last_msg_count = conversation.summary_msg_count or 0
        # Count total messages
        total_count_result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.sender.in_(["assistant", "user"]),
            )
        )
        total_count = total_count_result.scalars().all()
        msg_count = len(total_count)

        # Only update summary if message count crosses threshold or summary is
        # missing
        if (
            not conversation.summary
            or msg_count // threshold > last_msg_count // threshold
        ):
            # Fetch only new messages (unsummarized)
            new_msgs_result = await db.execute(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.sender.in_(["assistant", "user"]),
                )
                .order_by(Message.created_at.asc())
                .offset(last_msg_count)
            )
            new_messages = new_msgs_result.scalars().all()

            if not conversation.summary:
                # First summary: summarize all messages
                prompt = (
                    "Summarize the following conversation between user and assistant in a concise way for future context. "
                    "Format: {role: ..., content: ...} list.\n"
                    + str(
                        [{"role": m.sender, "content": m.content} for m in total_count]
                    )
                )
                summary = await gemini_service.generate_text(prompt)
            else:
                # Incremental summary: extend existing summary with new
                # messages
                prompt = (
                    f"Existing summary:\n{conversation.summary}\n\n"
                    f"New messages:\n{str([{'role': m.sender, 'content': m.content} for m in new_messages])}\n\n"
                    "Update the summary to include the new messages, keeping it concise for future context."
                )
                summary = await gemini_service.generate_text(prompt)
            summary = summary[:1000]
            conversation.summary = summary
            conversation.summary_msg_count = msg_count
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        logger.info(f"Conversation summary updated for conversation {conversation_id}")
    except Exception as e:
        logger.error(
            f"Error updating conversation summary for {conversation_id}: {e}",
            exc_info=True,
        )
        raise


async def get_retrieval_context(
    db: AsyncSession, conversation_id: int, keywords: List[str]
) -> List[str]:
    logger.info(
        f"Fetching retrieval context for conversation {conversation_id} with keywords: {keywords}"
    )
    try:
        # Search for messages containing keywords, deduplicate by content
        context_set = set()
        for kw in keywords:
            result = await db.execute(
                select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.content.ilike(f"%{kw}%"),
                )
            )
            for m in result.scalars().all():
                context_set.add(m.content)
        return list(context_set)[:5]  # Limit to top 5 relevant messages
    except Exception as e:
        logger.error(
            f"Error fetching retrieval context for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


async def track_token_usage(
    db: AsyncSession, conversation_id: int, user_id: int, tokens: int
):
    logger.info(
        f"Tracking token usage for conversation {conversation_id}, user {user_id}, tokens {tokens}"
    )
    try:
        usage = TokenUsage(
            conversation_id=conversation_id, user_id=user_id, tokens_used=tokens
        )
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        logger.info(
            f"Token usage tracked for conversation {conversation_id}, usage_id: {usage.id}"
        )
        return usage
    except Exception as e:
        logger.error(
            f"Error tracking token usage for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


# Streaming/AI integration using Gemini streaming with context window control
async def stream_ai_response(
    db: AsyncSession,
    conversation_id: int,
    prompt: str,
    last_n: int = 10,
    use_summary: bool = True,
    retrieval_keywords: Optional[List[str]] = None,
):
    """
    Async generator yielding streaming response chunks from Gemini.
    Context window includes last N messages, summary memory, and retrieval-based context.
    """
    logger.info(f"Streaming AI response for conversation {conversation_id}")
    try:
        # Last N messages
        last_messages = await get_conversation_messages(
            db, conversation_id, limit=last_n
        )
        last_context = [f"{m.sender.capitalize()}: {m.content}" for m in last_messages]
        # Summary memory (incremental, stored in DB, pure read)
        summary = await get_summary_memory(db, conversation_id) if use_summary else ""
        # Retrieval-based context
        retrieval_context = []
        if retrieval_keywords:
            retrieval_context = await get_retrieval_context(
                db, conversation_id, retrieval_keywords
            )
        # Build full context
        context_parts = []
        if summary:
            context_parts.append(f"Summary: {summary}")
        if last_context:
            context_parts.append("Last messages:\n" + "\n".join(last_context))
        if retrieval_context:
            context_parts.append("Relevant context:\n" + "\n".join(retrieval_context))
        full_context = "\n\n".join(context_parts)
        full_prompt = f"{full_context}\n\nUser: {prompt}"
        async for chunk in gemini_service.generate_streaming_text(full_prompt):
            yield chunk
    except Exception as e:
        logger.error(
            f"Error streaming AI response for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise


async def get_token_usage(db: AsyncSession, conversation_id: int):
    logger.info(f"Fetching token usage for conversation {conversation_id}")
    try:
        result = await db.execute(
            select(TokenUsage).where(TokenUsage.conversation_id == conversation_id)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(
            f"Error fetching token usage for conversation {conversation_id}: {e}",
            exc_info=True,
        )
        raise
