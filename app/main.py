import os
from fastapi import FastAPI, Query, Depends
from datetime import date
from typing import List, Optional, Generator
import psycopg2
from psycopg2.extensions import connection as Connection
from contextlib import asynccontextmanager
import logging
from .database import get_db_connection, init_db, close_db
from .models import Task, TaskCreate, TaskUpdate
from .crud import (
    create_task as crud_create_task,
    get_task as crud_get_task,
    get_tasks as crud_get_tasks,
    update_task as crud_update_task,
    delete_task as crud_delete_task
)
from .exceptions import (
    TaskNotFound,
    DatabaseError,
    InvalidDeadlineError,
    InvalidTaskStatusError
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_name = "test_todo_db" if os.getenv("TESTING") else "todo_db"
    init_db(db_name)
    try:
        with get_db_connection() as db:
            with db.cursor() as cur:
                cur.execute("SELECT 1")
        logger.info(f"✅ Database connection to {db_name} successful")
    except Exception as e:
        logger.error(f"❌ Database connection to {db_name} failed: {e}")
        raise
    yield
    close_db()
    logger.info("Database connections closed")

app = FastAPI(
    title="ToDo API",
    description="API для управления списком задач",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработчики ошибок
@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": exc.detail},
    )

@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc):
    logger.error(f"Database error: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

@app.exception_handler(InvalidDeadlineError)
async def invalid_deadline_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": exc.detail},
    )

# Роуты
@app.post("/tasks/", response_model=Task, status_code=201)
def create_task(
    task: TaskCreate,
    db: Connection = Depends(get_db_connection)
):
    created_task = crud_create_task(db, task)
    db.commit()  # Явное подтверждение изменений
    return created_task

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    db: Connection = Depends(get_db_connection)
):
    task = crud_get_task(db, task_id)
    if not task:
        raise TaskNotFound(task_id)
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks(
    status: Optional[str] = Query(None),
    deadline: Optional[date] = Query(None),
    title_search: Optional[str] = Query(None),
    db: Connection = Depends(get_db_connection)
):
    return crud_get_tasks(db, status=status, deadline=deadline, title_search=title_search)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Connection = Depends(get_db_connection)
):
    updated_task = crud_update_task(db, task_id, task)
    db.commit()
    if not updated_task:
        raise TaskNotFound(task_id)
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Connection = Depends(get_db_connection)
):
    if not crud_delete_task(db, task_id):
        raise TaskNotFound(task_id)
    db.commit()
    return {"message": "Task deleted successfully"}