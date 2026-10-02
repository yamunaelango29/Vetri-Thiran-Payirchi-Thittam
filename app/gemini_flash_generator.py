from .config import get_settings
from .gemini_client import generate_text


def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Build meals around a variety of nutritious foods, stay hydrated, and keep activity consistent. Avoid extreme restriction.",
        "muscle gain": "Include a balanced meal with a protein source after training and give your body enough recovery time.",
        "general wellness": "Aim for balanced meals, regular hydration, sufficient sleep, and a mix of strength, mobility, and enjoyable activity.",
        "flexibility": "Include comfortable mobility work regularly, stay hydrated, and avoid forcing a stretch into pain.",
    }
    return tips[goal]


def generate_nutrition_tip_with_flash(goal: str) -> tuple[str, str]:
    settings = get_settings()

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_tip(goal), "demo"

    prompt = f"""
You are FitBuddy's nutrition and recovery tip assistant.

Fitness goal: {goal}

Give one concise, practical general-wellness nutrition or recovery tip.
Requirements:
- 3 to 5 sentences maximum.
- Focus on balanced nutrition, hydration, sleep, and recovery.
- Do not prescribe a diet or diagnose a health condition.
- Do not encourage restrictive eating, supplements, or unsafe weight-loss methods.
- Make it understandable to a beginner.
"""

    return generate_text(prompt, settings.gemini_flash_model), "gemini"
