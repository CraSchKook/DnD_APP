from fastapi import APIRouter, Depends
from typing import List
from app.schemas.theme import Theme
from app.dependencies.db import FakeDatabase, get_db

router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)

@router.get("/", response_model=List[Theme])
def get_themes(db: FakeDatabase = Depends(get_db)):
    return db.list_themes()

@router.post("/", response_model=Theme)
def create_theme(theme: Theme, db: FakeDatabase = Depends(get_db)):
    return db.create_theme(theme)
