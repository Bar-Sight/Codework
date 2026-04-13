import time
import random
import requests
from datetime import datetime
API_BASE = "http://127.0.0.1:8000"
EVENT_INTERVAL = 5      # seconds between camera events
SALE_INTERVAL = 8       # seconds between sales events
products = [
    {"product": "IPA", "price": 6.0},
    {"product": "Lager", "price": 5.0},
    {"product": "Whiskey", "price": 8.0},
    {"product": "Cocktail", "price": 10.0},
]
def post_event():
    people = max(0, int(random.gauss(10, 6)))  # mean 10, sd 6
    female_pct = round(min(1.0, max(0.0, random.gauss(0.45, 0.12))), 2)
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "camera_id": "cam-1",
        "people_count": people,
        "female_pct": female_pct
    }
    try:
        r = requests.post(f"{API_BASE}/events", json=payload, timeout=2)
        print("event", payload, "->", r.status_code)
    except Exception as e:
        print("event error:", e)
def post_sale():
    p = random.choice(products)
    qty = random.choices([1,1,1,2], weights=[0.6,0.2,0.1,0.1])[0]
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "product": p["product"],
        "qty": qty,
        "price": p["price"]
    }
    try:
        r = requests.post(f"{API_BASE}/sales", json=payload, timeout=2)
        print("sale", payload, "->", r.status_code)
    except Exception as e:
        print("sale error:", e)
def main():
    next_event = time.time()
    next_sale = time.time()
    while True:
        now = time.time()
        if now >= next_event:
            post_event()
            next_event = now + EVENT_INTERVAL
        if now >= next_sale:
            post_sale()
            next_sale = now + SALE_INTERVAL
        time.sleep(0.5)
if __name__ == "__main__":
    main()
