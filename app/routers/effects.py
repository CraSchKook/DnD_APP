from fastapi import APIRouter, Depends
from app.schemas.effect import Effect
from app.dependencies.effect_db import FakeEffectDatabase, get_effect_db

router = APIRouter(
    prefix="/effects",
    tags=["Effects"]
)

@router.get("/", response_model=list[Effect])
async def get_effects(db: FakeEffectDatabase = Depends(get_effect_db)):
    return db.list_effects()

@router.get("/{effect_id}", response_model=Effect)
async def get_effect(effect_id: int, db: FakeEffectDatabase = Depends(get_effect_db)):
    return db.get_effect(effect_id)

@router.post("/", response_model=Effect, status_code=201)
async def create_effect(effect: Effect, db: FakeEffectDatabase = Depends(get_effect_db)):
    return db.create_effect(effect)

@router.put("/{effect_id}", response_model=Effect)
async def update_effect(effect_id: int, updated: Effect, db: FakeEffectDatabase = Depends(get_effect_db)):
    return db.update_effect(effect_id, updated)

@router.delete("/{effect_id}", status_code=204)
async def delete_effect(effect_id: int, db: FakeEffectDatabase = Depends(get_effect_db)):
    db.delete_effect(effect_id)
    return
