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


        
        """ Overwrite existing entry """
        """ Check database to see if item_name exists"""

        cursor.execute( "SELECT menu_item_id, item_name, category FROM menu_items WHERE item_name = ?", (menu_item['item_name'],))
        menu_item_result = [{"menu_item_id":i[0], "item_name":i[1], "category": i[2]} for i in cursor.fetchall()]
        
        new_menu_item = {"menu_item_id":0, "item_name":"", "category":""}
        # Pull last menu_item_id from menu_items
        cursor.execute("SELECT MAX(menu_item_id) FROM menu_items")
        last_menu_item_id = cursor.fetchone()[0]

        if len( menu_item_result) == 1:
            print(f"{menu_item_result[0]['item_name']} exists; item_id: { menu_item_result[0]['menu_item_id']}")
            update_prompt = input(f"Would you like to overwrite { menu_item_result[0]['item_name']} in {db}?: y/n  ")
            if update_prompt != "y":
                break
        else:
            print(f"{menu_item['item_name']} does not exist in: {db}")
            proceed_prompt = input(f"would you like to proceed?: y/n  ")
            if proceed_prompt != "y":
                break
            else:
                
                new_menu_item["menu_item_id"] = last_menu_item_id + 1
                new_menu_item["item_name"] = menu_item["item_name"]
                new_menu_item["category"] = menu_item["category"]
                print(f"new menu_item_id: {last_menu_item_id}; new item_name; {menu_item['item_name']}; category: {menu_item['category']}")

       
        """" Check database to see if any prep proceedures from the database matches the ones you are trying to input"""

        # Pull all prep procedures from the database and normalize.

        cursor.execute("SELECT * from prep_list")
        db_prep = [{"prep_id": i[0] , "prep": normalize(i[1])} for i in cursor.fetchall()]

        # normalize all prep procedures to input

        prep_to_upload = [{"prep_id": 0, "prep":normalize(i)} for i in menu_item['prep']]

        #find the last req_prep_id in the req_prep table
        cursor.execute("SELECT MAX(prep_id) FROM prep_list")
        last_prep_id = cursor.fetchone()[0]  


        for prep_1 in prep_to_upload:
            for prep_2 in db_prep:
                if prep_1["prep"] == prep_2["prep"]:
                    prep_1["prep_id"] = prep_2["prep_id"]

        for prep_1 in prep_to_upload:
            if prep_1["prep_id"] == 0:
                last_prep_id += 1
                prep_1["prep_id"] = last_prep_id
                
        print(f"prep_to_upload: {prep_to_upload}")

        """Check req_prep for existing requisitioned prep"""

        cursor.execute("SELECT * FROM req_prep")

        db_req_prep = [{"req_prep_id": i[0], "prep":i[1], "am_prep_team": i[2], "sous_prep": i[3], "category":i[4]} for i in cursor.fetchall()]

        req_prep_to_upload = []

        for req_prep in menu_item["req_prep"]:

            req_prep_to_upload.append({"req_prep_id":0, "prep":normalize(req_prep["prep"]), "am_prep_team": req_prep["am_prep_team"], "sous_prep": req_prep["sous_prep"], "category":req_prep["category"]}) 
        #print(f"req_prep_to_upload: {req_prep_to_upload}")
        #find the last req_prep_id in the req_prep table
        cursor.execute("SELECT MAX(req_prep_id) FROM req_prep")
        last_req_prep_id = cursor.fetchone()[0]  

        # Need to Check if prep is requisitioned, because sometimes there's no prep to be requisitioned...
        if req_prep_to_upload:
            for prep_1 in req_prep_to_upload:
                for prep_2 in db_req_prep:
                    if prep_1["prep"] == prep_2["prep"]:
                        prep_1["req_prep_id"] = prep_2["req_prep_id"]
                        prep_1["am_prep_team"] = prep_2["am_prep_team"]
                        prep_1["sous_prep"] = prep_2["sous_prep"]


            for prep_1 in req_prep_to_upload:
                if prep_1["req_prep_id"] == 0 and len(prep_1["prep"]) > 0:
                    last_req_prep_id += 1
                    prep_1["req_prep_id"] = last_req_prep_id
                print(f"req_prep_id: {last_req_prep_id}")   
            
            
        print(f"req_prep_to_upload: {req_prep_to_upload}")

        """ Check mise_checklist for mise_en_place """

        cursor.execute("SELECT * FROM mise_checklist")
        db_mise = [{"checklist_id":i[0], "mise_en_place":i[1]} for i in cursor.fetchall()]

        mise_to_upload = [{"checklist_id":0, "mise_en_place":normalize(i) }for i in menu_item["mise_en_place"]]


        cursor.execute("SELECT MAX(checklist_id) FROM mise_checklist")
        last_checklist_id = cursor.fetchone()[0]

        for mise_dict in  mise_to_upload:
            for db_mise_dict in db_mise:
                if mise_dict["mise_en_place"] == db_mise_dict["mise_en_place"]:
                    mise_dict["checklist_id"] = db_mise_dict["checklist_id"]

        for mise_dict in mise_to_upload:
            if mise_dict["checklist_id"] == 0:
                last_checklist_id += 1
                mise_dict["checklist_id"] = last_checklist_id
            
            print(f"checklist_id: {last_checklist_id}")
        print(f"mise_en_place: {mise_to_upload}")


        """ Check ingredients for existing ingredient_name """

        cursor.execute("SELECT ingredient_id, ingredient_name FROM ingredients")
        db_ingredients = [{"ingredient_id":i[0], "ingredient_name":i[1]} for i in cursor.fetchall()]

        ingredient_to_upload = [{"ingredient_id":0, "ingredient_name":normalize(i) }for i in menu_item["ingredients"]]


        cursor.execute("SELECT MAX(ingredient_id) FROM ingredients")
        last_ingredient_id = cursor.fetchone()[0]

        for ing in  ingredient_to_upload:
            for db_ing in db_ingredients:
                if ing["ingredient_name"] == db_ing["ingredient_name"]:
                    ing["ingredient_id"] = db_ing["ingredient_id"]

        for ing in ingredient_to_upload:
            if ing["ingredient_id"] == 0:
                last_ingredient_id += 1
                ing["ingredient_id"] = last_ingredient_id
            
            print(f"ingredient_id: {last_ingredient_id}")
        print(f"ingredients_to_upload: {ingredient_to_upload}")
                    
       
        """Insert new data into chosen database"""
            
        # Check if new_menu_item exists
        # if new_menu_item:
        #         cursor.execute(
        #                     """INSERT INTO menu_items (menu_item_id, item_name, category) 
        #                        VALUES (?, ?, ?)""", (new_menu_item['menu_item_id'], new_menu_item['item_name'], new_menu_item['category'])) 
        #  Input new prep in prep_list
        for prep in prep_to_upload:
            cursor.execute("SELECT 1 FROM prep_list WHERE prep_id = ?", (prep['prep_id'], ))
            exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                "INSERT INTO prep_list (prep_id, prep) VALUES (?, ?)", 
                (prep['prep_id'], prep['prep'])
            )

                    #conn.close()
# ------------------------------------------------------------------------------------------
def pull_data(item_id, db):
    pass
# ------------------------------------------------------------------------------------------
