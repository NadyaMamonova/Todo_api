from datetime import datetime, date
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as Connection
from app.models import TaskCreate, TaskUpdate, TaskInDB, TaskStatus
from app.exceptions import DatabaseError
from typing import Generator


def create_task(db: Connection, task: TaskCreate) -> TaskInDB:
    """Создание новой задачи в БД"""
    query = """
        INSERT INTO tasks (title, description, deadline, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, title, description, deadline, status, created_at, updated_at;
    """

    try:

        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                query,
                (
                    task.title,
                    task.description,
                    task.deadline,
                    task.status.value,
                    datetime.now()
                )
            )
            result = cur.fetchone()
            db.commit()
            return TaskInDB(**result)
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Database error: {e}")


def get_task(db: Connection, task_id: int) -> Optional[TaskInDB]:
    """Получение задачи по ID"""
    query = """
        SELECT id, title, description, deadline, status, created_at, updated_at
        FROM tasks
        WHERE id = %s;
    """

    try:

            with db.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (task_id,))
                result = cur.fetchone()
                return TaskInDB(**result) if result else None
    except Exception as e:
        raise DatabaseError(str(e))


def get_tasks(
    db: Connection,
    status: Optional[str] = None,
    deadline: Optional[date] = None,
    title_search: Optional[str] = None
) -> List[TaskInDB]:
    """Получение списка задач с фильтрацией"""
    base_query = """
        SELECT id, title, description, deadline, status, created_at, updated_at
        FROM tasks
        WHERE 1=1
    """
    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status)

    if deadline:
        conditions.append("deadline = %s")
        params.append(deadline)

    if title_search:
        conditions.append("title ILIKE %s")
        params.append(f"%{title_search}%")

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    base_query += " ORDER BY created_at DESC"

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(base_query, params)
            return [TaskInDB(**row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error while fetching tasks: {e}")


def update_task(db: Connection, task_id: int, task: TaskUpdate) -> Optional[TaskInDB]:
    """Обновление существующей задачи"""
    current_task = get_task(db, task_id)
    if not current_task:
        return None

    update_data = task.model_dump(exclude_unset=True)
    updated_task = current_task.model_copy(update=update_data)

    query = """
        UPDATE tasks
        SET title = %s,
            description = %s,
            deadline = %s,
            status = %s,
            updated_at = %s
        WHERE id = %s
        RETURNING id, title, description, deadline, status, created_at, updated_at;
    """

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                query,
                (
                    updated_task.title,
                    updated_task.description,
                    updated_task.deadline,
                    updated_task.status.value,
                    datetime.now(),
                    task_id
                )
            )
            result = cur.fetchone()
            db.commit()
            return TaskInDB(**result) if result else None
    except psycopg2.Error as e:
        db.rollback()
        raise DatabaseError(f"Database error while updating task: {e}")


def delete_task(db: Connection, task_id: int) -> bool:
    """Удаление задачи по ID"""
    query = "DELETE FROM tasks WHERE id = %s RETURNING id;"

    try:
        with db.cursor() as cur:
            cur.execute(query, (task_id,))
            deleted = cur.fetchone() is not None
            db.commit()
            return deleted
    except psycopg2.Error as e:
        db.rollback()
        raise DatabaseError(f"Database error while deleting task: {e}")