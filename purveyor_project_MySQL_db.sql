-- Create table for ingredients
CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient VARCHAR(255) NOT NULL,
    ingredient_name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    purveyor VARCHAR(255),
    ingredient_type VARCHAR(255),
    item_code VARCHAR(255),
    item_size VARCHAR(255)
);

-- Create master table for all menu items
CREATE TABLE menu_items (
    menu_item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL
);

-- Create table for all procedures 
CREATE TABLE procedures (
    proc_id INT AUTO_INCREMENT PRIMARY KEY,
    item_procedure TEXT NOT NULL
);

-- Create table for restrictions
CREATE TABLE restrictions (
    restrictions_id INT AUTO_INCREMENT PRIMARY KEY,
    restriction_type VARCHAR(255) NOT NULL
);

-- Create a junction table linking menu_items and procedures
CREATE TABLE menu_procedures (
    menu_item_id INT,
    proc_id INT,
    PRIMARY KEY (menu_item_id, proc_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (proc_id) REFERENCES procedures(proc_id)
);

-- Create a junction table linking menu_items and ingredients
CREATE TABLE menu_ingredients (
    menu_item_id INT,
    ingredient_id INT,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);

-- Create a junction table linking menu_items and their restrictions
CREATE TABLE menu_restrictions (
    menu_item_id INT,
    restrictions_id INT,
    PRIMARY KEY (menu_item_id, restrictions_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (restrictions_id) REFERENCES restrictions(restrictions_id)
);

-- Create table for vendors with more specific data types and a primary key
CREATE TABLE vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    purveyor VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    contact VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(255),
    ordering_info TEXT,
    deadline VARCHAR(255),
    minimum_order VARCHAR(255)
);

-- Create table for all menu items checklist
CREATE TABLE mise_checklist (
    checklist_id INT AUTO_INCREMENT PRIMARY KEY,
    mise_en_place TEXT NOT NULL
);

-- Create a junction table linking mise_checklist and menu_items
CREATE TABLE menu_mise_checklist (
    menu_item_id INT,
    checklist_id INT,
    PRIMARY KEY (menu_item_id, checklist_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (checklist_id) REFERENCES mise_checklist(checklist_id)
);

