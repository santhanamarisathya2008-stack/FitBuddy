from gemini_generator import generate_content


def update_workout_plan(old_plan, feedback, age):
    prompt = f"""
    Update this general 7-day movement plan.

    Age: {age}

    Original plan:
    {old_plan}

    User feedback:
    {feedback}

    Instructions:
    - Return a revised 7-day plan.
    - Use simple English.
    - Keep the plan age-appropriate.
    - Include rest and recovery.
    - Avoid calorie restriction, supplements,
      and medical treatment advice.
    - For users under 18, recommend adult or
      qualified coach supervision.
    - Never suggest exercising through pain,
      dizziness, or unusual breathlessness.
    """

    response = generate_content(prompt)

    if not response.text:
        raise RuntimeError("Gemini returned an empty updated plan")

    return response.text.strip()