from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


def generate_quick_tip(goal):
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key missing in .env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
    Give one short, safe recovery tip for {goal}.
    Use simple English.
    Do not provide medical advice or supplements.
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return (
        response.text.strip()
        if response.text
        else "Take suitable rest breaks and stay hydrated."
    )