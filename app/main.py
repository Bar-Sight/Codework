from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlmodel import select, delete
import threading
from app.db import init_db, get_session
from app.models import Event as EventModel, Sale as SaleModel
app = FastAPI(title="BarSight API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=[""],
    allow_headers=[""],
)

init_db()
RETENTION_MINUTES = 60
_store_lock = threading.Lock()

class Event(BaseModel):
    timestamp: Optional[datetime] = None
    camera_id: Optional[str] = None
    people_count: int
    female_pct: Optional[float] = None
class Sale(BaseModel):
    timestamp: Optional[datetime] = None
    product: str
    qty: int
    price: float
def _now_utc() -> datetime:
    return datetime.utcnow()
def _query_windowed_data():
    cutoff = _now_utc() - timedelta(minutes=RETENTION_MINUTES)
    with get_session() as sess:
        events_cut = sess.exec(select(EventModel).where(EventModel.timestamp >= cutoff)).all()
        sales_cut = sess.exec(select(SaleModel).where(SaleModel.timestamp >= cutoff)).all()
    events_list = [
        {"timestamp": e.timestamp, "camera_id": e.camera_id, "people_count": e.people_count, "female_pct": e.female_pct}
        for e in events_cut
    ]
    sales_list = [
        {"timestamp": s.timestamp, "product": s.product, "qty": s.qty, "price": s.price}
        for s in sales_cut
    ]
    return events_list, sales_list
def _aggregate_metrics() -> Dict:
    events_cut, sales_cut = _query_windowed_data()
    sample_count = len(events_cut)
    total_people = sum(int(e.get("people_count", 0)) for e in events_cut) if sample_count else 0
    avg_people = total_people // sample_count if sample_count else 0

    weighted_female_sum = 0.0
    weighted_total = 0
    for e in events_cut:
        fp = e.get("female_pct")
        pc = int(e.get("people_count", 0))
        if fp is not None and pc > 0:
            weighted_female_sum += float(fp) * pc
            weighted_total += pc
    female_pct = round((weighted_female_sum / weighted_total), 2) if weighted_total else 0.0
    male_pct = round(1.0 - female_pct, 2) if weighted_total else 0.0

    sales_last_window = sum(int(s.get("qty", 0)) for s in sales_cut)
    revenue_last_window = round(sum(int(s.get("qty", 0)) * float(s.get("price", 0.0)) for s in sales_cut), 2)

    inventory_snapshot: Dict[str, int] = {}
    for s in sales_cut:
        prod = s.get("product", "unknown")
        inventory_snapshot[prod] = inventory_snapshot.get(prod, 0) + int(s.get("qty", 0))

    inventory_alerts = []
    for product, sold in inventory_snapshot.items():
        if sold >= 10:
            inventory_alerts.append({"product": product, "sold_in_window": sold, "note": "High demand — consider reorder"})

    return {
        "avg_people_observed": avg_people,
        "sample_count": sample_count,
        "female_pct": female_pct,
        "male_pct": male_pct,
        "sales_last_window": sales_last_window,
        "revenue_last_window": revenue_last_window,
        "inventory_snapshot": inventory_snapshot,
        "inventory_alerts": inventory_alerts,
        "retention_minutes": RETENTION_MINUTES,
        "last_updated": _now_utc().isoformat(),
    }  

@app.get("/health")
def health():
    return {"status": "ok", "time": _now_utc().isoformat()}
@app.get("/metrics")
def metrics():
    return _aggregate_metrics()
@app.post("/events")
def post_event(e: Event):
    e_dict = e.dict()
    ts = e_dict.get("timestamp") or _now_utc()
    ev = EventModel(
        timestamp=ts,
        camera_id=e_dict.get("camera_id"),
        people_count=int(e_dict.get("people_count", 0)),
        female_pct=float(e_dict.get("female_pct")) if e_dict.get("female_pct") is not None else None,
    )
    with get_session() as sess:
        sess.add(ev)
        sess.commit()
        sess.refresh(ev)
    return {"received": True, "event": {"id": ev.id, "people_count": ev.people_count, "female_pct": ev.female_pct}}

@app.post("/sales")
def post_sale(s: Sale):
    s_dict = s.dict()
    ts = s_dict.get("timestamp") or _now_utc()
    sale = SaleModel(
        timestamp=ts,
        product=s_dict.get("product"),
        qty=int(s_dict.get("qty", 0)),
        price=float(s_dict.get("price", 0.0)),
    )
    with get_session() as sess:
        sess.add(sale)
        sess.commit()
        sess.refresh(sale)
    return {"received": True, "sale": {"id": sale.id, "product": sale.product, "qty": sale.qty, "price": sale.price}}
@app.get("/recommendations")
def recommendations():
    m = _aggregate_metrics()
    recs = []
    if m["sample_count"] > 0 and m["avg_people_observed"] < 5:
        recs.append({"type": "promotion", "message": "Low traffic — consider midweek promotion (Tue/Thu)."})
    if m["sales_last_window"] > 20:
        recs.append({"type": "inventory", "message": "High recent sales — review stock on top-sellers."})
    recs.append({"type": "info", "message": f"Retention window: {m['retention_minutes']} minutes"})
    return recs
@app.post("/admin/clear")
def admin_clear():
    with get_session() as sess:
        sess.exec(delete(EventModel))
        sess.exec(delete(SaleModel))
        sess.commit()
    return {"cleared": True}