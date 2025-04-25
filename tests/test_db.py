import pytest
from app.crud import create_task, get_task, get_tasks, update_task, delete_task
from app.models import Task
from datetime import date


@pytest.fixture
def sample_task():
    return Task(
        title="Test Task",
        description="Test Description",
        deadline=date(2025, 12, 31),
        status="pending"
    )


def test_create_and_get_task(test_db, sample_task):
    # Тест создания и получения задачи
    created_task = create_task(sample_task)
    assert created_task is not None

    task_id = created_task["id"]
    retrieved_task = get_task(task_id)
    assert retrieved_task["title"] == "Test Task"


def test_get_tasks_with_filters(test_db, sample_task):
    # Тест фильтрации задач
    create_task(sample_task)
    create_task(Task(title="Another Task", status="completed"))

    pending_tasks = get_tasks(status="pending")
    assert len(pending_tasks) >= 1
    assert all(task["status"] == "pending" for task in pending_tasks)


def test_update_task(test_db, sample_task):
    # Тест обновления задачи
    created_task = create_task(sample_task)
    task_id = created_task["id"]

    updated_data = Task(
        title="Updated Task",
        description="New Description",
        status="completed"
    )
    updated_task = update_task(task_id, updated_data)
    assert updated_task["title"] == "Updated Task"
    assert updated_task["status"] == "completed"


def test_delete_task(test_db, sample_task):
    # Тест удаления задачи
    created_task = create_task(sample_task)
    task_id = created_task["id"]

    delete_result = delete_task(task_id)
    assert delete_result["id"] == task_id

    assert get_task(task_id) is None