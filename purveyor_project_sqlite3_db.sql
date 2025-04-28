

-- Create table for ingredients
CREATE TABLE ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT NOT NULL,
    ingredient_name TEXT NOT NULL,
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
    menu_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    checklist_id INTEGER,
    PRIMARY KEY (menu_item_id, checklist_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (checklist_id) REFERENCES mise_checklist(checklist_id)   
);
            
-- Create table for master_product_catalog imported from xtraCHEF
CREATE TABLE master_product_catalog (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    item_description TEXT NOT NULL,
    vendor TEXT NOT NULL,
    item_code TEXT NOT NULL,
    pack_size_unit TEXT NOT NULL
);

-- Create table for all menu items with their corresponding prep
CREATE TABLE prep_list (
    prep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prep TEXT NOT NULL,
    rec_prep BOOLEAN NOT NULL DEFAULT 0,
    sous_prep BOOLEAN NOT NULL DEFAULT 0
);
--Create a junction table linkikng prep_list and menu_items

CREATE TABLE menu_prep_list(
    menu_item_id INTEGER,
    prep_id INTEGER,
    PRIMARY KEY (menu_item_id, prep_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (prep_id) REFERENCES prep_list(prep_id)   
);
--Create a table with prep items that can be requisitioned from the AM prep team, using the main prep items in prep_list as reference.
CREATE TABLE req_prep (
    req_prep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prep TEXT NOT NULL
);

-- Create a junction linking menu_items with requisition_prep

CREATE TABLE req_menu_prep_list(
    menu_item_id INTEGER,
    req_prep_id INTEGER,
    PRIMARY KEY (menu_item_id , req_prep_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(menu_item_id),
    FOREIGN KEY (rec_prep_id) REFERENCES requisitioned_prep(rec_prep_id)   
);
--Delete a table

DROP TABLE table_name;

