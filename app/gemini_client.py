from functools import lru_cache

from .config import get_settings


@lru_cache
def get_gemini_client():
    settings = get_settings()
    if settings.demo_mode or not settings.gemini_api_key:
        return None

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        ) from exc

    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(prompt: str, model: str) -> str:
    client = get_gemini_client()
    if client is None:
        raise RuntimeError("Gemini client is unavailable because DEMO_MODE is enabled or GEMINI_API_KEY is missing.")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
