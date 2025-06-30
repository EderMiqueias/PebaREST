from typing import Optional
from pebarest import BaseModel


class Item(BaseModel):
    name: str
    quantity: int
    description: Optional[str] = None



