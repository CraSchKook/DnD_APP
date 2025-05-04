from pydantic import BaseModel
from typing import Dict

class Theme(BaseModel):
    id: int
    name: str
    colors: Dict[str, str]
    icons_path: str
    map_filters: Dict[str, str]
