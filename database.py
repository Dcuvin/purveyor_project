import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
import time
import os
import json
import shutil



def upload_excel(name_of_excel_file, db):
    
    table_name = ['menu_items', 'prep_list', 'menu_prep_list',
                  'req_prep','menu_req_prep_list', 'mise_checklist', 'menu_mise_checklist','ingredients',
                  'menu_ingredients','stations','menu_items_stations', 
                  'categories', 'menu_items_categories']
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Load the Excel file
    # To read all sheets, use sheet_name=None
    #.read_excel creates a dictionary
    excel_data = pd.read_excel(name_of_excel_file, sheet_name= None)
    # Replace NaN values with 'n/a'. This is done iteratively due to the excel file having several sheets.
    for key in excel_data:
        excel_data[key].fillna('n/a', inplace=True)
        
    # Check if tables in the database exists
    verified_tables = []
    
    for name in table_name:
        
        try:
            cursor.execute(f'SELECT * FROM {name}')
            verified_tables.append(name)

        except sqlite3.OperationalError:

            continue
    print(verified_tables)

    if len(verified_tables) != len(table_name):
    
        print("❌ Error with uploading excel file!")

    else:
    
        for sheet_name, df in excel_data.items():
            print(f"✅ Uploading sheet: {sheet_name}")
            # Drop the table if it exists before replacing it with new data
            # this helped solve the locked table that kept occuring
            #cursor.execute(f'DROP TABLE IF EXISTS {sheet_name}')
            # Clear all data from the table while keeping its schema intact.
            cursor.execute(f'DELETE FROM {sheet_name}')
            conn.commit()                         # ← flush the delete
            # Append the new data to the existing (now empty) table.
            #df.to_sql(sheet_name, conn, if_exists='append', index=False)
    
            df.to_sql(sheet_name, conn, if_exists='replace', index=False)
       
    # Commit the transaction
    conn.commit()
        
    # Close the connection
    conn.close()
    print("✅ Excel file upload successful!")

    # Make a copy of db excel file just in case
    cwd = os.getcwd()
    backup_name = f"copy_{name_of_excel_file}"
    dest_path = os.path.join(cwd, backup_name)

    shutil.copy2(name_of_excel_file, dest_path)

    print(f"✅ Copied:\n  {name_of_excel_file}\n→ {dest_path}")

# ------------------------------------------------------------------------------------------

def input_new_data(db):

    #Check filepath
    file_path = "db_input_file.json"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing content
    with open("db_input_file.json", 'r') as file:
        #data is a list of dict
        data = json.load(file)

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    for dict_item in data:
        item_name = dict_item["item_name"]
        #prep = dict_item["prep"]
        #req_prep = dict_item["req_prep"]
        #mise_checklist =dict_item["mise_checklist"]
        #ingredients = dict_item["ingredients"]
        #stations = dict_item["stations"]

        """Check to see if menu_item exists"""
        print(item_name)
        cursor.execute( "SELECT menu_item_id FROM menu_items WHERE item_name = ?", (item_name,))
        result = cursor.fetchone()
        print(result)

        if result:
            menu_item_id = result[0]
            print(f"menu_item exist: {menu_item_id}")
        else:
            
            cursor.execute(
                "INSERT INTO menu_items (item_name) VALUES (?)",
                (item_name,)
            )
            menu_item_id = cursor.lastrowid
            conn.commit()
            print(f"✅ New entry:{menu_item_id} ; {item_name}")
        conn.close()

# Function that creates a dataframe
def create_df(data):

    df= pd.DataFrame(data)
    return df
      