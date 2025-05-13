from pydantic import BaseModel

class Player(BaseModel):
    id: int | None = None
    name: str

    class Config:
        orm_mode = True  # ← Важно для SQLAlchemy