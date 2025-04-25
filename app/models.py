from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class Task(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    created_at: date = Field(default_factory=date.today)
    deadline: Optional[date] = None
    status: TaskStatus = Field(default=TaskStatus.pending)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Купить продукты",
                "description": "Молоко, хлеб, яйца",
                "deadline": "2025-04-20",
                "status": "pending"
            }
        }


