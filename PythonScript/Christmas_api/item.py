from pydantic import BaseModel
from typing import Optional, Dict, List
class Item(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    toy: List[str]
