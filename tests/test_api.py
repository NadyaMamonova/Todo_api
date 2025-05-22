import pytest
from app.models import TaskCreate, TaskStatus
from datetime import date
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    # Создаем тестового клиента для каждого теста
    with TestClient(app) as client:
        yield client


def test_create_task(client):
    """Тест создания задачи"""
    task_data = {
        "title": "Test Task",
        "description": "Test description",
        "deadline": str(date.today()),
        "status": "pending"
    }

    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == TaskStatus.pending.value  # Используем .value для enum

    assert "id" in data


def test_get_task(client):
    """Тест получения задачи по ID"""
    # Создаем задачу
    task_data = {
        "title": "Task to Get",
        "description": "Test description for get",
        "status": "pending"
    }

    create_response = client.post("/tasks/", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()

    # Получаем созданную задачу
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["id"] == task_id


def test_task_not_found(client):
    """Тест на получение несуществующей задачи"""
    response = client.get("/tasks/9999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def test_update_task(client):
    """Тест обновления задачи"""
    # Создаем задачу
    task_data = {
        "title": "Task to Update",
        "description": "Original description",
        "status": "pending"
    }

    create_response = client.post("/tasks/", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    # Обновляем задачу
    update_data = {
        "title": "Updated Task",
        "status": "in_progress"
    }

    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()

    assert updated_task["title"] == update_data["title"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["description"] == task_data["description"]


def test_delete_task(client):
    """Тест удаления задачи"""
    # Создаем задачу
    task_data = {
        "title": "Task to Delete",
        "status": "pending"
    }

    create_response = client.post("/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Удаляем задачу
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200

    # Проверяем удаление
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_filter_tasks(client):
    """Тест фильтрации задач"""
    # Создаем тестовые данные
    test_tasks = [
        {"title": "Task 1", "status": "pending"},
        {"title": "Task 2", "status": "in_progress"},
        {"title": "Task 3", "status": "completed"}
    ]

    for task in test_tasks:
        client.post("/tasks/", json=task)

    # Тестируем фильтры
    response = client.get("/tasks/?status=pending")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1
    assert all(task["status"] == "pending" for task in tasks)

    response = client.get("/tasks/?title_search=Task")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 3
    assert all("Task" in task["title"] for task in tasks)