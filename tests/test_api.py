import pytest
from datetime import date


def test_create_task(client):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "deadline": "2025-12-31",
        "status": "pending"
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"


def test_get_task(client):
    # Сначала создаем задачу
    create_response = client.post("/tasks/", json={
        "title": "Get Test Task",
        "description": "Test",
        "status": "pending"
    })
    task_id = create_response.json()["id"]

    # Теперь получаем ее
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test Task"


def test_get_tasks_with_filters(client):
    # Создаем несколько задач для фильтрации
    client.post("/tasks/", json={"title": "Task 1", "status": "pending"})
    client.post("/tasks/", json={"title": "Task 2", "status": "completed"})

    # Фильтр по статусу
    response = client.get("/tasks/?status=pending")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert all(task["status"] == "pending" for task in response.json())


def test_update_task(client):
    # Создаем задачу для обновления
    create_response = client.post("/tasks/", json={
        "title": "Original Task",
        "status": "pending"
    })
    task_id = create_response.json()["id"]

    # Обновляем задачу
    update_data = {
        "title": "Updated Task",
        "status": "completed"
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["status"] == "completed"


def test_delete_task(client):
    # Создаем задачу для удаления
    create_response = client.post("/tasks/", json={
        "title": "Task to Delete",
        "status": "pending"
    })
    task_id = create_response.json()["id"]

    # Удаляем задачу
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # Проверяем, что задача действительно удалена
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404