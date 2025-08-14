import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
import time
import os
import json
import shutil
from fuzzy import normalize, fuzz

def db_input():
   db_number = input('Specify which database to update by typing the corresponding number:')
   return db_number
# ------------------------------------------------------------------------------------------

def excel_file_to_upload():
    excel_file_db_number = input('Specify excel file by typing the corresponding number:')
    return excel_file_db_number
# ------------------------------------------------------------------------------------------

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

# Function that creates a dataframe
def create_df(data):

    df= pd.DataFrame(data)
    return df
      
# ------------------------------------------------------------------------------------------

def delete_data(item_ids, db):
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    tables =["menu_items", "menu_prep_list", "menu_req_prep_list", "menu_mise_checklist"]

    for table in tables:
        for id in item_ids:

            cursor.execute(f"SELECT * FROM {table} WHERE menu_item_id = ?", (id,))
            
            to_be_deleted = cursor.fetchall()

            for item in to_be_deleted:
                print(f"\n {item[0]}")

            user_input= input(f"The following will be deleted from {db}. Would you like to proceed? : y / n ")

            if user_input != "y":
                print("❌ Please try again")
                break
            else:
           
                cursor.execute(f"DELETE FROM {table} WHERE menu_item_id = ?", (id,))            

                print(f"✅ Deleted records with menu_item_id {id} from {table}.")

    conn.commit()
    conn.close()
    print("✅ All deletions committed successfully.")


# ------------------------------------------------------------------------------------------

def get_ingredients(db):

    """queries database for all ingredient names and updates json file."""
    
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()

    file_path = "ingredients.json"
    if os.path.exists(file_path):
        print("✅  file_path is correct")
        cursor.execute("""
                        SELECT ingredient_name
                        FROM ingredients
                       """)
        
        ingredients = cursor.fetchall()

        data = [ingredient[0] for ingredient in ingredients]

       # Write the data into a JSON file
        with open(file_path, 'w') as json_file:

            json.dump(data, json_file,indent=2)
    else:
        print("❌ ERROR: standard_menu.json does not exist, will be created.")

    



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

    updated_data = data["menu_items"]
    #print(updated_data)

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    for menu_item in updated_data:
        #print(menu_item["item_name"])
        """ Overwrite existing entry """
        """ Check database to see if item_name exists"""

        cursor.execute( "SELECT menu_item_id, item_name, category FROM menu_items WHERE item_name = ?", (menu_item['item_name'],))
        menu_items = [{"menu_item_id":i[0], "item_name":i[1], "category": i[2]} for i in cursor.fetchall()]

      
        if len(menu_items) == 1:
            print(f"{menu_items[0]['item_name']} exists; item_id: {menu_items[0]['menu_item_id']}")
            update_prompt = input(f"Would you like to overwrite {menu_items[0]['item_name']} in {db}?: y/n  ")
            if update_prompt != "y":
                break
        else:
            print(f"{menu_item['item_name']} does not exist in: {db}")
            proceed_prompt = input(f"would you like to proceed?: y/n  ")
            if proceed_prompt != "y":
                break

            else:
                    
                """" Check database to see if any prep proceedures from the database matches the ones you are trying to input"""

                # Pull all prep procedures from the database and normalize.

                cursor.execute("SELECT prep_id, prep from prep_list")
                db_prep = [{"prep_id": i[0] , "prep": normalize(i[1])} for i in cursor.fetchall()]

                # normalize all prep procedures to input

                normalize_prep = [normalize(i) for i in menu_item['prep']]

                prep_to_upload =[]

                for prep in normalize_prep:
                    for dict_prep in db_prep:
                        if prep == dict_prep["prep"]:
                            prep_to_upload.append(dict_prep)
                            print(f"prep_id: {dict_prep['prep_id'], {prep}}")
                print(prep_to_upload)

                """Check req_prep for existing requisitioned prep"""

                cursor.execute("SELECT * FROM req_prep")

                db_req_prep = [{"req_prep_id": i[0], "prep":i[1], "am_prep_team": i[2], "sous_prep": i[3], "category":i[4]} for i in cursor.fetchall()]

                normalize_req_prep = [normalize(i) for i in menu_item['req_prep'][0]['prep']]

                print(normalize_req_prep)
                        # for req_prep_1 in menu_item["req_prep"]:

                        #     for req_prep_2 in db_req_prep:
                        #         if req_prep_1["prep"] == req_prep_2["prep"]:
                        #             print(req_prep_2)

                        
                            # cursor.execute(
                            #     "INSERT INTO menu_items (item_name) VALUES (?)",
                            #     (item,)
                            # )
                            # menu_item_id = cursor.lastrowid

                            # cursor.execute()
                            # conn.commit()
                            # print(f"✅ New entry:{menu_item_id} ; {item}")
                    #conn.close()
# ------------------------------------------------------------------------------------------

