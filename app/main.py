from fastapi import FastAPI, HTTPException, Query, Depends
from datetime import date
from typing import Optional, List
from .database import get_db
from .models import Task
from .crud import (
    create_task as crud_create_task,
    get_task as crud_get_task,
    get_tasks as crud_get_tasks,
    update_task as crud_update_task,
    delete_task as crud_delete_task
)
import psycopg2

app = FastAPI(
    title="ToDo API",
    description="API для управления списком задач",
    version="1.0.0"
)


@app.post("/tasks/", response_model=Task, status_code=201)
def create_task(task: Task):
    try:
        created_task = crud_create_task(task)
        if not created_task:
            raise HTTPException(status_code=400, detail="Failed to create task")
        return created_task
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    try:
        task = crud_get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/tasks/", response_model=List[Task])
def read_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    deadline: Optional[date] = Query(None, description="Filter by deadline"),
    title_search: Optional[str] = Query(None, description="Search in title")
):
    try:
        tasks = crud_get_tasks(status=status, deadline=deadline, title_search=title_search)
        return tasks
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    try:
        updated_task = crud_update_task(task_id, task)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        deleted_task = crud_delete_task(task_id)
        if not deleted_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.on_event("startup")
async def startup():
    # Проверка подключения к БД при старте
    try:
        conn = get_db()
        conn.close()
    except Exception as e:
        raise Exception(f"Failed to connect to database: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)