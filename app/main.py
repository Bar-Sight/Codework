from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=[""],
    allow_headers=[""],
)

app = FastAPI(title="BarSight API")
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
@app.get("/metrics")
def metrics():
    # sample metrics for demo/pitch; replace with DB-driven values later
    return {
        "people_count": 12,
        "female_pct": 0.45,
        "male_pct": 0.55,
        "sales_last_hour": 24,
        "inventory_alerts": [{"product": "IPA", "on_hand": 2, "reorder_point": 5}]
    }
class Event(BaseModel):
    timestamp: Optional[datetime] = None
    camera_id: Optional[str] = None
    people_count: int
    female_pct: Optional[float] = None
@app.post("/events")
def post_event(e: Event):
    # echo for demo; later store to DB
    return {"received": True, "event": e.dict()}
class Sale(BaseModel):
    timestamp: Optional[datetime] = None
    product: str
    qty: int
    price: float
@app.post("/sales")
def post_sale(s: Sale):
    # echo for demo; later ingest into DB
    return {"received": True, "sale": s.dict()}
@app.get("/recommendations")
def recommendations():
    # demo recommendations
    return [
        {"type": "promotion", "message": "Consider Tue happy hour 6–8pm — expected +12% traffic"},
        {"type": "inventory", "message": "Reorder IPA — on hand 2 (reorder point 5)"}
    ]
