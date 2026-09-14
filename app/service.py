from __future__ import annotations
import re, secrets
from collections import Counter
from dataclasses import dataclass

ALLOWED_CATEGORIES = {"service","staff","speed","cleanliness","price","other"}
PLANS = {
    "trial":{"locations":1,"monthly_feedback":50},
    "starter":{"locations":1,"monthly_feedback":500},
    "growth":{"locations":5,"monthly_feedback":5000},
}

@dataclass(frozen=True)
class FeedbackInput:
    rating:int
    category:str
    comment:str=""

def slugify(value):
    slug = re.sub(r"[^a-z0-9]+","-",value.lower()).strip("-")
    if not slug:
        raise ValueError("Business name must contain letters or numbers.")
    return slug

def create_business(conn,name,plan="trial"):
    name=name.strip()
    if len(name)<2:
        raise ValueError("Business name is too short.")
    if plan not in PLANS:
        raise ValueError("Unknown plan.")
    base=slugify(name); slug=base; i=2
    while conn.execute("SELECT 1 FROM businesses WHERE slug=?",(slug,)).fetchone():
        slug=f"{base}-{i}"; i+=1
    return conn.execute("INSERT INTO businesses(name,slug,plan) VALUES(?,?,?)",(name,slug,plan)).lastrowid

def create_location(conn,business_id,name):
    b=conn.execute("SELECT plan FROM businesses WHERE id=?",(business_id,)).fetchone()
    if not b:
        raise ValueError("Business not found.")
    count=conn.execute("SELECT COUNT(*) c FROM locations WHERE business_id=?",(business_id,)).fetchone()["c"]
    if count>=PLANS[b["plan"]]["locations"]:
        raise ValueError("Location limit reached for current plan.")
    name=name.strip()
    if not name:
        raise ValueError("Location name is required.")
    token=secrets.token_urlsafe(12)
    cur=conn.execute("INSERT INTO locations(business_id,name,token) VALUES(?,?,?)",(business_id,name,token))
    return cur.lastrowid,token

def add_feedback(conn,token,data):
    loc=conn.execute("SELECT l.id,b.plan FROM locations l JOIN businesses b ON b.id=l.business_id WHERE l.token=?",(token,)).fetchone()
    if not loc:
        raise ValueError("Feedback link not found.")
    if not 1<=data.rating<=5:
        raise ValueError("Rating must be between 1 and 5.")
    category=data.category.strip().lower()
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category.")
    comment=data.comment.strip()
    if len(comment)>1000:
        raise ValueError("Comment is too long.")
    used=conn.execute("SELECT COUNT(*) c FROM feedback WHERE location_id=?",(loc["id"],)).fetchone()["c"]
    if used>=PLANS[loc["plan"]]["monthly_feedback"]:
        raise ValueError("Feedback limit reached for current plan.")
    return conn.execute(
        "INSERT INTO feedback(location_id,rating,category,comment) VALUES(?,?,?,?)",
        (loc["id"],data.rating,category,comment)
    ).lastrowid

def dashboard(conn,business_id):
    business=conn.execute("SELECT id,name,slug,plan FROM businesses WHERE id=?",(business_id,)).fetchone()
    if not business:
        raise ValueError("Business not found.")
    rows=conn.execute("""
        SELECT f.rating,f.category,f.comment,f.created_at,l.name location_name
        FROM feedback f JOIN locations l ON l.id=f.location_id
        WHERE l.business_id=? ORDER BY f.id DESC
    """,(business_id,)).fetchall()
    total=len(rows)
    avg=round(sum(r["rating"] for r in rows)/total,2) if total else 0.0
    cats=Counter(r["category"] for r in rows)
    insights=["No feedback yet. Share the feedback link with customers."] if not total else [
        f"Most mentioned category: {cats.most_common(1)[0][0]} ({cats.most_common(1)[0][1]} responses)."
    ]
    low=sum(1 for r in rows if r["rating"]<=2)
    if low:
        insights.append(f"{low} low-rated response(s) need attention.")
    locs=conn.execute("SELECT id,name,token FROM locations WHERE business_id=?",(business_id,)).fetchall()
    return {
        "business":dict(business),
        "metrics":{"total_feedback":total,"average_rating":avg,"low_rating_count":low},
        "category_breakdown":dict(cats),
        "recent_feedback":[dict(r) for r in rows[:10]],
        "insights":insights,
        "locations":[dict(r) for r in locs],
        "plan_limits":PLANS[business["plan"]],
    }
