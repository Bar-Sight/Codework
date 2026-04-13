from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    camera_id: Optional[str] = None
    people_count: int = 0
    female_pct: Optional[float] = None
class Sale(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    product: str
    qty: int = 0
    price: float = 0.0