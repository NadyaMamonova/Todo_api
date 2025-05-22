import subprocess
import time

import pytest
import psycopg2
import os
import logging

from fastapi import FastAPI

from app.database import init_db, connection_pool
from fastapi.testclient import TestClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def wait_for_postgres():
    """Ожидание доступности PostgreSQL"""
    for _ in range(30):
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="db"
            )
            conn.close()
            logger.info("✅ PostgreSQL is ready")
            return
        except psycopg2.OperationalError:
            time.sleep(1)
    pytest.fail("PostgreSQL not ready after 30 seconds")


@pytest.fixture(scope="session")
def test_db():
    test_db_name = os.getenv('TEST_DB_NAME', 'test_todo_db')

    # Удаление и создание БД
    subprocess.run(
        ["psql", "-U", "postgres", "-h", "db", "-c", f"DROP DATABASE IF EXISTS {test_db_name};"],
        env={"PGPASSWORD": "postgres"},
        check=False
    )
    subprocess.run(
        ["psql", "-U", "postgres", "-h", "db", "-c", f"CREATE DATABASE {test_db_name};"],
        env={"PGPASSWORD": "postgres"},
        check=True
    )

    # Применение миграций
    subprocess.run(
        ["psql", "-U", "postgres", "-d", test_db_name, "-h", "db", "-f", "/app/migrations/init.sql"],
        env={"PGPASSWORD": "postgres"},
        check=True
    )

    # Инициализация пула
    init_db(dbname=test_db_name)
    yield test_db_name

    # Закрытие пула
    if connection_pool and not connection_pool.closed:
        connection_pool.closeall()
        logger.info("Closed test database connections")


@pytest.fixture
def db_conn(test_db):
    """Фикстура для получения соединения с тестовой БД"""
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


@pytest.fixture
def client(test_db):
    from app.main import app
    test_app = FastAPI()
    test_app.include_router(app.router)
    test_app.dependency_overrides = app.dependency_overrides

    with TestClient(test_app) as client:
        yield client

@pytest.fixture
def sample_task_data():
    from datetime import date
    return {
        "title": "Test Task",
        "description": "Test Description",
        "deadline": date(2025, 12, 31),
        "status": "pending"
    }

@pytest.fixture(autouse=True)
def cleanup_pool():
    yield
    if connection_pool and not connection_pool.closed:
        connection_pool.closeall()
        logger.info("Test database pool closed after test")