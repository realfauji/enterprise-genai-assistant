from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.schemas import SessionResponse
from app.core.security import get_current_user
from pathlib import Path

from app.langchain_layer.loaders import load_documents
from app.langchain_layer.splitter import split_documents
from app.langchain_layer.vector_store import add_documents_to_vectorstore
from sqlalchemy import select
import shutil


router = APIRouter(prefix="/sessions", tags=["Sessions"])

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/create", response_model=SessionResponse)
async def create_session(db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    new_session = ChatSession(user_id=current_user.id, title="New Chat")
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return {"session_id": new_session.id, "created_at": new_session.created_at.isoformat()}

@router.post("/upload")
async def upload_document(file:UploadFile = File(...), current_user=Depends(get_current_user)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        documents = load_documents(str(file_path))
        chunks = split_documents(documents)
        add_documents_to_vectorstore(user_id=current_user.id, documents=chunks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Document indexed successfully"}

@router.get("/my-sessions")
async def get_my_sessions(db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()

    response = []
    for index, session in enumerate(sessions, start=1):
        response.append({
            "id": session.id,  # real DB id
            "display_number": index,  # user-wise numbering
            "title": session.title,
            "created_at": session.created_at
        })

    return response

@router.get("/{session_id}/messages")
async def get_session_messages(session_id:int, db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
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

    return [
        {"role": m.role, "content": m.content} for m in messages]
    
@router.put("/{session_id}/rename")
async def rename_session(session_id:int, title:dict, db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = title["title"]
    await db.commit()

    return {"message": "Session renamed"}

@router.delete("/{session_id}")
async def delete_session(session_id:int, db:AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    return {"message": "Session deleted"}
