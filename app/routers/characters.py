from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.character import Character as CharacterModel
from app.models.ability import Ability as AbilityModel
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterRead
from app.models.inventory import Inventory as InventoryModel
from app.schemas.inventory import InventoryGroup

# Импортируем get_current_user, чтобы «узнавать» player из JWT
from app.core.auth import get_current_user
from app.models.player import Player as PlayerModel

# Импортируем модели Race, Profession, Level
from app.models.race import Race as RaceModel
from app.models.profession import Profession as ProfessionModel
from app.models.level import Level as LevelModel

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
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.player_id == current_user.id)
        .options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
    )
    return result.scalars().all()


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть одного персонажа по ID вместе с его способностями.
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character_id)
        .options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
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
    1. Проверяем, что race_id, profession_id, level_id существуют.
    2. Сохраняем все поля, включая «финальные» статы, которые прислал фронтенд.
    """
    # --- Шаг 1: проверка существования Race, Class, Level ---
    result_race = await db.execute(select(RaceModel).where(RaceModel.id == new_char.race_id))
    race_obj = result_race.scalar_one_or_none()
    if not race_obj:
        raise HTTPException(status_code=404, detail="Race not found")

    result_prof = await db.execute(select(ProfessionModel).where(ProfessionModel.id == new_char.profession_id)) # это класс в системе днд
    prof_obj = result_prof.scalar_one_or_none()
    if not prof_obj:
        raise HTTPException(status_code=404, detail="Profession not found")

    result_lvl = await db.execute(select(LevelModel).where(LevelModel.id == new_char.level_id))
    lvl_obj = result_lvl.scalar_one_or_none()
    if not lvl_obj:
        raise HTTPException(status_code=404, detail="Level not found")

    # --- Шаг 2: создаём модель с данными из запроса ---
    character = CharacterModel(
        name=new_char.name,
        player_id=None if new_char.is_npc else current_user.id,
        session_id=new_char.session_id,
        race_id=new_char.race_id,
        profession_id=new_char.profession_id,
        level_id=new_char.level_id,
        is_npc=new_char.is_npc,
        avatar_url=new_char.avatar_url,
        hp=new_char.hp,
        armor=new_char.armor,
        strength=new_char.strength,
        dexterity=new_char.dexterity,
        constitution=new_char.constitution,
        intelligence=new_char.intelligence,
        wisdom=new_char.wisdom,
        charisma=new_char.charisma,
        shards=new_char.shards
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

    # Повторная загрузка с .options(selectinload(...))
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character.id)
        .options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
    )
    return result.scalar_one()


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

    if character.player_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")

    # Обновляем поля, переданные в запросе
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

    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character.id)
        .options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
    )
    return result.scalar_one()


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int,
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить персонажа, но только если текущий пользователь — его владелец.
    """
    result = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.player_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your character")

    await db.delete(character)
    await db.commit()


@router.get("/{character_id}/inventory", response_model=InventoryGroup)
async def character_inventory(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Вернуть инвентарь персонажа в виде:
    {
      "id": <character_id>,
      "character_id": <character_id>,
      "items": [
        { "id": <inv_id>, "quantity": <int>, "equipped": <bool>, "item": { … } },
        …
      ]
    }
    """
    # Проверка существования персонажа и прав
    result_char = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result_char.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    if character.player_id != current_user.id and current_user.active_as != "master":
        raise HTTPException(status_code=403, detail="Not your character")

    # Грузим записи инвентаря вместе с деталями item
    res_inv = await db.execute(
        select(InventoryModel)
        .where(InventoryModel.character_id == character_id)
        .options(selectinload(InventoryModel.item))
    )
    inv_items = res_inv.scalars().all()

    return InventoryGroup(
        id=character_id,
        character_id=character_id,
        items=inv_items
    )


@router.get("/", response_model=List[CharacterRead])
async def get_all_characters(
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(require_active_as("master"))
):
    """
    Вернуть всех персонажей, - доступно мастеру
    """
    result = await db.execute(
        select(CharacterModel).options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
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
        .options(
            selectinload(CharacterModel.race),
            selectinload(CharacterModel.profession),
            selectinload(CharacterModel.level),
            selectinload(CharacterModel.abilities),
            selectinload(CharacterModel.inventory_items),
        )
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
