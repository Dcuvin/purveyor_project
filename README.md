# purveyor_project
# Purveyor Project

A Python-based culinary operations tool for automating banquet and events workflows.

This project was built to reduce manual admin work in hospitality by turning event and menu data into structured outputs like prep lists, requisition sheets, checklists, and database-driven menu records. It is centered around banquet/event operations where menus, guest counts, prep needs, and service formats change constantly.

## Why this project exists

Banquet kitchens deal with a moving target:

- Different menus for every event
- Different guest counts, times, and locations
- Repeated manual prep-list creation
- Requisition sheets that need to be rebuilt constantly
- Ingredient and menu data spread across spreadsheets and notes

The goal of this project is to make that workflow faster, more consistent, and easier to scale by combining:

- SQLite for structured menu and prep data
- Excel-based templates and exports
- JSON-based data input
- Fuzzy matching for menu normalization
- OpenAI-powered parsing of event/BEO text
- HTML generation for BEO-style forms

---

## What the project does

At a high level, the project can:

- Upload master Excel data into a SQLite database
- Add or update menu/item data from JSON
- Normalize and fuzzy-match menu items against a standard menu
- Parse copied BEO/event text into structured event info
- Generate Excel prep lists and order sheets
- Generate Word checklists
- Generate prep requisition sheets from event data
- Build HTML dropdowns for BEO-style forms from database data
- Create weekly report folders and fill weekly report workbooks

---

## Core features

### 1. Database-driven menu and prep management
The project uses SQLite as the source of truth for menu items, prep lists, ingredients, stations, categories, and related junction tables.

Examples of supported workflows:

- Upload structured Excel sheets into an existing database
- Pull and update ingredient/menu relationships
- Delete or query records
- Refresh menu data used for matching logic

### 2. BEO / event parsing
Event information can be extracted from copied event text stored in `prompt_file.txt`.

The parser extracts:

- Event name
- Guest count
- Event time
- Event date
- Event type
- Event location
- Food items

Those extracted menu items are then fuzzy-matched against the database to identify menu item IDs and station IDs.

### 3. Prep list generation
The project can generate event-specific prep outputs, including:

- Excel prep sheets
- Order sheets
- Word checklists
- Requisition sheets
- Serveware / pull-sheet style outputs

These files are saved into event-specific folders under `prep_and_checklists/`.

### 4. Weekly reporting workflow
The codebase includes commands for:

- Creating a weekly report folder
- Filling a weekly report workbook from extracted weekly data

This supports a broader event-financial reporting workflow.

### 5. HTML BEO form support
The repo includes Jinja-based HTML templates that can be populated from database values, allowing dropdown menus to be updated dynamically for form-based workflows.

---

## Project structure

A simplified overview of the repo:

```text
purveyor_project/
├── main.py
├── database.py
├── prep_and_check_list.py
├── prep_req.py
├── product_catalog.py
├── fuzzy.py
├── openapi.py
├── beo.py
├── check_file.py
├── excel_format.py
├── beo_form_template.html
├── beo_form_final.html
├── prompt_file.txt
├── db_input_file.json
├── standard_menu.json
├── ingredients.json
├── input_product_catalog.json
├── prep_and_checklists/
├── *.db
├── *.xlsx
└── *.json