import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    # Создаем временную тестовую БД
    conn = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        cur.execute("CREATE DATABASE test_todo_db")
    except psycopg2.Error:
        cur.execute("DROP DATABASE test_todo_db")
        cur.execute("CREATE DATABASE test_todo_db")

    yield
    cur.execute("DROP DATABASE test_todo_db")
    cur.close()
    conn.close()