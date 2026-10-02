from .config import get_settings
from .gemini_client import generate_text


def _demo_plan(username: str, goal: str, intensity: str) -> str:
    level = {
        "low": "Beginner-friendly, gentle progression",
        "medium": "Moderate effort with controlled progression",
        "high": "Challenging but sustainable effort",
    }[intensity]

    focus = {
        "weight loss": "cardio, full-body movement and strength",
        "muscle gain": "strength-focused full-body training",
        "general wellness": "balanced strength, mobility and cardio",
        "flexibility": "mobility, stretching and light strength",
    }[goal]

    days = [
        ("Day 1", f"Full Body — {focus}"),
        ("Day 2", "Light Cardio + Mobility"),
        ("Day 3", "Upper Body + Core"),
        ("Day 4", "Rest / Gentle Mobility"),
        ("Day 5", "Lower Body + Core"),
        ("Day 6", "Cardio + Full Body Movement"),
        ("Day 7", "Recovery + Stretching"),
    ]

    lines = [
        f"FitBuddy Demo Plan for {username}",
        f"Goal: {goal.title()} | Intensity: {intensity.title()}",
        f"Approach: {level}",
        "",
        "General safety: use comfortable technique, rest when needed, and stop any movement that causes pain.",
    ]

    for day, focus_text in days:
        lines.extend([
            "",
            day,
            f"Focus: {focus_text}",
            "Warm-up: 5–10 minutes of easy movement and mobility.",
            "Main workout: 2–3 simple exercises appropriate to your experience, using controlled repetitions or short intervals.",
            "Rest: Take enough recovery between sets to maintain safe technique.",
            "Cooldown: 5 minutes of easy movement and comfortable stretching.",
        ])

    return "\n".join(lines)


def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> tuple[str, str]:
    settings = get_settings()

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_plan(username, goal, intensity), "demo"

    prompt = f"""
You are FitBuddy, a general wellness fitness-planning assistant.

Create a safe, practical 7-day fitness plan for:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

Requirements:
- Produce exactly Day 1 through Day 7.
- Include warm-up, main workout, rest/recovery, and cooldown guidance.
- For each workout day, include exercise names and simple sets/reps or duration.
- Include rest days or recovery where appropriate.
- Keep the plan suitable for a general wellness application and avoid extreme exercise.
- Do not prescribe medical treatment or diagnose conditions.
- Do not encourage starvation, dangerous weight-loss methods, or exercising through pain.
- Do not assume the user has gym equipment; provide simple alternatives where useful.
- Mention that users should adapt or stop an exercise if it causes pain and seek qualified professional advice for medical/injury concerns.
- Return readable plain text with headings. Do not use Markdown tables.

The result must be useful for a student project demo and easy to render inside a <pre> element.
"""

    return generate_text(prompt, settings.gemini_pro_model), "gemini"
