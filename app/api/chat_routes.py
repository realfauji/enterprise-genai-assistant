from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.dependencies import get_db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.schemas import ChatMessageCreate
from app.core.security import get_current_user

from app.langchain_layer.vector_store import load_vectorstore
from app.langchain_layer.chains import build_rag_chain, build_simple_llm_chain, create_auto_title

from app.langchain_layer.token_callback import TokenUsageCallback, count_tokens
from app.models.usage_log import UsageLog


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{session_id}")
async def send_message(session_id:int, message:ChatMessageCreate, db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    # Validate session ownership
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=message.content,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    try:
        vectorstore = load_vectorstore(current_user.id)
        docs = vectorstore.similarity_search(message.content, k=4)

        if not docs:
            use_rag = False
        else:
            use_rag = True
    except ValueError:
        vectorstore = None
        use_rag = False

    # Load session history
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
    )
    messages = history_result.scalars().all()

    history_pairs = []
    for i in range(len(messages) - 1):
        if messages[i].role == "user" and messages[i + 1].role == "assistant":
            history_pairs.append(
                (messages[i].content, messages[i + 1].content)
            )
    history_pairs = history_pairs[-5:]

    # Build chain
    token_callback = TokenUsageCallback()
    if use_rag:
        result = build_rag_chain(
            provider=None,   # will use default from .env
            vectorstore=vectorstore,
            question=message.content,
            history_pairs=history_pairs,
            callbacks=[token_callback]
        )
    else:
        result = build_simple_llm_chain(
            provider=None,
            question=message.content,
            history_pairs=history_pairs,
            callbacks=[token_callback]
        )
    answer = result["answer"]

    prompt_text = message.content
    completion_text = answer
    prompt_tokens = count_tokens(prompt_text)
    completion_tokens = count_tokens(completion_text)
    total_tokens = prompt_tokens + completion_tokens
    cost_per_1k_tokens = 0.002
    cost = (total_tokens / 1000) * cost_per_1k_tokens

    # Auto-generate title if first message
    if len(messages) == 0:  # only first user message exists
        short_title = create_auto_title(provider=None, question=message.content)
        result_session = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session_obj = result_session.scalar_one()
        session_obj.title = short_title
        await db.commit()

    # Save assistant message
    assistant_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=answer,
    )
    db.add(assistant_message)
    await db.commit()

    usage = UsageLog(
    user_id=current_user.id,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    total_tokens=total_tokens,
    cost=cost,
    )

    db.add(usage)
    await db.commit()

    return {
        "answer": answer,
        "sources_count": len(result.get("source_documents", [])) if use_rag else 0,
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": total_tokens, "estimated_cost": cost}
    }

@router.get("/{session_id}/history")
async def get_session_history(session_id:int, db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
    )
    messages = messages_result.scalars().all()
    if not messages:
        raise HTTPException(status_code=404, detail="No message history found for this session")

    return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]
