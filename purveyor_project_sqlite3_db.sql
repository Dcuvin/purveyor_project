-- Create master table for all menu items
CREATE TABLE menu_items (
    menu_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL

);

-- Create table for all menu items with their corresponding prep
CREATE TABLE prep_list (
    prep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prep TEXT NOT NULL UNIQUE
);



--Create a junction table linkikng prep_list and menu_items

CREATE TABLE menu_prep_list(
    menu_item_id INTEGER,
    item_name TEXT NOT NULL,
    prep_id INTEGER,
    PRIMARY KEY (menu_item_id, prep_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (prep_id) REFERENCES prep_list(prep_id)   
);

--Create a table with prep items that can be requisitioned from the AM prep team, using the main prep items in prep_list as reference.
CREATE TABLE req_prep (
    req_prep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prep TEXT NOT NULL UNIQUE,
    am_prep_team BOOLEAN NOT NULL DEFAULT 0,
    sous_prep BOOLEAN NOT NULL DEFAULT 0,
    category TEXT NOT NULL
);


-- Create a junction linking menu_items with requisition_prep

CREATE TABLE menu_req_prep_list(
    menu_item_id INTEGER,
    item_name TEXT NOT NULL,   
    req_prep_id INTEGER,
    PRIMARY KEY (menu_item_id, req_prep_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN kEY (item_name) REFERENCES menu_items(item_name),
    FOREIGN KEY (req_prep_id) REFERENCES req_prep(req_prep_id)   
);

-- Create table for all menu items checklist
CREATE TABLE mise_checklist (
    checklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mise_en_place TEXT NOT NULL UNIQUE
);
--Create a junction table linkikng mise_checklist and menu_items

CREATE TABLE menu_mise_checklist(
    menu_item_id INTEGER,
    item_name TEXT NOT NULL,
    checklist_id INTEGER,
    PRIMARY KEY (menu_item_id, checklist_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (checklist_id) REFERENCES mise_checklist(checklist_id)   
);



-- Create table for ingredients
CREATE TABLE ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purveyor TEXT,
    ingredient_code TEXT NOT NULL, 
    ingredient_description TEXT,   
    ingredient_name TEXT,
    pack_size_unit TEXT,
    purchase_price REAL NOT NULL DEFAULT 0.0,
    ingredient_type TEXT

);

--Create a junction table linkikng menu_items and ingredients

CREATE TABLE menu_ingredients(
    menu_item_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)   
);


-- Create a table for stations

CREATE TABLE stations(
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_name TEXT NOT NULL   
);

-- Create a junction table to group certain menu_items to stations

CREATE TABLE menu_items_stations(
    station_id INTEGER,
    station_name TEXT NOT NULL,   
    menu_item_id INTEGER,
    PRIMARY KEY (station_id, menu_item_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)   
);


-- Create table for all categories
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);



--Create a junction table linkikng menu_items and categories

CREATE TABLE menu_items_categories(
    menu_item_id INTEGER,
    item_name TEXT NOT NULL,
    category_name TEXT NOT NULL,
    category_id INTEGER,
    PRIMARY KEY (menu_item_id, category_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)   
);

--Create a junction table for ordering purposes linking menu_items to purchasing table.
CREATE TABLE menu_items_purchasing(
    menu_item_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(menu_item_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)   
);
--Create a dietary table for restrictions.
CREATE TABLE dietary (
    dietary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dietary_name TEXT NOT NULL
    
);

--Delete a table

DROP TABLE table_name;

-- Empty a table

DELETE FROM table_name;

--Add column
ALTER TABLE table_name
ADD COLUMN column_name;

--Show table structure
PRAGMA table_info(menu_items);

--Rename a table column
ALTER TABLE table_name RENAME COLUMN old_column_name TO new_column_name;
ALTER TABLE ingredients RENAME COLUMN uom TO pack_size_unit;

--menu_items:ingredeints query

SELECT menu_ingredients.menu_item_id,   ingredients.ingredient_name, ingredients.ingredient_id, ingredients.ingredient_name, ingredients.purveyor, ingredients.ingredient_code, ingredients.pack_size_unit, ingredients.purchase_price
FROM ingredients
JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
WHERE menu_ingredients.menu_item_id = 1;

--menu_items:ingredeints query

SELECT ingredient_id FROM menu_ingredients WHERE menu_item_id = 1;

INSERT OR IGNORE INTO stations (station_name) VALUES
('holiday party'),
('breakfast station'),
('continental breakfast'),
('breakfast sandwich station'),
 ('sandwiches'),
('grain bowls'),
('hearty salads'),
('sweet & savory snacks'),
('chips & dips'),
('afternoon tea station'),
('cheese & charcuterie'),
('raw bar'),
('crudite & mezze'),
("farmer's green market"),
('a taste of nine orchard');

INSERT OR IGNORE INTO categories (category_name) VALUES
('canape'),
('passed small plates'),
('plated starter'),
('plated entree'),
('family starter'),
('family entree'),
('plated breakfast'),
('station'),
('sides');