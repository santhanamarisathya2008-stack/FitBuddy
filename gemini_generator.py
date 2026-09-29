import time

from google import genai
from google.genai.errors import ClientError, ServerError
from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiUnavailableError(RuntimeError):
    pass


def get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key missing in .env")
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_content(prompt):
    for attempt in range(3):
        try:
            with get_client() as client:
                return client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
        except ClientError as error:
            if error.code == 429:
                raise GeminiUnavailableError(
                    "Gemini quota is temporarily exhausted."
                ) from error
            raise
        except ServerError as error:
            if error.code != 503:
                raise
            if attempt == 2:
                raise GeminiUnavailableError(
                    "Gemini is temporarily unavailable. Please try again shortly."
                ) from error
            time.sleep(2 ** attempt)


def fallback_workout(user):
    supervision = (
        "Because you are under 18, exercise with parent or qualified coach supervision.\n\n"
        if user.age < 18
        else ""
    )
    return f"""Gemini is temporarily unavailable. This is a general fallback plan, not an AI-personalized plan.
Goal: {user.goal}
Activity level: {user.intensity}

Before each session, warm up gently for 5 minutes. Cool down and stretch comfortably for 5 minutes afterward. Work at a pace where you can speak; rest as needed.

Day 1: Strength - 1 or 2 easy rounds of 8 chair squats, 8 wall push-ups, and 10 glute bridges.
Day 2: Walk at a comfortable pace for 15 to 25 minutes.
Day 3: Gentle mobility and stretching for 10 to 15 minutes.
Day 4: Rest, or take an easy 10-minute walk.
Day 5: Repeat Day 1, stopping each movement if it causes discomfort.
Day 6: Choose an enjoyable light activity for 15 to 25 minutes.
Day 7: Rest and recover.

{supervision}Stop if you feel pain, dizziness, or unusual breathlessness. This general plan is not medical advice."""


def generate_workout(user):
    prompt = f"""
    Create a general, safe 7-day fitness and movement plan.

    Name: {user.name}
    Age: {user.age}
    Goal: {user.goal}
    Activity level: {user.intensity}

    Requirements:
    - Provide a plan for all 7 days.
    - Include warm-up, activity, and cool-down.
    - Include suitable rest and recovery.
    - Use simple English.
    - Avoid calorie targets, restrictive diets,
      supplements, and medical treatment.
    - For users under 18, recommend parent or
      qualified coach supervision.
    - Advise stopping if pain, dizziness, or
      unusual breathlessness occurs.
    """

    try:
        response = generate_content(prompt)
    except GeminiUnavailableError:
        return fallback_workout(user)

    if not response.text:
        raise RuntimeError("Gemini returned an empty plan")

    return response.text.strip()


def generate_nutrition_tip(user):
    prompt = f"""
    Give one simple balanced nutrition and recovery tip
    for a person aged {user.age} with the goal {user.goal}.

    Avoid calorie targets, restrictive diets,
    supplements, and medical treatment advice.
    Use simple English.
    """

    try:
        response = generate_content(prompt)
    except GeminiUnavailableError:
        return "Eat balanced meals, drink water, and get enough rest."

    return (
        response.text.strip()
        if response.text
        else "Eat balanced meals, drink water, and get enough rest."
    )