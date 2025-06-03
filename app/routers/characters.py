from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.character import Character as CharacterModel
from app.models.ability import Ability as AbilityModel
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterRead
from app.schemas.inventory import InventoryRead
from app.models.inventory import Inventory as InventoryModel

# Импортируем get_current_user, чтобы «узнавать» player из JWT
from app.core.auth import get_current_user
from app.models.player import Player as PlayerModel

# Импортируем модели Race, Profession, Level
from app.models.race import Race as RaceModel
from app.models.profession import Profession as ProfessionModel
from app.models.level import Level as LevelModel

# Импортируем функцию, которая рассчитает финальные статы:
from app.core.rules import compute_final_stats

# Импортируем функцию, которая определяет роль пользователя Игрок/Мастер:
from app.core.roles import require_active_as

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)

@router.get("/me", response_model=List[CharacterRead])
async def list_my_characters(
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Вернуть всех персонажей, принадлежащих текущему (залогиненному) игроку.
    """
    # selectinload загружает способности сразу вместе с персонажем
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.player_id == current_user.id)
        .options(selectinload(CharacterModel.abilities))
    )
    return result.scalars().all()


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть одного персонажа по ID вместе с его способностями.
    (Обратите внимание: здесь потенциально можно добавить проверку,
    что этот character.player_id == current_user.id, но для простоты —
    оставим базовый вариант.)
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character_id)
        .options(selectinload(CharacterModel.abilities))
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/", response_model=CharacterRead, status_code=201)
async def create_character(
    new_char: CharacterCreate,
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать нового персонажа. 
    Логика:
    1. Проверяем, что race_id, class_id, level_id существуют.
    2. Проверяем, что new_char.player_id == current_user.id (в Body он не передаёт player_id, 
       ибо мы его берём из JWT). 
    3. Расчитываем финальные статы через compute_final_stats:
       compute_final_stats(race, cls, level, strength_user, dexterity_user, …)
    4. Сохраняем персонажа с финальными stats.
    """

    # --- Шаг 1: проверка существования Race, Class, Level ---
    result_race = await db.execute(select(RaceModel).where(RaceModel.id == new_char.race_id))
    race_obj = result_race.scalar_one_or_none()
    if not race_obj:
        raise HTTPException(status_code=404, detail="Race not found")

    result_cls = await db.execute(select(ProfessionModel).where(ProfessionModel.id == new_char.profession_id))
    cls_obj = result_cls.scalar_one_or_none()
    if not cls_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    result_lvl = await db.execute(select(LevelModel).where(LevelModel.id == new_char.level_id))
    lvl_obj = result_lvl.scalar_one_or_none()
    if not lvl_obj:
        raise HTTPException(status_code=404, detail="Level not found")

    # --- Шаг 2: проверка, что player_id совпадает с current_user.id ---
    # (У вас new_char не содержит player_id, потому что player_id мы берём из JWT)
    # Однако, если вы вдруг добавили поле player_id в CharacterCreate, можно его игнорировать:
    # if new_char.player_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Cannot create character for another user")

    # --- Шаг 3: вычисление финальных статов ---
    final_stats = compute_final_stats(
        race_obj,
        cls_obj,
        lvl_obj,
        strength_user=new_char.strength_user,
        dexterity_user=new_char.dexterity_user,
        constitution_user=new_char.constitution_user,
        intelligence_user=new_char.intelligence_user,
        wisdom_user=new_char.wisdom_user,
        charisma_user=new_char.charisma_user
    )
    # compute_final_stats вернул словарь вида:
    # {
    #   "hp": 25,
    #   "armor": 12,
    #   "strength": 15,
    #   "dexterity": 14,
    #   … и т. д.
    # }

    character = CharacterModel(
        name=new_char.name,
        player_id=None if new_char.is_npc else current_user.id,
        session_id=new_char.session_id,
        race_id=new_char.race_id,
        profession_id=new_char.profession_id,
        level_id=new_char.level_id,
        is_npc=new_char.is_npc,
        avatar_url=new_char.avatar_url,
        hp=final_stats["hp"],
        armor=final_stats["armor"],
        strength=final_stats["strength"],
        dexterity=final_stats["dexterity"],
        constitution=final_stats["constitution"],
        intelligence=final_stats["intelligence"],
        wisdom=final_stats["wisdom"],
        charisma=final_stats["charisma"],
    )

    # Присваиваем способности, если они пришли:
    if new_char.ability_ids:
        result_abilities = await db.execute(
            select(AbilityModel).where(AbilityModel.id.in_(new_char.ability_ids))
        )
        character.abilities = result_abilities.scalars().all()

    db.add(character)
    await db.commit()
    await db.refresh(character)
    return character


@router.put("/{character_id}", response_model=CharacterRead)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить данные персонажа и его способности, но только если этот персонаж
    действительно принадлежит текущему пользователю.
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character_id)
        .options(selectinload(CharacterModel.abilities))
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Проверим, что этот character принадлежит текущему пользователю:
    if character.player_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")

    # Обновляем простые поля:
    update_data = data.dict(exclude_unset=True, exclude={"ability_ids"})
    for field, value in update_data.items():
        setattr(character, field, value)

    # Обновляем способности, если переданы:
    if data.ability_ids is not None:
        res = await db.execute(
            select(AbilityModel).where(AbilityModel.id.in_(data.ability_ids))
        )
        character.abilities = res.scalars().all()

    await db.commit()
    await db.refresh(character)  
    return character


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int,
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить персонажа, но только если текущий пользователь — его владелец.
    """
    result = await db.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.player_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")

    await db.delete(character)
    await db.commit()


@router.get("/{character_id}/inventory", response_model=List[InventoryRead])
async def character_inventory(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть список предметов в инвентаре данного персонажа.
    (здесь тоже можно добавить проверку владельца персонажа, если нужно)
    """
    res_char = await db.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    char = res_char.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    res_inv = await db.execute(
        select(InventoryModel).where(InventoryModel.character_id == character_id)
    )
    return res_inv.scalars().all()

