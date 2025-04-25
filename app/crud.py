from datetime import date
from typing import List, Optional
from .database import get_db
from .models import Task


def create_task(task: Task):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, description, created_at, deadline, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, title, description, created_at, deadline, status;
                """,
                (task.title, task.description, task.created_at, task.deadline, task.status)
            )
            result = cur.fetchone()
            conn.commit()
            return result


def get_task(task_id: int):
    """Получение одной задачи по ID"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            return cur.fetchone()


def get_tasks(
        status: Optional[str] = None,
        deadline: Optional[date] = None,
        title_search: Optional[str] = None
) -> List[dict]:
    """
    Получение списка задач с фильтрами:
    - по статусу
    - по сроку выполнения
    - по поиску в названии
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []

            if status:
                query += " AND status = %s"
                params.append(status)

            if deadline:
                query += " AND deadline = %s"
                params.append(deadline)

            if title_search:
                query += " AND title ILIKE %s"
                params.append(f"%{title_search}%")

            query += " ORDER BY created_at DESC"
            cur.execute(query, params)
            return cur.fetchall()


def update_task(task_id: int, task: Task):
    """Обновление задачи"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET title = %s,
                    description = %s,
                    deadline = %s,
                    status = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING *;
                """,
                (task.title, task.description, task.deadline, task.status, task_id)
            )
            result = cur.fetchone()
            conn.commit()
            return result


def delete_task(task_id: int):
    """Удаление задачи"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id;",
                (task_id,)
            )
            result = cur.fetchone()
            conn.commit()
            return result