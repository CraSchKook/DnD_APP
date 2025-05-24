from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class EventTemplate(Base):
    __tablename__ = "event_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    parameters = Column(JSON, nullable=True)  # произвольные данные шаблона
