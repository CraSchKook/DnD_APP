from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.event_template import EventTemplate as EventTemplateModel
from app.schemas.event_template import EventTemplateCreate, EventTemplateRead, EventTemplateUpdate

router = APIRouter(prefix="/event_templates", tags=["EventTemplates"])

@router.get("/", response_model=list[EventTemplateRead])
async def list_event_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EventTemplateModel))
    return result.scalars().all()


@router.get("/{template_id}", response_model=EventTemplateRead)
async def read_event_template(template_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EventTemplateModel).where(EventTemplateModel.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(404, detail="EventTemplate not found")
    return template


@router.post("/", response_model=EventTemplateRead, status_code=201)
async def create_event_template(
    data: EventTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    template = EventTemplateModel(**data.dict())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.put("/{template_id}", response_model=EventTemplateRead)
async def update_event_template(
    template_id: int,
    data: EventTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EventTemplateModel).where(EventTemplateModel.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(404, detail="EventTemplate not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_event_template(template_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EventTemplateModel).where(EventTemplateModel.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(404, detail="EventTemplate not found")

    await db.delete(template)
    await db.commit()
