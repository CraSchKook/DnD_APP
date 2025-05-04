from fastapi import APIRouter, Depends
from app.schemas.session import Session
from app.dependencies.session_db import FakeSessionDatabase, get_session_db
from datetime import datetime

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.get("/", response_model=list[Session])
async def get_sessions(db: FakeSessionDatabase = Depends(get_session_db)):
    return db.list_sessions()

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: int, db: FakeSessionDatabase = Depends(get_session_db)):
    return db.get_session(session_id)

@router.post("/", response_model=Session, status_code=201)
async def create_session(session: Session, db: FakeSessionDatabase = Depends(get_session_db)):
    return db.create_session(session)

@router.put("/{session_id}", response_model=Session)
async def update_session(session_id: int, updated: Session, db: FakeSessionDatabase = Depends(get_session_db)):
    return db.update_session(session_id, updated)

@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int, db: FakeSessionDatabase = Depends(get_session_db)):
    db.delete_session(session_id)
    return
