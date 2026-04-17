from pydantic import BaseModel, Field, field_validator
from typing import Optional


class DeckCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50, strip_whitespace=True)
    description: Optional[str] = Field(default=None, max_length=200)
    tags: Optional[str] = Field(default=None, max_length=100)


class CardImport(BaseModel):
    front: str = Field(min_length=3, max_length=50, strip_whitespace=True)
    back: str = Field(min_length=3, max_length=50, strip_whitespace=True)
    difficulty_hint: Optional[str] = Field(default=None, max_length=50)

    @field_validator("front", "back", mode="after")
    @classmethod
    def validate_not_empty(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name}  не может быть пустым")
        return v


class ProgressUpdate(BaseModel):
    card_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    is_correct: bool
    user_input: Optional[str] = Field(
        default=None, max_length=100, strip_whitespace=True
    )
