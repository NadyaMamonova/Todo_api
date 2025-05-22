import pytest
from datetime import date, timedelta
from app.crud import create_task, get_task, get_tasks, update_task, delete_task
from app.models import TaskCreate, TaskUpdate
from app.database import get_db_connection


@pytest.fixture
def sample_task_data():
    return {
        "title": "Test Task",
        "description": "Test Description",
        "deadline": date.today() + timedelta(days=1),  # Дата в будущем
        "status": "pending"
    }

@pytest.fixture
def db_connection():
    """Фикстура для получения соединения с БД"""
    with get_db_connection() as db:  # Используем новый контекстный менеджер
        yield db

def test_create_and_get_task(db_connection, sample_task_data):
    # Создаем задачу
    task_create = TaskCreate(**sample_task_data)
    created_task = create_task(db_connection, task_create)

    assert created_task is not None
    assert created_task.title == sample_task_data["title"]

    # Получаем задачу
    fetched_task = get_task(db_connection, created_task.id)
    assert fetched_task is not None
    assert fetched_task.id == created_task.id

def test_get_tasks_with_filters(db_connection, sample_task_data):
    # Создаем несколько задач
    task1 = create_task(db_connection, TaskCreate(**sample_task_data))
    task2 = create_task(db_connection, TaskCreate(
        title="Another Task",
        status="completed"
    ))

    # Фильтр по статусу
    pending_tasks = get_tasks(db_connection, status="pending")
    assert len(pending_tasks) >= 1
    assert all(task.status == "pending" for task in pending_tasks)

    # Фильтр по названию
    search_tasks = get_tasks(db_connection, title_search="Another")
    assert len(search_tasks) >= 1
    assert any("Another" in task.title for task in search_tasks)

def test_update_task(db_connection, sample_task_data):
    # Создаем задачу
    task_create = TaskCreate(**sample_task_data)
    created_task = create_task(db_connection, task_create)

    # Обновляем задачу
    update_data = TaskUpdate(
        title="Updated Task",
        status="completed"
    )
    updated_task = update_task(db_connection, created_task.id, update_data)

    assert updated_task is not None
    assert updated_task.title == "Updated Task"
    assert updated_task.status == "completed"

def test_delete_task(db_connection, sample_task_data):
    # Создаем задачу
    task_create = TaskCreate(**sample_task_data)
    created_task = create_task(db_connection, task_create)

    # Удаляем задачу
    delete_result = delete_task(db_connection, created_task.id)
    assert delete_result is True

    # Проверяем, что задача удалена
    deleted_task = get_task(db_connection, created_task.id)
    assert deleted_task is None
    assert deleted_task is None