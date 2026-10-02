from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import (
    delete_user,
    get_all_users,
    get_db,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, FeedbackResponse, UserInput, WorkoutResponse
from .updated_plan import update_workout_plan

router = APIRouter()
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _render_error(request: Request, message: str, code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": message, "status_code": code},
        status_code=code,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": "FitBuddy – AI Fitness Plan Generator"},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_page(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except Exception as exc:
        return _render_error(request, f"Invalid input: {exc}", 422)

    try:
        user = save_user(
            db,
            data.username,
            data.user_id,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )
        workout_plan, workout_source = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )
        nutrition_tip, nutrition_source = generate_nutrition_tip_with_flash(data.goal)
        save_plan(db, user, workout_plan, nutrition_tip)
    except Exception as exc:
        return _render_error(request, f"AI generation failed: {exc}", 502)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": user.plan,
            "source": "gemini" if "gemini" in (workout_source, nutrition_source) else "demo",
            "updated": False,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_page(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except Exception as exc:
        return _render_error(request, f"Invalid feedback: {exc}", 422)

    user = get_user(db, data.user_id)
    original_plan = get_original_plan(db, data.user_id)

    if not user or not original_plan:
        return _render_error(request, "User or original plan not found.", 404)

    try:
        revised_plan, source = update_workout_plan(original_plan, data.feedback)
        nutrition_tip, nutrition_source = generate_nutrition_tip_with_flash(user.goal)
        update_plan(db, data.user_id, revised_plan, data.feedback, nutrition_tip)
        user = get_user(db, data.user_id)
    except Exception as exc:
        return _render_error(request, f"AI update failed: {exc}", 502)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": user.plan,
            "source": "gemini" if "gemini" in (source, nutrition_source) else "demo",
            "updated": True,
        },
    )


@router.get("/result/{user_id}", response_class=HTMLResponse)
def result_page(request: Request, user_id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user or not user.plan:
        return _render_error(request, "User or plan not found.", 404)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": user.plan, "source": "stored", "updated": bool(user.plan.updated_plan)},
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


@router.post("/admin/delete/{user_id}")
def delete_user_page(user_id: str, db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/api/generate-workout", response_model=WorkoutResponse)
def generate_workout_api(payload: UserInput, db: Session = Depends(get_db)):
    user = save_user(
        db,
        payload.username,
        payload.user_id,
        payload.age,
        payload.weight,
        payload.goal,
        payload.intensity,
    )

    try:
        workout_plan, workout_source = generate_workout_gemini(
            payload.username,
            payload.age,
            payload.weight,
            payload.goal,
            payload.intensity,
        )
        nutrition_tip, nutrition_source = generate_nutrition_tip_with_flash(payload.goal)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc

    save_plan(db, user, workout_plan, nutrition_tip)

    return WorkoutResponse(
        user_id=user.user_id,
        username=user.username,
        goal=user.goal,
        intensity=user.intensity,
        workout_plan=workout_plan,
        nutrition_tip=nutrition_tip,
        source="gemini" if "gemini" in (workout_source, nutrition_source) else "demo",
    )


@router.post("/api/submit-feedback", response_model=FeedbackResponse)
def submit_feedback_api(payload: FeedbackRequest, db: Session = Depends(get_db)):
    user = get_user(db, payload.user_id)
    original_plan = get_original_plan(db, payload.user_id)

    if not user or not original_plan:
        raise HTTPException(status_code=404, detail="User or original plan not found.")

    try:
        revised_plan, plan_source = update_workout_plan(original_plan, payload.feedback)
        nutrition_tip, nutrition_source = generate_nutrition_tip_with_flash(user.goal)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI update failed: {exc}") from exc

    update_plan(db, payload.user_id, revised_plan, payload.feedback, nutrition_tip)

    return FeedbackResponse(
        user_id=payload.user_id,
        updated_plan=revised_plan,
        nutrition_tip=nutrition_tip,
        source="gemini" if "gemini" in (plan_source, nutrition_source) else "demo",
    )


@router.get("/api/users")
def list_users_api(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": user.created_at.isoformat(),
            "has_updated_plan": bool(user.plan and user.plan.updated_plan),
        }
        for user in users
    ]
