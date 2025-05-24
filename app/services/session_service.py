# app/services/session_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate

async def get_all_sessions(db: AsyncSession):
    result = await db.execute(select(SessionModel))
    return result.scalars().all()

async def get_session_by_id(session_id: int, db: AsyncSession):
    result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

async def create_session(data: SessionCreate, db: AsyncSession):
    session = SessionModel(name=data.name, description=data.description or "")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def update_session(session_id: int, data: SessionUpdate, db: AsyncSession):
    session = await get_session_by_id(session_id, db)
    if data.name is not None:
        session.name = data.name
    if data.description is not None:
        session.description = data.description
    await db.commit()
    await db.refresh(session)
    return session

async def delete_session(session_id: int, db: AsyncSession):
    session = await get_session_by_id(session_id, db)
    await db.delete(session)
    await db.commit()
