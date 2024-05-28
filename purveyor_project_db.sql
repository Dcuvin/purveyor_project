

-- Create table for ingredients
CREATE TABLE ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT NOT NULL,
    ingredient_name TEXT NOT NULL,
    brand TEXT,
    purveyor TEXT,
    ingredient_type TEXT,
    item_code TEXT,
    item_size TEXT
);

-- Create master table for all menu items
CREATE TABLE menu_items (
    menu_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL
);

-- Create table for all procedures 
CREATE TABLE procedures (
    proc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_procedure TEXT NOT NULL 
);

--Create table for restrictions
CREATE TABLE restrictions (
    restrictions_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restriction_type TEXT NOT NULL  
);


--Create a junction table linkikng menu_items and procedures

CREATE TABLE menu_procedures(
    menu_item_id INTEGER,
    proc_id INTEGER,
    PRIMARY KEY (menu_item_id, proc_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (proc_id) REFERENCES procedures(proc_id)   
);

--Create a junction table linkikng menu_items and ingredients

CREATE TABLE menu_ingredients(
    menu_item_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)   
);

-- Create a junction table linking menu_items and their restrictions
CREATE TABLE menu_restrictions(
    menu_item_id INTEGER,
    restrictions_id INTEGER,
    PRIMARY KEY (menu_item_id, restrictions_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (restrictions_id) REFERENCES restrictions(restrictions_id)   
);

-- Create table for vendors with more specific data types and a primary key
CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purveyor TEXT NOT NULL,
    product TEXT NOT NULL,
    contact TEXT,
    email TEXT,
    phone_number TEXT,
    ordering_info TEXT,
    deadline TEXT,
    minimum_order TEXT  
);

-- Create table for all menu items checklist
CREATE TABLE mise_checklist (
    checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mise_en_place TEXT NOT NULL
);
--Create a junction table linkikng mise_checklist and menu_items

CREATE TABLE menu_mise_checklist(
    menu_item_id INTEGER,
    checklist_id INTEGER,
    PRIMARY KEY (menu_item_id, checklist_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (checklist_id) REFERENCES mise_checklist(checklist_id)   
);