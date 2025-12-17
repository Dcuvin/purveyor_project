# Queries database for all up-to-date menu_items and updates standard_menu.json
import os #This statement is used to include the functionality of the os module, allowing you to interact with the operating system in a portable way
import sqlite3
import json
from rapidfuzz import process, fuzz
import re

def update_standard_menu(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT item_name FROM menu_items;")
    item_names = [row[0] for row in cursor.fetchall()]  # Cleaner list comprehension

    cursor.execute("SELECT station_name FROM stations;")
    station_names = [row[0] for row in cursor.fetchall()]
    conn.close()

    #print(item_names)

    file_path = "standard_menu.json"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("❌ ERROR: standard_menu.json does not exist, will be created.")

    # Write the menu list to the JSON file
    with open(file_path, 'w') as file:
        json.dump(item_names, file, indent=4)
        print("✅ standard_menu.json has been updated!")
    # Updates standard_station_menu.json
    file_path = "standard_station_menu.json"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("❌ ERROR: standard_staion_menu.json does not exist, will be created.")

    # Write the staion_names list to the JSON file
    with open(file_path, 'w') as file:
        json.dump(station_names, file, indent=4)
        print("✅ standard_menu.json has been updated!")
#----------------------------------------------------------------------------

def get_standard_menu():
    file_path = "standard_menu.json"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("❌ ERROR: standard_menu.json does not exist, will be created.")

    # Write the menu list to the JSON file
    data = " "
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data

    #print(data)
    #----------------------------------------------------------------------------

def get_standard_station_menu():
    file_path = "standard_station_menu.json"
    if os.path.exists(file_path):
        print("✅  file_path is correct")
    else:
        print("❌ ERROR: standard_menu.json does not exist, will be created.")

    # Write the menu list to the JSON file
    data = " "
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data

    #print(data)


#----------------------------------------------------------------------------

def normalize(text):
    try:
        text = text.lower()
        text = text.replace("&", " and ")
        text = re.sub(r"[^a-z0-9%/.\-\s]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text.strip()
    except:
        return
#----------------------------------------------------------------------------

def match_menu_items(item, choices, threshold=85):
    normalized_item = normalize(item)
    normalized_choices = [normalize(choice) for choice in choices]
    match, score, _ = process.extractOne(normalized_item, normalized_choices, scorer=fuzz.token_set_ratio)
    if score >= threshold:
        return choices[normalized_choices.index(match)]
    else:
        return None
    
#----------------------------------------------------------------------------

def fuzzy_match(upload_item, db_item, threshold=95):
    normalized_upload_item = normalize(upload_item)
    normalized_db_item = normalize(db_item)
    score = fuzz.token_set_ratio(normalized_upload_item, normalized_db_item)
    
    return score >= threshold
    
