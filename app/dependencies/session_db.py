from typing import List
from fastapi import HTTPException
from app.schemas.session import Session
from datetime import datetime

class FakeSessionDatabase:
    """In-memory хранилище сессий."""
    def __init__(self):
        self._sessions: List[Session] = []

    def list_sessions(self) -> List[Session]:
        return self._sessions

    def get_session(self, session_id: int) -> Session:
        for s in self._sessions:
            if s.id == session_id:
                return s
        raise HTTPException(status_code=404, detail="Session not found")

    def create_session(self, session: Session) -> Session:
        if any(s.id == session.id for s in self._sessions):
            raise HTTPException(status_code=400, detail="Session with this ID already exists")
        self._sessions.append(session)
        return session

    def update_session(self, session_id: int, updated: Session) -> Session:
        for idx, s in enumerate(self._sessions):
            if s.id == session_id:
                self._sessions[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: int) -> None:
        for idx, s in enumerate(self._sessions):
            if s.id == session_id:
                self._sessions.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Session not found")

# единый экземпляр
fake_session_db = FakeSessionDatabase()

# зависимость
def get_session_db() -> FakeSessionDatabase:
    return fake_session_db
