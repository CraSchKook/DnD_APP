from pydantic import BaseModel
from typing import Dict

class Theme(BaseModel):
    id: int
    name: str
    colors: Dict[str, str]  # Пример: {"background": "#000000", "text": "#FFFFFF"}
    icons_path: str  # Пример: "/static/icons/dark_theme/"
    map_filters: Dict[str, str]  # Пример: {"fog": "enabled", "light": "dim"}
