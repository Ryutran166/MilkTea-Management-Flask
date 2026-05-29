-- =========================================
-- DATABASE: MILK TEA MANAGEMENT SYSTEM
-- PostgreSQL
-- =========================================

-- =========================================
-- BRANCHES
-- =========================================

CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================================
-- USERS
-- =========================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,

    branch_id INT,

    username VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    full_name VARCHAR(100) NOT NULL,

    phone VARCHAR(20),

    role VARCHAR(20) NOT NULL
    CHECK(role IN ('admin', 'manager', 'staff')),

    status BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_users_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(id)
    ON DELETE SET NULL
);

-- =========================================
-- EMPLOYEE ATTENDANCES
-- =========================================

CREATE TABLE employee_attendances (
    id SERIAL PRIMARY KEY,

    user_id INT NOT NULL,

    branch_id INT,

    work_date DATE NOT NULL,

    check_in TIMESTAMP,

    check_out TIMESTAMP,

    total_hours NUMERIC(5,2) DEFAULT 0
    CHECK(total_hours >= 0),

    attendance_status VARCHAR(20)
    DEFAULT 'present'
    CHECK(attendance_status IN ('present', 'late', 'absent')),

    note TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_user_workdate
    UNIQUE(user_id, work_date),

    CONSTRAINT fk_attendance_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_attendance_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(id)
    ON DELETE SET NULL
);

-- =========================================
-- EMPLOYEE SALARIES
-- =========================================

CREATE TABLE employee_salaries (
    id SERIAL PRIMARY KEY,

    user_id INT NOT NULL,

    month INT NOT NULL
    CHECK(month BETWEEN 1 AND 12),

    year INT NOT NULL
    CHECK(year >= 2020),

    base_salary NUMERIC(12,2) NOT NULL
    CHECK(base_salary >= 0),

    bonus NUMERIC(12,2) DEFAULT 0
    CHECK(bonus >= 0),

    total_salary NUMERIC(12,2) NOT NULL
    CHECK(total_salary >= 0),

    payment_status VARCHAR(20)
    CHECK(payment_status IN ('pending', 'paid')),

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_salary_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- =========================================
-- CATEGORIES
-- =========================================

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT
);

-- =========================================
-- PRODUCTS
-- =========================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,

    category_id INT,

    name VARCHAR(100) NOT NULL,

    description TEXT,

    base_price NUMERIC(10,2) NOT NULL
    CHECK(base_price >= 0),

    image VARCHAR(255),

    status BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_product_category
    FOREIGN KEY (category_id)
    REFERENCES categories(id)
    ON DELETE SET NULL
);

-- =========================================
-- SIZES
-- =========================================

CREATE TABLE sizes (
    id SERIAL PRIMARY KEY,

    name VARCHAR(10) NOT NULL UNIQUE,

    extra_price NUMERIC(10,2) DEFAULT 0
    CHECK(extra_price >= 0),

  
);

-- =========================================
-- PRODUCT SIZES
-- =========================================

CREATE TABLE product_sizes (
    id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,

    size_id INT NOT NULL,

    CONSTRAINT unique_product_size
    UNIQUE(product_id, size_id),

    CONSTRAINT fk_product_size_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_product_size_size
    FOREIGN KEY (size_id)
    REFERENCES sizes(id)
    ON DELETE CASCADE
);

-- =========================================
-- TOPPINGS
-- =========================================

CREATE TABLE toppings (
    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,

    price NUMERIC(10,2) NOT NULL
    CHECK(price >= 0),

    status BOOLEAN DEFAULT TRUE
);

-- =========================================
-- ORDERS
-- =========================================

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,

    branch_id INT,

    user_id INT,

    total_amount NUMERIC(12,2) NOT NULL
    CHECK(total_amount >= 0),

    payment_method VARCHAR(50)
    CHECK(payment_method IN ('cash', 'momo', 'banking', 'vnpay')),

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_order_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(id)
    ON DELETE SET NULL,

    CONSTRAINT fk_order_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE SET NULL
);

-- =========================================
-- ORDER ITEMS
-- =========================================

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,

    order_id INT NOT NULL,

    product_id INT,

    size_id INT,

    quantity INT NOT NULL
    CHECK(quantity > 0),

    unit_price NUMERIC(10,2) NOT NULL
    CHECK(unit_price >= 0),

    subtotal NUMERIC(12,2) NOT NULL
    CHECK(subtotal >= 0),

    note TEXT,

    CONSTRAINT fk_order_item_order
    FOREIGN KEY (order_id)
    REFERENCES orders(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_order_item_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE SET NULL,

    CONSTRAINT fk_order_item_size
    FOREIGN KEY (size_id)
    REFERENCES sizes(id)
    ON DELETE SET NULL
);

-- =========================================
-- ORDER ITEM TOPPINGS
-- =========================================

