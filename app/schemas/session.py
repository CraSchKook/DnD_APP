from pydantic import BaseModel
from datetime import datetime

class SessionBase(BaseModel):
    name: str
    description: str | None = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SessionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
