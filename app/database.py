import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from psycopg2.extensions import connection as Connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация пула соединений
connection_pool: Optional[ThreadedConnectionPool] = None

def init_db(dbname: str = "todo_db"):
    global connection_pool
    if connection_pool and not connection_pool.closed:
        logger.info(f"Closing existing pool for {dbname}")
        connection_pool.closeall()

    try:
        logger.info(f"Initializing new connection pool for {dbname}")
        connection_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=dbname,
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            cursor_factory=RealDictCursor
        )
        logger.info(f"Successfully initialized connection pool for {dbname}")
    except Exception as e:
        logger.error(f"Failed to initialize connection pool for {dbname}", exc_info=True)
        raise

def close_db():
    """Закрытие всех соединений в пуле"""
    if connection_pool and not connection_pool.closed:
        connection_pool.closeall()
        logger.info("Closed all database connections")


@contextmanager
def get_db_connection() -> Generator[Connection, None, None]:
    if connection_pool is None or connection_pool.closed:
        init_db()

    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except psycopg2.Error as e:
        logger.error("Database error", exc_info=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

