from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.session_service import (
    get_all_sessions,
    get_session_by_id,
    create_session,
    update_session,
    delete_session
)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.get("/", response_model=list[SessionRead])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    return await get_all_sessions(db)

@router.get("/{session_id}", response_model=SessionRead)
async def read_session(session_id: int, db: AsyncSession = Depends(get_db)):
    return await get_session_by_id(session_id, db)

@router.post("/", response_model=SessionRead, status_code=201)
async def add_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    return await create_session(data, db)

@router.put("/{session_id}", response_model=SessionRead)
async def edit_session(session_id: int, data: SessionUpdate, db: AsyncSession = Depends(get_db)):
    return await update_session(session_id, data, db)

@router.delete("/{session_id}", status_code=204)
async def remove_session(session_id: int, db: AsyncSession = Depends(get_db)):
    await delete_session(session_id, db)
