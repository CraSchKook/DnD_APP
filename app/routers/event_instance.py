from fastapi import APIRouter, Depends
from typing import List
from app.schemas.event_instance import EventInstance, EventInstanceCreate
from app.dependencies.db import FakeDatabase, get_db

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.get("/", response_model=List[EventInstance])
def list_event_instances(db: FakeDatabase = Depends(get_db)):
    return db.list_event_instances()

@router.post("/", response_model=EventInstance)
def create_event_instance(event_instance: EventInstanceCreate, db: FakeDatabase = Depends(get_db)):
    new_event_instance = EventInstance(id=len(db.event_instances) + 1, **event_instance.dict())
    return db.create_event_instance(new_event_instance)
