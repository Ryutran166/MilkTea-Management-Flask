CREATE TABLE "branches" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "phone" varchar(20),
  "address" text,
  "status" boolean DEFAULT true,
  "created_at" timestamp
);

CREATE TABLE "users" (
  "id" serial PRIMARY KEY,
  "branch_id" int,
  "username" varchar(100) UNIQUE,
  "password" varchar(255),
  "full_name" varchar(100),
  "phone" varchar(20),
  "role" varchar(20),
  "status" boolean DEFAULT true,
  "created_at" timestamp
);

CREATE TABLE "employee_attendances" (
  "id" serial PRIMARY KEY,
  "user_id" int,
  "branch_id" int,
  "work_date" date,
  "check_in" timestamp,
  "check_out" timestamp,
  "total_hours" numeric(5,2) DEFAULT 0,
  "attendance_status" varchar(20) DEFAULT 'present',
  "note" text,
  "created_at" timestamp
);

CREATE TABLE "employee_salaries" (
  "id" serial PRIMARY KEY,
  "user_id" int,
  "month" int,
  "year" int,
  "base_salary" numeric(12,2),
  "bonus" numeric(12,2),
  "total_salary" numeric(12,2),
  "payment_status" varchar(20),
  "created_at" timestamp
);

CREATE TABLE "categories" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "description" text
);

CREATE TABLE "products" (
  "id" serial PRIMARY KEY,
  "category_id" int,
  "name" varchar(100),
  "description" text,
  "base_price" numeric(10,2),
  "image" varchar(255),
  "status" boolean DEFAULT true,
  "created_at" timestamp
);

CREATE TABLE "sizes" (
  "id" serial PRIMARY KEY,
  "name" varchar(10),
  "extra_price" numeric(10,2),
  "multiplier" numeric(10,2)
);

CREATE TABLE "product_sizes" (
  "id" serial PRIMARY KEY,
  "product_id" int,
  "size_id" int
);

CREATE TABLE "toppings" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "price" numeric(10,2),
  "status" boolean DEFAULT true
);

CREATE TABLE "orders" (
  "id" serial PRIMARY KEY,
  "branch_id" int,
  "user_id" int,
  "total_amount" numeric(12,2),
  "payment_method" varchar(50),
  "order_status" varchar(50),
  "created_at" timestamp
);

CREATE TABLE "order_items" (
  "id" serial PRIMARY KEY,
  "order_id" int,
  "product_id" int,
  "size_id" int,
  "quantity" int,
  "unit_price" numeric(10,2),
  "subtotal" numeric(12,2),
  "note" text
);

CREATE TABLE "order_item_toppings" (
  "id" serial PRIMARY KEY,
  "order_item_id" int,
  "topping_id" int
);

CREATE TABLE "inventories" (
  "id" serial PRIMARY KEY,
  "branch_id" int,
  "name" varchar(100),
  "quantity" numeric(12,2),
  "unit" varchar(20),
  "min_quantity" numeric(12,2),
  "updated_at" timestamp
);

CREATE TABLE "suppliers" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "phone" varchar(20),
  "address" text,
  "status" boolean DEFAULT true
);

CREATE TABLE "import_receipts" (
  "id" serial PRIMARY KEY,
  "branch_id" int,
  "supplier_id" int,
  "user_id" int,
  "total_amount" numeric(12,2),
  "note" text,
  "created_at" timestamp
);

CREATE TABLE "import_receipt_items" (
  "id" serial PRIMARY KEY,
  "receipt_id" int,
  "inventory_id" int,
  "quantity" numeric(12,2),
  "unit_price" numeric(10,2),
  "total_price" numeric(12,2)
);

CREATE TABLE "product_recipes" (
  "id" serial PRIMARY KEY,
  "product_id" int,
  "inventory_id" int,
  "quantity" numeric(12,2)
);

CREATE TABLE "inventory_transactions" (
  "id" serial PRIMARY KEY,
  "inventory_id" int,
  "transaction_type" varchar(50),
  "quantity" numeric(12,2),
  "reference_id" int,
  "note" text,
  "created_at" timestamp
);

CREATE TABLE "topping_recipes" (
  "id" serial PRIMARY KEY,
  "topping_id" int,
  "inventory_id" int,
  "quantity" numeric(12,2)
);


CREATE INDEX idx_orders_created_at
ON orders(created_at);

CREATE INDEX idx_orders_branch
ON orders(branch_id);

CREATE INDEX idx_order_items_order
ON order_items(order_id);

CREATE UNIQUE INDEX ON "employee_attendances" ("user_id", "work_date");

ALTER TABLE "users" ADD FOREIGN KEY ("branch_id") REFERENCES "branches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "employee_attendances" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "employee_salaries" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "products" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "product_sizes" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "product_sizes" ADD FOREIGN KEY ("size_id") REFERENCES "sizes" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("branch_id") REFERENCES "branches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("size_id") REFERENCES "sizes" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_item_toppings" ADD FOREIGN KEY ("order_item_id") REFERENCES "order_items" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_item_toppings" ADD FOREIGN KEY ("topping_id") REFERENCES "toppings" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "inventories" ADD FOREIGN KEY ("branch_id") REFERENCES "branches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "import_receipts" ADD FOREIGN KEY ("branch_id") REFERENCES "branches" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "import_receipts" ADD FOREIGN KEY ("supplier_id") REFERENCES "suppliers" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "import_receipts" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "import_receipt_items" ADD FOREIGN KEY ("receipt_id") REFERENCES "import_receipts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "import_receipt_items" ADD FOREIGN KEY ("inventory_id") REFERENCES "inventories" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "product_recipes" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "product_recipes" ADD FOREIGN KEY ("inventory_id") REFERENCES "inventories" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "topping_recipes" ADD FOREIGN KEY ("topping_id") REFERENCES "toppings" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "topping_recipes" ADD FOREIGN KEY ("inventory_id") REFERENCES "inventories" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "inventory_transactions" ADD FOREIGN KEY ("inventory_id") REFERENCES "inventories" ("id") DEFERRABLE INITIALLY IMMEDIATE;
