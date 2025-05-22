from fastapi import HTTPException, status
from typing import Optional

class TaskNotFound(HTTPException):
    def __init__(self, task_id: Optional[int] = None):
        detail = "Task not found"
        if task_id:
            detail = f"Task with ID {task_id} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class InvalidDeadlineError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Deadline must be in the future"
        )

class InvalidTaskStatusError(HTTPException):
    def __init__(self, status: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid task status: {status}"
        )