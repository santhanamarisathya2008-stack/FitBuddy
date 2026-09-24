from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
def generate_plan(request: Request,
                  name: str = Form(...),
                  age: int = Form(...),
                  weight: float = Form(...),
                  goal: str = Form(...),
                  intensity: str = Form(...)):
    plan = f"Hello {name}, age {age}, weight {weight}kg. Your goal is {goal}. Here is a {intensity} workout plan!"
    return templates.TemplateResponse("result.html", {
        "request": request,
        "name": name,
        "age": age,
        "weight": weight,
        "goal": goal,
        "intensity": intensity,
        "plan": plan
    })
