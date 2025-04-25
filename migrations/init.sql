CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATE DEFAULT CURRENT_DATE,
    deadline DATE,
    status VARCHAR(50) DEFAULT 'pending'
);