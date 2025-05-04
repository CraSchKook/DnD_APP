from fastapi import APIRouter, Depends
from app.schemas.event_template import EventTemplate
from app.dependencies.event_template_db import FakeEventTemplateDatabase, get_event_template_db

router = APIRouter(
    prefix="/event-templates",
    tags=["Event Templates"]
)

@router.get("/", response_model=list[EventTemplate])
async def get_templates(db: FakeEventTemplateDatabase = Depends(get_event_template_db)):
    return db.list_templates()

@router.get("/{template_id}", response_model=EventTemplate)
async def get_template(template_id: int, db: FakeEventTemplateDatabase = Depends(get_event_template_db)):
    return db.get_template(template_id)

@router.post("/", response_model=EventTemplate, status_code=201)
async def create_template(template: EventTemplate, db: FakeEventTemplateDatabase = Depends(get_event_template_db)):
    return db.create_template(template)

@router.put("/{template_id}", response_model=EventTemplate)
async def update_template(template_id: int, updated: EventTemplate, db: FakeEventTemplateDatabase = Depends(get_event_template_db)):
    return db.update_template(template_id, updated)

@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: int, db: FakeEventTemplateDatabase = Depends(get_event_template_db)):
    db.delete_template(template_id)
    return
