-- Create database if not exists
CREATE DATABASE IF NOT EXISTS text2sql_db;
USE text2sql_db;

-- Create feedback table for storing query feedback
CREATE TABLE IF NOT EXISTS query_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_id VARCHAR(255) UNIQUE NOT NULL,
    natural_language TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    feedback ENUM('thumbs_up', 'thumbs_down') NOT NULL,
    corrected_sql TEXT NULL,
    comments TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_feedback (feedback),
    INDEX idx_created_at (created_at)
);

-- Sample tables for demonstration
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    registration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) AS (quantity * unit_price) STORED,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    manager_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

-- Insert sample data
INSERT INTO customers (first_name, last_name, email, phone, city, state, country, registration_date) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', 'New York', 'NY', 'USA', '2023-01-15'),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', 'Los Angeles', 'CA', 'USA', '2023-02-20'),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', 'Chicago', 'IL', 'USA', '2023-03-10'),
('Alice', 'Williams', 'alice.williams@email.com', '555-0104', 'Houston', 'TX', 'USA', '2023-04-05'),
('Charlie', 'Brown', 'charlie.brown@email.com', '555-0105', 'Phoenix', 'AZ', 'USA', '2023-05-12');

INSERT INTO products (product_name, category, price, cost, stock_quantity, description) VALUES
('Laptop Pro', 'Electronics', 1299.99, 800.00, 50, 'High-performance laptop for professionals'),
('Wireless Mouse', 'Electronics', 29.99, 15.00, 200, 'Ergonomic wireless mouse'),
('Office Chair', 'Furniture', 199.99, 120.00, 30, 'Comfortable ergonomic office chair'),
('Desk Lamp', 'Furniture', 79.99, 45.00, 75, 'LED desk lamp with adjustable brightness'),
('Smartphone', 'Electronics', 699.99, 400.00, 100, 'Latest smartphone with advanced features'),
('Coffee Mug', 'Kitchen', 12.99, 5.00, 500, 'Ceramic coffee mug'),
('Notebook', 'Stationery', 8.99, 3.00, 1000, 'Spiral-bound notebook');

INSERT INTO employees (first_name, last_name, email, department, position, salary, hire_date) VALUES
('Michael', 'Scott', 'michael.scott@company.com', 'Sales', 'Regional Manager', 75000.00, '2020-01-15'),
('Jim', 'Halpert', 'jim.halpert@company.com', 'Sales', 'Sales Representative', 50000.00, '2020-03-01'),
('Pam', 'Beesly', 'pam.beesly@company.com', 'Administration', 'Receptionist', 35000.00, '2020-02-10'),
('Dwight', 'Schrute', 'dwight.schrute@company.com', 'Sales', 'Assistant Regional Manager', 55000.00, '2020-01-20'),
('Stanley', 'Hudson', 'stanley.hudson@company.com', 'Sales', 'Sales Representative', 48000.00, '2019-11-15'),
('Angela', 'Martin', 'angela.martin@company.com', 'Accounting', 'Senior Accountant', 52000.00, '2019-09-01'),
('Kevin', 'Malone', 'kevin.malone@company.com', 'Accounting', 'Accountant', 42000.00, '2020-05-12');

INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address) VALUES
(1, '2024-01-15', 1329.98, 'delivered', '123 Main St, New York, NY 10001'),
(2, '2024-01-20', 29.99, 'delivered', '456 Oak Ave, Los Angeles, CA 90210'),
(3, '2024-02-01', 199.99, 'shipped', '789 Pine St, Chicago, IL 60601'),
(1, '2024-02-10', 92.98, 'delivered', '123 Main St, New York, NY 10001'),
(4, '2024-02-15', 699.99, 'processing', '321 Elm St, Houston, TX 77001'),
(5, '2024-03-01', 12.99, 'delivered', '654 Maple Dr, Phoenix, AZ 85001'),
(2, '2024-03-05', 88.98, 'pending', '456 Oak Ave, Los Angeles, CA 90210');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(2, 2, 1, 29.99),
(3, 3, 1, 199.99),
(4, 4, 1, 79.99),
(4, 6, 1, 12.99),
(5, 5, 1, 699.99),
(6, 6, 1, 12.99),
(7, 4, 1, 79.99),
(7, 7, 1, 8.99);

-- Update manager relationships
UPDATE employees SET manager_id = 1 WHERE employee_id IN (2, 4, 5);
UPDATE employees SET manager_id = 6 WHERE employee_id = 7;