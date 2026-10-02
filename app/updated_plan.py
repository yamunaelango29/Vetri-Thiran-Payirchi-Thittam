from .config import get_settings
from .gemini_client import generate_text


def _demo_update(original_plan: str, feedback: str) -> str:
    return (
        original_plan
        + "\n\nUPDATED USING YOUR FEEDBACK\n"
        + f"Requested change: {feedback}\n"
        + "The demo version records the feedback and keeps the original plan available. "
          "In Gemini mode, the AI regenerates the complete 7-day plan using this feedback."
    )


def update_workout_plan(original_plan: str, feedback: str) -> tuple[str, str]:
    settings = get_settings()

    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_update(original_plan, feedback), "demo"

    prompt = f"""
You are updating a FitBuddy 7-day wellness workout plan.

Original plan:
{original_plan}

User feedback:
{feedback}

Create a complete revised Day 1 through Day 7 plan.
Requirements:
- Apply the feedback where it is reasonable.
- Preserve useful structure from the original plan.
- Include warm-up, main workout, rest/recovery and cooldown guidance.
- Keep exercise suggestions general and safe.
- Do not encourage exercising through pain or extreme weight-loss behavior.
- Do not provide medical diagnosis or treatment.
- Make the final response self-contained; do not say "same as above".
- Return readable plain text suitable for a <pre> block.
"""

    return generate_text(prompt, settings.gemini_pro_model), "gemini"
