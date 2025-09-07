-- Drop tables if they already exist (optional, for a clean seed)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS data_table;
DROP TABLE IF EXISTS users;

-- Create the "users" table for the /users endpoint
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into "users"
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

-- Create the "data_table" for the /data endpoint
CREATE TABLE data_table (
    id SERIAL PRIMARY KEY,
    data_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into "data_table"
INSERT INTO data_table (data_value) VALUES
    ('Sample Data 1'),
    ('Sample Data 2'),
    ('Sample Data 3');

-- Create the "orders" table for the /orders endpoint
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into "orders"
INSERT INTO orders (customer_id, total) VALUES
    (1, 100.50),
    (2, 200.00),
    (3, 150.75);
