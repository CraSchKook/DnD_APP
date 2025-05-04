from pydantic import BaseModel
from datetime import datetime

class Session(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime