from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .db import db_session, init_db
from .service import FeedbackInput, add_feedback, create_business, create_location, dashboard

app = FastAPI(title="ReviewPilot", version="0.1.0")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status":"ok","service":"reviewpilot"}

@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post("/demo/setup")
def demo_setup(business_name:str=Form(...), location_name:str=Form(...)):
    try:
        with db_session() as conn:
            bid=create_business(conn,business_name)
            create_location(conn,bid,location_name)
    except ValueError as exc:
        raise HTTPException(400,str(exc))
    return RedirectResponse(f"/dashboard/{bid}",status_code=303)

@app.get("/f/{token}", response_class=HTMLResponse)
def feedback_form(request:Request, token:str):
    with db_session() as conn:
        loc=conn.execute("""SELECT l.name location_name,b.name business_name
                            FROM locations l JOIN businesses b ON b.id=l.business_id
                            WHERE l.token=?""",(token,)).fetchone()
    if not loc:
        raise HTTPException(404,"Feedback link not found.")
    return templates.TemplateResponse("feedback.html",{"request":request,"token":token,"location":dict(loc)})

@app.post("/f/{token}", response_class=HTMLResponse)
def submit_feedback(request:Request, token:str, rating:int=Form(...), category:str=Form(...), comment:str=Form("")):
    try:
        with db_session() as conn:
            add_feedback(conn,token,FeedbackInput(rating,category,comment))
    except ValueError as exc:
        raise HTTPException(400,str(exc))
    return templates.TemplateResponse("thanks.html",{"request":request})

@app.get("/dashboard/{business_id}", response_class=HTMLResponse)
def business_dashboard(request:Request,business_id:int):
    try:
        with db_session() as conn:
            data=dashboard(conn,business_id)
    except ValueError as exc:
        raise HTTPException(404,str(exc))
    return templates.TemplateResponse("dashboard.html",{"request":request,**data})
