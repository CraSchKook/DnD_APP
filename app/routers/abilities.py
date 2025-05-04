from fastapi import APIRouter, Depends
from app.schemas.ability import Ability
from app.dependencies.ability_db import FakeAbilityDatabase, get_ability_db

router = APIRouter(
    prefix="/abilities",
    tags=["Abilities"]
)

@router.get("/", response_model=list[Ability])
async def get_abilities(db: FakeAbilityDatabase = Depends(get_ability_db)):
    return db.list_abilities()

@router.get("/{ability_id}", response_model=Ability)
async def get_ability(ability_id: int, db: FakeAbilityDatabase = Depends(get_ability_db)):
    return db.get_ability(ability_id)

@router.post("/", response_model=Ability, status_code=201)
async def create_ability(ability: Ability, db: FakeAbilityDatabase = Depends(get_ability_db)):
    return db.create_ability(ability)

@router.put("/{ability_id}", response_model=Ability)
async def update_ability(ability_id: int, updated: Ability, db: FakeAbilityDatabase = Depends(get_ability_db)):
    return db.update_ability(ability_id, updated)

@router.delete("/{ability_id}", status_code=204)
async def delete_ability(ability_id: int, db: FakeAbilityDatabase = Depends(get_ability_db)):
    db.delete_ability(ability_id)
    return
