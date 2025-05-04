from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class EventInstanceBase(BaseModel):
    session_id: int
    template_id: int
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None  # Дополнительные данные события

class EventInstanceCreate(EventInstanceBase):
    pass

class EventInstance(EventInstanceBase):
    id: int

    class Config:
        orm_mode = True
