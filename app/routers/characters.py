from fastapi import APIRouter, Depends
from app.schemas.character import Character
from app.dependencies.character_db import FakeCharacterDatabase, get_character_db

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)

@router.get("/", response_model=list[Character])
async def get_characters(db: FakeCharacterDatabase = Depends(get_character_db)):
    return db.list_characters()

@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: int, db: FakeCharacterDatabase = Depends(get_character_db)):
    return db.get_character(character_id)

@router.post("/", response_model=Character, status_code=201)
async def create_character(character: Character, db: FakeCharacterDatabase = Depends(get_character_db)):
    return db.create_character(character)

@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: int, updated: Character, db: FakeCharacterDatabase = Depends(get_character_db)):
    return db.update_character(character_id, updated)

@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int, db: FakeCharacterDatabase = Depends(get_character_db)):
    db.delete_character(character_id)
    return
