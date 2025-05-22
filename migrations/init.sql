CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);



--
---- Создаем функцию для автоматического обновления updated_at
--CREATE OR REPLACE FUNCTION update_modified_column()
--RETURNS TRIGGER AS $$
--BEGIN
--    NEW.updated_at = NOW();
--    RETURN NEW;
--END;
--$$ LANGUAGE plpgsql;
--
---- Создаем триггер для обновления updated_at при изменении записи
--CREATE TRIGGER update_tasks_modtime
--BEFORE UPDATE ON tasks
--FOR EACH ROW
--EXECUTE FUNCTION update_modified_column();