@router.get("/", response_model=List[CharacterRead])
async def get_all_characters(
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(require_active_as("master"))  # ← проверка роли
):
    result = await db.execute(
        select(CharacterModel).options(selectinload(CharacterModel.abilities))
    )
    return result.scalars().all()

@router.get("/available-npcs", response_model=List[CharacterRead])
async def list_available_npcs(
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(require_active_as("master"))
):
    """
    Вернуть всех NPC, которые доступны для назначения игрокам.
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.is_npc == True)
        .where(CharacterModel.player_id == None)
        .options(selectinload(CharacterModel.abilities))
    )
    return result.scalars().all()


@router.post("/{character_id}/assign-to-player", status_code=200)
async def assign_npc_to_player(
    character_id: int,
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(require_active_as("master"))
):
    """
    Присвоить NPC игроку.
    - Только мастер может это сделать.
    - NPC становится персонажем (is_npc=False).
    """
    # Найдём персонажа
    result = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    if not character.is_npc:
        raise HTTPException(status_code=400, detail="Character is not an NPC")
    if character.player_id is not None:
        raise HTTPException(status_code=400, detail="NPC already assigned to a player")

    # Проверим, существует ли игрок
    res_player = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = res_player.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Присваиваем
    character.player_id = player.id
    character.is_npc = False

    await db.commit()
    await db.refresh(character)

    return {"detail": f"NPC '{character.name}' теперь принадлежит игроку {player_id}"}

@router.post("/{character_id}/unassign", status_code=200)
async def unassign_character_from_player(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(require_active_as("master"))
):
    """
    Отвязать персонажа от игрока (вернуть в состояние NPC).
    Только мастер может это делать.
    """
    result = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.player_id is None:
        raise HTTPException(status_code=400, detail="Character is not assigned to any player")

    # Отвязываем
    character.player_id = None
    character.is_npc = True

    await db.commit()
    await db.refresh(character)

    return {"detail": f"Персонаж '{character.name}' теперь снова NPC"}
