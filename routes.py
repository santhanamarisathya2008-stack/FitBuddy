from fastapi import (
    APIRouter, Request, Form, Depends, HTTPException
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets

from database import get_db, User
from schemas import UserInput, ALLOWED_GOALS, ALLOWED_INTENSITIES
from gemini_generator import (
    GeminiUnavailableError,
    generate_workout,
    generate_nutrition_tip
)
from updated_plan import update_workout_plan
from config import ADMIN_USERNAME, ADMIN_PASSWORD

router = APIRouter()
templates = Jinja2Templates(directory=".")
security = HTTPBasic()


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security)
):
    valid_user = secrets.compare_digest(
        credentials.username, ADMIN_USERNAME
    )
    valid_password = secrets.compare_digest(
        credentials.password, ADMIN_PASSWORD
    )

    if not (valid_user and valid_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin login",
            headers={"WWW-Authenticate": "Basic"}
        )

    return credentials.username


def home_page(request, error=None):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "goals": sorted(ALLOWED_GOALS),
            "intensities": sorted(ALLOWED_INTENSITIES),
            "error": error
        }
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return home_page(request)


@router.post("/generate-workout", response_class=HTMLResponse)
def create_workout(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = UserInput(
            name=name,
            user_id=user_id,
            age=age,
            goal=goal,
            intensity=intensity
        )

        workout = generate_workout(data)
        tip = generate_nutrition_tip(data)

        user = db.query(User).filter(
            User.user_id == data.user_id
        ).first()

        if user is None:
            user = User(
                name=data.name,
                user_id=data.user_id,
                age=data.age,
                goal=data.goal,
                intensity=data.intensity,
                workout_plan=workout,
                nutrition_tip=tip
            )
            db.add(user)
        else:
            user.name = data.name
            user.age = data.age
            user.goal = data.goal
            user.intensity = data.intensity
            user.workout_plan = workout
            user.nutrition_tip = tip
            user.feedback = ""
            user.updated_plan = ""

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": workout,
                "plan_title": "Your 7-Day Plan",
                "message": ""
            }
        )

    except Exception as error:
        db.rollback()
        return home_page(request, str(error))


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == user_id.strip()
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    feedback = feedback.strip()

    if not feedback or len(feedback) > 1000:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": user.workout_plan,
                "plan_title": "Your 7-Day Plan",
                "message": "Please enter feedback up to 1000 characters."
            }
        )

    try:
        updated = update_workout_plan(
            user.workout_plan,
            feedback,
            user.age
        )

        user.feedback = feedback
        user.updated_plan = updated

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": updated,
                "plan_title": "Updated 7-Day Plan",
                "message": "Your plan has been updated."
            }
        )

    except GeminiUnavailableError:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": user.workout_plan,
                "plan_title": "Your 7-Day Plan",
                "message": (
                    "Gemini is temporarily unavailable. Your plan was not changed; "
                    "please try your feedback again shortly."
                )
            }
        )

    except Exception:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": user.workout_plan,
                "plan_title": "Your 7-Day Plan",
                "message": "Could not update the plan. Check your API key."
            }
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
    admin: str = Depends(require_admin)
):
    users = db.query(User).order_by(User.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users}
    )