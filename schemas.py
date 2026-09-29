from pydantic import BaseModel, Field, field_validator

ALLOWED_GOALS = {
    "General Fitness",
    "Flexibility",
    "Endurance",
    "Sports Fitness",
    "Strength"
}

ALLOWED_INTENSITIES = {
    "Light",
    "Moderate",
    "Active"
}


class UserInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=13, le=100)
    goal: str
    intensity: str

    @field_validator("name", "user_id")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, value):
        if value not in ALLOWED_GOALS:
            raise ValueError("Invalid fitness goal")
        return value

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):
        if value not in ALLOWED_INTENSITIES:
            raise ValueError("Invalid activity level")
        return value