CREATE TABLE order_item_toppings (
    id SERIAL PRIMARY KEY,

    order_item_id INT NOT NULL,

    topping_id INT NOT NULL,

    CONSTRAINT unique_orderitem_topping
    UNIQUE(order_item_id, topping_id),

    CONSTRAINT fk_orderitem_topping_item
    FOREIGN KEY (order_item_id)
    REFERENCES order_items(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_orderitem_topping_topping
    FOREIGN KEY (topping_id)
    REFERENCES toppings(id)
    ON DELETE CASCADE
);

-- =========================================
-- INVENTORIES
-- =========================================

CREATE TABLE inventories (
    id SERIAL PRIMARY KEY,

    branch_id INT,

    name VARCHAR(100) NOT NULL,

    quantity NUMERIC(12,2) DEFAULT 0
    CHECK(quantity >= 0),

    unit VARCHAR(20),

    min_quantity NUMERIC(12,2) DEFAULT 0
    CHECK(min_quantity >= 0),

    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_inventory_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(id)
    ON DELETE SET NULL
);

-- =========================================
-- SUPPLIERS
-- =========================================

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    phone VARCHAR(20),

    address TEXT,

    status BOOLEAN DEFAULT TRUE
);

-- =========================================
-- IMPORT RECEIPTS
-- =========================================

CREATE TABLE import_receipts (
    id SERIAL PRIMARY KEY,

    branch_id INT,

    supplier_id INT,

    user_id INT,

    total_amount NUMERIC(12,2)
    CHECK(total_amount >= 0),

    note TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_import_branch
    FOREIGN KEY (branch_id)
    REFERENCES branches(id)
    ON DELETE SET NULL,

    CONSTRAINT fk_import_supplier
    FOREIGN KEY (supplier_id)
    REFERENCES suppliers(id)
    ON DELETE SET NULL,

    CONSTRAINT fk_import_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE SET NULL
);

-- =========================================
-- IMPORT RECEIPT ITEMS
-- =========================================

CREATE TABLE import_receipt_items (
    id SERIAL PRIMARY KEY,

    receipt_id INT NOT NULL,

    inventory_id INT,

    quantity NUMERIC(12,2) NOT NULL
    CHECK(quantity > 0),

    unit_price NUMERIC(10,2) NOT NULL
    CHECK(unit_price >= 0),

    total_price NUMERIC(12,2) NOT NULL
    CHECK(total_price >= 0),

    CONSTRAINT fk_receipt_item_receipt
    FOREIGN KEY (receipt_id)
    REFERENCES import_receipts(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_receipt_item_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventories(id)
    ON DELETE SET NULL
);

-- =========================================
-- PRODUCT RECIPES
-- =========================================

CREATE TABLE product_recipes (
    id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,

    inventory_id INT NOT NULL,

    quantity NUMERIC(12,2) NOT NULL
    CHECK(quantity > 0),

    CONSTRAINT unique_product_recipe
    UNIQUE(product_id, inventory_id),

    CONSTRAINT fk_recipe_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_recipe_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventories(id)
    ON DELETE CASCADE
);

-- =========================================
-- TOPPING RECIPES
-- =========================================

CREATE TABLE topping_recipes (
    id SERIAL PRIMARY KEY,

    topping_id INT NOT NULL,

    inventory_id INT NOT NULL,

    quantity NUMERIC(12,2) NOT NULL
    CHECK(quantity > 0),

    CONSTRAINT unique_topping_recipe
    UNIQUE(topping_id, inventory_id),

    CONSTRAINT fk_topping_recipe_topping
    FOREIGN KEY (topping_id)
    REFERENCES toppings(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_topping_recipe_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventories(id)
    ON DELETE CASCADE
);

-- =========================================
-- INVENTORY TRANSACTIONS
-- =========================================

CREATE TABLE inventory_transactions (
    id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    transaction_type VARCHAR(50)
    CHECK(transaction_type IN (
        'import',
        'export',
        'adjustment',
        'sale'
    )),

    quantity NUMERIC(12,2) NOT NULL
    CHECK(quantity > 0),

    reference_id INT,

    note TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_inventory_transaction_inventory
    FOREIGN KEY (inventory_id)
    REFERENCES inventories(id)
    ON DELETE CASCADE
);

-- =========================================
-- PAYMENTS
-- =========================================

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,

    order_id INT NOT NULL,

    amount NUMERIC(12,2) NOT NULL
    CHECK(amount >= 0),

    payment_method VARCHAR(50)
    CHECK(payment_method IN (
        'cash',
        'momo',
        'banking',
        'vnpay'
    )),

    payment_status VARCHAR(20)
    CHECK(payment_status IN (
        'pending',
        'paid',
        'failed'
    )),

    paid_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_payment_order
    FOREIGN KEY (order_id)
    REFERENCES orders(id)
    ON DELETE CASCADE
);


CREATE TABLE product_toppings (
    id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,
    topping_id INT NOT NULL,

    CONSTRAINT fk_product_toppings_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_product_toppings_topping
        FOREIGN KEY (topping_id)
        REFERENCES toppings(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_product_topping
        UNIQUE (product_id, topping_id)
);
-- =========================================
-- INDEXES
-- =========================================

CREATE INDEX idx_orders_created_at
ON orders(created_at);

CREATE INDEX idx_orders_branch
ON orders(branch_id);

CREATE INDEX idx_orders_user
ON orders(user_id);

CREATE INDEX idx_order_items_order
ON order_items(order_id);

CREATE INDEX idx_inventory_branch
ON inventories(branch_id);

CREATE INDEX idx_attendance_user
ON employee_attendances(user_id);

CREATE INDEX idx_attendance_workdate
ON employee_attendances(work_date);

CREATE INDEX idx_product_category
ON products(category_id);