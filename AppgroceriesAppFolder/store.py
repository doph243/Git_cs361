"""Data layer: users, shopping list, pantry — persisted to data.json."""
import json, os, hashlib
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# Simulated product barcode database (IH#3: ISBN search as an info-gathering tool)
PRODUCT_DB = {
    "111": {"name": "Apples",          "category": "Produce"},
    "222": {"name": "Olive Oil",       "category": "Oil"},
    "333": {"name": "Pasta",           "category": "Dry Goods"},
    "444": {"name": "Milk",            "category": "Dairy"},
    "555": {"name": "Chicken Breast",  "category": "Meat"},
    "666": {"name": "Bread",           "category": "Bakery"},
    "777": {"name": "Orange Juice",    "category": "Beverages"},
}

# ---------- internal helpers ----------

def _load():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "lists": {}, "pantries": {}}
    with open(DATA_FILE) as f:
        return json.load(f)

def _save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ---------- auth ----------

def register(username, password):
    """Return (True, msg) on success, (False, msg) on failure."""
    d = _load()
    if username in d["users"]:
        return False, "Username already taken."
    d["users"][username] = _hash(password)
    d["lists"][username]    = []
    d["pantries"][username] = []
    _save(d)
    return True, "Account created! Please log in."

def authenticate(username, password):
    """Return True if credentials match."""
    d = _load()
    return username in d["users"] and d["users"][username] == _hash(password)

# ---------- shopping list ----------

def get_list(username):
    return _load()["lists"].get(username, [])

def add_item(username, name, category="", quantity=1, notes=""):
    d = _load()
    d["lists"][username].append({
        "name": name, "category": category,
        "quantity": quantity, "notes": notes,
        "checked": False,
        "date_added": datetime.now().isoformat(),
    })
    _save(d)

def remove_item(username, idx):
    d = _load()
    d["lists"][username].pop(idx)
    _save(d)

def toggle_item(username, idx):
    d = _load()
    item = d["lists"][username][idx]
    item["checked"] = not item["checked"]
    _save(d)

# ---------- pantry ----------

def get_pantry(username):
    return _load()["pantries"].get(username, [])

def add_pantry_item(username, name, category="", quantity=1):
    d = _load()
    d["pantries"][username].append({"name": name, "category": category, "quantity": quantity})
    _save(d)

def remove_pantry_item(username, idx):
    d = _load()
    d["pantries"][username].pop(idx)
    _save(d)

def update_pantry_item(username, idx, name, category, quantity):
    d = _load()
    d["pantries"][username][idx] = {"name": name, "category": category, "quantity": quantity}
    _save(d)

# ---------- ISBN / barcode lookup ----------

def isbn_lookup(code):
    """Return product dict or None if not found."""
    return PRODUCT_DB.get(code.strip())
