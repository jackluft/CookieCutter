from pydantic import BaseModel
class Item(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    toy: List[str]
