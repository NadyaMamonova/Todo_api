from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime, timezone
from typing import Optional
from enum import Enum
from app.exceptions import InvalidDeadlineError


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "Buy groceries"}  # Заменено example на json_schema_extra
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        json_schema_extra={"example": "Milk, eggs, bread"}
    )
    deadline: Optional[date] = Field(
        None,
        json_schema_extra={"example": "2025-12-31"}  # Исправлен пример даты
    )
    status: TaskStatus = Field(default=TaskStatus.pending)

    @field_validator('deadline')
    def validate_deadline(cls, v: Optional[date]) -> Optional[date]:
        if v and v < datetime.now(timezone.utc).date():  # Исправлено на UTC дату
            raise InvalidDeadlineError()
        return v

    @field_validator('status')
    def validate_status(cls, v: TaskStatus) -> TaskStatus:
        if not isinstance(v, TaskStatus):
            raise ValueError(
                f"Invalid status. Must be one of: {list(TaskStatus.__members__.keys())}"
            )
        return v


class TaskCreate(TaskBase):
    """Модель для создания задачи"""
    pass


class TaskUpdate(BaseModel):
    """Модель для обновления задачи (частичное обновление)"""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        json_schema_extra={"example": "Updated title"}
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        json_schema_extra={"example": "Updated description"}
    )
    deadline: Optional[date] = Field(
        None,
        json_schema_extra={"example": "2025-12-31"}
    )
    status: Optional[TaskStatus] = None

    @field_validator('deadline')
    def validate_deadline(cls, v: Optional[date]) -> Optional[date]:
        if v and v < datetime.now(timezone.utc).date():  # Исправлено на UTC дату
            raise InvalidDeadlineError()
        return v


class TaskInDB(TaskBase):
    """Модель для работы с БД"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Алиас для обратной совместимости
Task = TaskInDB