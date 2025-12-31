import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
import time
import os
import json
import shutil
from fuzzy import normalize, fuzzy_match
from tabulate import tabulate


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

    # ✅ Enable foreign key enforcement for this connection
    #cursor.execute("PRAGMA foreign_keys = ON;")
    # Load the Excel file
    # To read all sheets, use sheet_name=None
    #.read_excel creates a dictionary
    excel_data = pd.read_excel(name_of_excel_file, sheet_name= None)
    # Replace NaN values with 'n/a'. This is done iteratively due to the excel file having several sheets.
    for key in excel_data:
        excel_data[key].fillna('n/a', inplace=True)
        
#     # Check if tables in the database exists
        verified_tables = []
        for table in table_name:
        
            try:
                cursor.execute(f"SELECT 1 FROM {table} LIMIT 1;")
                verified_tables.append(table)

            except sqlite3.OperationalError:

                continue

        if len(verified_tables) != len(table_name):
    
            print("❌ Error with uploading master_sheets!")

        else:
            for sheet_name, df in excel_data.items():
                    print(f"✅ Uploading sheet: {sheet_name}")
                     # Clear all data from the table while keeping its schema intact.
                    cursor.execute(f'DELETE FROM {sheet_name}')        
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
        print("✅  file_path is correct; ingredients.json updated")
        cursor.execute("""
                        SELECT ingredient_id, purveyor, ingredient_code, ingredient_name 
                        FROM ingredients
                       """)


        rows = cursor.fetchall()
        headers = [d[0] for d in cursor.description]

       # Write the data into a JSON file
        with open(file_path, 'w') as json_file:

            json_file.write(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("❌ ERROR: standard_menu.json does not exist, will be created.")



# ------------------------------------------------------------------------------------------

def input_update_data(db):

    #Check filepath
    file_path = "db_input_file.json"
    #file_path = "pulled_db_data.json"
    #file_path ="pulled_db_data copy.json"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing content
    with open(file_path, 'r') as file:
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
        
        new_menu_item = None
     
        if len(menu_item_result) == 1:
            # print(f"{menu_item_result[0]['item_name']} exists; item_id: { menu_item_result[0]['menu_item_id']}")
            # update_prompt = input(f"Would you like to overwrite { menu_item_result[0]['item_name']} in {db}?: y/n  ")
            # if update_prompt != "y":
               #continue
            new_menu_item = None
        else:
            print(f"{menu_item['item_name']} does not exist in: {db}")
            proceed_prompt = input(f"would you like to proceed?: y/n  ")
            if proceed_prompt != "y":
                continue
            new_menu_item = {
                            "item_name": menu_item["item_name"],
                            "category": menu_item["category"]
                            }
        """" Check database to see if any prep proceedures from the database matches the ones you are trying to input"""

        # Pull all prep procedures from the database and normalize.

        cursor.execute("SELECT * from prep_list")
        db_prep = [{"prep_id": i[0] , "prep": normalize(i[1])} for i in cursor.fetchall()]

        # normalize all prep procedures to input

        prep_to_upload = [{"prep_id": 0, "prep":normalize(i)} for i in menu_item['prep']]
        #find the last req_prep_id in the req_prep table
        for new_prep in prep_to_upload:
            for existing_prep in db_prep:
                if new_prep["prep"] == existing_prep["prep"]:
                    new_prep["prep_id"] = existing_prep["prep_id"]

        """Check req_prep for existing requisitioned prep"""

        cursor.execute("SELECT * FROM req_prep")

        db_req_prep = [{"req_prep_id": i[0], "prep":i[1], "am_prep_team": i[2], "sous_prep": i[3], "category":i[4]} for i in cursor.fetchall()]

        req_prep_to_upload = []

        # iterate over req_prep since it's a list of dictionaries
        for req_prep in menu_item["req_prep"]:

            req_prep_to_upload.append({"req_prep_id":0, "prep":normalize(req_prep["prep"]), "am_prep_team": req_prep["am_prep_team"], "sous_prep": req_prep["sous_prep"], "category":req_prep["category"]}) 

        #print(f"req_prep_to_upload: {req_prep_to_upload}")
        

        # Need to Check if prep is requisitioned, because sometimes there's no prep to be requisitioned...
        if req_prep_to_upload:
            for prep_1 in req_prep_to_upload:
                for prep_2 in db_req_prep:
                    if prep_1["prep"] == prep_2["prep"]:
                        prep_1["req_prep_id"] = prep_2["req_prep_id"]
                        prep_1["am_prep_team"] = prep_2["am_prep_team"]
                        prep_1["sous_prep"] = prep_2["sous_prep"]
                        prep_1["category"] = prep_2["category"]


            
        #print(f"req_prep_to_upload: {req_prep_to_upload}")

        """ Check mise_checklist for mise_en_place """

        cursor.execute("SELECT * FROM mise_checklist")
        db_mise = [{"checklist_id":i[0], "mise_en_place":i[1]} for i in cursor.fetchall()]

        mise_to_upload = [{"checklist_id":0, "mise_en_place":normalize(i) }for i in menu_item["mise_en_place"]]


        for mise_dict in  mise_to_upload:
            for db_mise_dict in db_mise:
                if mise_dict["mise_en_place"] == db_mise_dict["mise_en_place"]:
                    mise_dict["checklist_id"] = db_mise_dict["checklist_id"]

        print(f"mise_en_place: {mise_to_upload}")


        """ Check ingredients for existing ingredient_name """

        cursor.execute("SELECT ingredient_id, purveyor, ingredient_name FROM ingredients")
        db_ingredients = [{"ingredient_id":i[0],"purveyor":i[1],"ingredient_name":normalize(i[2])} for i in cursor.fetchall()]

        ingredient_to_upload = []
        for ing in menu_item["ingredients"]:
           
            ingredient_to_upload.append({"ingredient_id":0, "purveyor": normalize(ing["purveyor"]), "ingredient_name":normalize(ing["ingredient"])})

        #print(ingredient_to_upload)
        #break
        for ing in ingredient_to_upload:
            matches =[]
            for db_ing in db_ingredients:
                score = fuzzy_match(ing["ingredient_name"], db_ing["ingredient_name"]) + fuzzy_match(ing["purveyor"], db_ing["purveyor"])
                matches.append({"score":score,
                                "ingredient_id":db_ing["ingredient_id"], 
                                "purveyor":db_ing["purveyor"],
                                "ingredient_name":db_ing["ingredient_name"]})
            # sort by highest score
            matches.sort(key=lambda x: x["score"], reverse=True)
            best_match =matches[0]
            ing["ingredient_id"] = best_match["ingredient_id"]
            ing["purveyor"] = best_match["purveyor"]
            ing["ingredient_name"] = best_match["ingredient_name"]
       
            print(f"🍽️ ingredients_to_upload: {ingredient_to_upload}")


        """ Check to see if new menu item belongs to a station and pull the station_id and station_name """
        #pull all existing station names and compare
        cursor.execute("SELECT station_name FROM stations")
        existing_stations =[i[0] for i in cursor.fetchall()]
        station_names = []
        station_to_upload = {}

        if menu_item["menu_items_stations"]:
            for existing_station in existing_stations:
                for station in menu_item["menu_items_stations"]:
                    if fuzzy_match(existing_station, station):
                        station_names.append(existing_station)
        
        #if menu_item["menu_items_stations"]:
            #for station in menu_item["menu_items_stations"]:
            for name in station_names:
                cursor.execute("SELECT * FROM stations WHERE station_name = ?", (name,))
                results = cursor.fetchone()
                if results:
                        station_to_upload['station_id']= results[0]       
                        station_to_upload['station_name'] = results[1]
                else:
                    continue

        """ Pull category_id and category_name """
        #pull all existing category names and compare
        cursor.execute("SELECT category_name FROM categories")
        existing_categories=[i[0] for i in cursor.fetchall()]
        category_names =[]
        category_to_upload ={}
        if menu_item["menu_items_category"]:
            for existing_category in existing_categories:
                for category in menu_item["menu_items_category"]:
                    if fuzzy_match(existing_category,category):
                        category_names.append(existing_category)

            for category in category_names:
                cursor.execute("SELECT * FROM categories WHERE category_name = ?", (category,))

                results = cursor.fetchone()
                if results:
                    
                    category_to_upload["category_id"] = results[0]
                    category_to_upload["category_name"] = results[1]
                else:
                    continue
        
        #print(existing_stations)
        #print(station_names)
        print(station_to_upload)
        print(category_to_upload)

        """Pull all ingredients from purchasing table"""
        cursor.execute("SELECT ingredient_id, ingredient_name, purveyor, item_code FROM purchasing")
        db_purchasing = [{"ingredient_id":i[0], "ingredient_name":i[1], "purveyor":i[2], "item_code":i[3]} for i in cursor.fetchall()]
        purchasing_to_upload = []
        for ing in menu_item["purchasing"]:
           
            purchasing_to_upload.append({"ingredient_id":0, "ingredient_name":normalize(ing["ingredient"]), "purveyor": normalize(ing["purveyor"]),"item_code":ing["sku"]})

        """Normalize and fuzzy match all existing ingredients from purchasing table with ingredients (purchasing) to upload"""
        """"""
        for ing in purchasing_to_upload:
            matches =[]
            for db_ing in db_purchasing:
                score = fuzzy_match(ing["ingredient_name"], db_ing["ingredient_name"]) + fuzzy_match(ing["purveyor"], db_ing["purveyor"])
                if score:
                    matches.append({"score":score,
                                        "ingredient_id":db_ing["ingredient_id"], 
                                        "purveyor":db_ing["purveyor"],
                                        "ingredient_name":db_ing["ingredient_name"],
                                        "item_code":db_ing["item_code"]
                                        })
                    # sort by highest score
                    matches.sort(key=lambda x: x["score"], reverse=True)
                    best_match =matches[0]
                    ing["ingredient_id"] = best_match["ingredient_id"]
                    ing["purveyor"] = best_match["purveyor"]
                    ing["ingredient_name"] = best_match["ingredient_name"]
                    ing["item_code"]= best_match["item_code"]
                    
       
                print(f"💰 purchasing_to_upload: {purchasing_to_upload}")

     
        #break
        """Insert new data into chosen database""" 
        # Check if new_menu_item exists
        new_menu_item_id = 0
        if new_menu_item:

            cursor.execute(
                        """INSERT INTO menu_items (item_name, category) 
                           VALUES (?, ?)""", (new_menu_item['item_name'], new_menu_item['category'][0],)) 
            new_menu_item_id = cursor.lastrowid
            print(f"✅ new_menu_item: {new_menu_item_id}, {new_menu_item['item_name']} has been added!")
            
            # Insert prep into prep_list
            for prep in prep_to_upload:
                cursor.execute("INSERT OR IGNORE INTO prep_list(prep) VALUES (?)", (prep['prep'],))

            # Pull prep_ids
            for prep in prep_to_upload:
                cursor.execute("SELECT * FROM prep_list WHERE prep = ?", (prep['prep'],))
                result = cursor.fetchone()
                if result:
                    prep['prep_id'] = result[0]

                print(f"✅ prep_list: {prep} has been added!")


            # Map new_menu_item to new / existing prep in menu_prep_list
            for prep in prep_to_upload:
                cursor.execute("INSERT OR IGNORE INTO menu_prep_list (menu_item_id, item_name, prep_id) VALUES (?,?,?)", (new_menu_item_id, new_menu_item['item_name'], prep['prep_id'],))
                print(f"✅ menu_prep_list: {new_menu_item_id}, {new_menu_item['item_name']}, {prep['prep_id']} has been added!")

            # Insert new/existing requisition prep into req_prep
            for req_prep in req_prep_to_upload:
                cursor.execute("""INSERT OR IGNORE INTO req_prep (prep, am_prep_team, sous_prep, category)
                                VALUES (?, ? ,?, ?)""", (req_prep['prep'], req_prep['am_prep_team'], req_prep['sous_prep'], req_prep['category'],))

            # Pull req_prep ids
            for req_prep in req_prep_to_upload:
                cursor.execute("SELECT * FROM req_prep WHERE prep = ?", (req_prep['prep'],))
                result = cursor.fetchone()
                if result:
                    req_prep['req_prep_id'] = result[0]

                print(f"✅ req_prep:  {req_prep} has been added!")

            
            # Map new_menu_item to new / existing prep in menu_req_prep_list
            for req_prep in req_prep_to_upload:
                cursor.execute("INSERT OR IGNORE INTO menu_req_prep_list VALUES (?,?,?)", (new_menu_item_id, new_menu_item['item_name'], req_prep['req_prep_id'],))
                print(f"✅ menu_req_prep: {new_menu_item_id}, {new_menu_item['item_name']}, {req_prep['req_prep_id']} has been added!")

            # Insert new/existing mise into mise_checklist
            for mise in mise_to_upload:
                cursor.execute("""INSERT OR IGNORE INTO mise_checklist (mise_en_place)
                                VALUES (?)""", (mise['mise_en_place'],))
            # Pull checklist_ids
            for mise in mise_to_upload:
                cursor.execute("SELECT * FROM mise_checklist WHERE mise_en_place= ?",(mise['mise_en_place'],))
                result = cursor.fetchone()
                if result:
                    mise['checklist_id'] = result[0]
                print(f"✅ mise_checklist: {mise} has been added!")
                
            # Map checklist_id to new_menu_item_id in menu_mise_checklist
            for mise in mise_to_upload:
                cursor.execute("INSERT OR IGNORE INTO menu_mise_checklist VALUES (?,?,?)", (new_menu_item_id, new_menu_item['item_name'], mise['checklist_id'],))
                print(f"✅ menu_mise_checklist: {new_menu_item_id}, {new_menu_item['item_name']}, {mise['checklist_id']} has been added!")

            
            # Map ingredient_id to new_menu_item_id in menu_ingredients
            for ingredient in ingredient_to_upload:
                cursor.execute("INSERT OR IGNORE INTO menu_ingredients VALUES (?,?)", (new_menu_item_id, ingredient['ingredient_id'],))
                print(f"✅ menu_ingredient: {ingredient} ")

            # Map station_id to new_menu_item_id if it exists
            if station_to_upload:
                cursor.execute("INSERT OR IGNORE INTO menu_items_stations VALUES (?,?,?)", (station_to_upload['station_id'], station_to_upload['station_name'], new_menu_item_id, ))

                print(f"✅ menu_item_stations:{station_to_upload['station_id'],station_to_upload['station_name']} has been added! ")
            else:
                continue
            
            

            # Map categories to menu_items_categories
            if category_to_upload:
                
                cursor.execute("INSERT OR IGNORE INTO menu_items_categories VALUES (?, ?, ?, ?)", (new_menu_item_id, new_menu_item['item_name'], category_to_upload['category_id'],category_to_upload['category_name'],))
            print(f"✅ menu_items_categories: {new_menu_item_id,new_menu_item['item_name'],category_to_upload['category_id'],category_to_upload['category_name']} has been added! ")

            # Insert purchasing ingredient_id to new_menu_item_id in purchasing table
            for purchase in purchasing_to_upload:
                cursor.execute("INSERT OR IGNORE INTO purchasing (ingredient_name, purveyor, item_code) VALUES (?,?,?)", (purchase['ingredient_name'], purchase['purveyor'], purchase['item_code'],))

                print(f"✅ purchasing: {purchase['ingredient_name']}, {purchase['purveyor']},{purchase['item_code']} has been added! ")

                # cursor.execute("INSERT OR IGNORE INTO purchasing VALUES (?,?,?,?)", (purchase['ingredient_id'], purchase['ingredient_name'], purchase['purveyor'], purchase['item_code'],))

                # print(f"✅ purchasing: {purchase['ingredient_id']}, {purchase['ingredient_name']}, {purchase['purveyor']},{purchase['item_code']} has been added! ")

            # Map menu_items_purchasing to new_menu_item_id
            for purchase in purchasing_to_upload:
                   
            #        cursor.execute("INSERT OR IGNORE INTO menu_items_purchasing (menu_item_id, item_name, ingredient_name) VALUES (?, ?, ?, ?)", (new_menu_item_id, new_menu_item['item_name'],purchase['ingredient_name'],))
            # print(f"✅ menu_items_purchasing: {new_menu_item_id,new_menu_item['item_name'],purchase['ingredient_name']} has been added! ")

                   cursor.execute("INSERT OR IGNORE INTO menu_items_purchasing VALUES (?, ?, ?, ?)", (new_menu_item_id, new_menu_item['item_name'], purchase['ingredient_id'],purchase['ingredient_name'],))
            print(f"✅ menu_items_purchasing: {new_menu_item_id,new_menu_item['item_name'],purchase['ingredient_id'],purchase['ingredient_name']} has been added! ")

        else:
            """"If menu_item already exists, but you want to overwrite the data"""
            existing_menu_item_id = menu_item_result[0]['menu_item_id']
            if menu_item_result:
               
                # Insert prep into prep_list
                for prep in prep_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO prep_list(prep) VALUES (?)", (prep['prep'],))

                # Pull prep_ids
                for prep in prep_to_upload:
                    cursor.execute("SELECT * FROM prep_list WHERE prep = ?", (prep['prep'],))
                    result = cursor.fetchone()
                    if result:
                        prep['prep_id'] = result[0]

                    print(f"✅ prep_list: {prep} has been added!")

                # Delete existing mappings in menu_prep_list prior to overwrite
                for prep in prep_to_upload:
                    cursor.execute("DELETE FROM menu_prep_list WHERE menu_item_id = ?", (existing_menu_item_id,))
                    print(f"✅ Old menu_prep_list mappings deleted for: {existing_menu_item_id}, {menu_item_result[0]['item_name']}")

                # Map new_menu_item to new / existing prep in menu_prep_list
                for prep in prep_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_prep_list (menu_item_id, item_name, prep_id) VALUES (?,?,?)", (existing_menu_item_id, menu_item_result[0]['item_name'], prep['prep_id'],))
                    print(f"✅ menu_prep_list: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {prep['prep_id']} has been added!")
                
                # Delete existing mappings in req_prep prior to overwrite
                for req_prep in req_prep_to_upload:
                    cursor.execute("DELETE FROM menu_req_prep_list WHERE menu_item_id = ?", (existing_menu_item_id,))
                    print(f"✅ Old menu_req_prep_list mappings deleted for: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {req_prep}")

                # Insert new/existing requisition prep into req_prep
                for req_prep in req_prep_to_upload:
                    cursor.execute("""INSERT OR IGNORE INTO req_prep (prep, am_prep_team, sous_prep, category)
                                    VALUES (?, ? ,?, ?)""", (req_prep['prep'], req_prep['am_prep_team'], req_prep['sous_prep'], req_prep['category'],))

                # Pull req_prep ids
                for req_prep in req_prep_to_upload:
                    cursor.execute("SELECT * FROM req_prep WHERE prep = ?", (req_prep['prep'],))
                    result = cursor.fetchone()
                    if result:
                        req_prep['req_prep_id'] = result[0]

                    print(f"✅ req_prep: {req_prep} has been added!")

                # Delete existing req_prep mappings in menu_prep_list prior to overwrite
                for req_prep in req_prep_to_upload:
                    cursor.execute("DELETE FROM menu_req_prep_list WHERE menu_item_id = ?", (existing_menu_item_id,))
                    print(f"✅ Old menu_req_prep_list mappings deleted for: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {req_prep}")
                
                # Map menu_item_result to new / existing prep in menu_req_prep_list
                for req_prep in req_prep_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_req_prep_list VALUES (?,?,?)", (existing_menu_item_id, menu_item_result[0]['item_name'], req_prep['req_prep_id'],))
                    print(f"✅ menu_req_prep: {req_prep['req_prep_id']}, {menu_item_result[0]['item_name']}, {req_prep['prep']} has been added!")
                # Insert ingredient in purchasing table

                # Insert purchasing ingredient_id to new_menu_item_id in purchasing table
                for purchasing in purchasing_to_upload:

                    cursor.execute("INSERT OR IGNORE INTO purchasing (ingredient_name, purveyor, item_code) VALUES  (?,?,?)", (purchasing['ingredient_name'], purchasing['purveyor'], purchasing['item_code'],))

                    print(f"✅ purchasing: {purchasing['ingredient_name']}, {purchasing['purveyor']},{purchasing['item_code']} has been added! ")

                    # cursor.execute("INSERT OR IGNORE INTO purchasing VALUES (?,?,?,?)", ( purchasing["ingredient_id"], purchasing['ingredient_name'], purchasing['purveyor'], purchasing['item_code'],))

                    # print(f"✅ purchasing:{purchasing["ingredient_id"]}, {purchasing['ingredient_name']}, {purchasing['purveyor']},{purchasing['item_code']} has been added! ")        

                # Delete existing purchasing mappings in menu_items_purchasing prior to overwrite
                for purchasing in purchasing_to_upload:
                    cursor.execute("DELETE FROM menu_items_purchasing WHERE menu_item_id = ?", (existing_menu_item_id,))
                    print(f"✅ Old menu_items_purchasing mappings deleted for: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {purchasing['ingredient_name']}, {purchasing['purveyor']}, {purchasing['item_code']}")
                
                # Map purchasing to new / existing prep in menu_req_prep_list
                for purchasing in purchasing_to_upload:

                    # cursor.execute("INSERT OR IGNORE INTO menu_items_purchasing (menu_item_id, item_name, ingredient_name) VALUES (?, ?, ?)", (existing_menu_item_id, menu_item_result[0]['item_name'],purchasing['ingredient_name'],))
                    
                    # print(f"✅ menu_items_purchasing: {existing_menu_item_id}, {menu_item_result[0]['item_name']},{purchasing['ingredient_name']}, {purchasing['purveyor']} has been added!")

                    cursor.execute("INSERT OR IGNORE INTO menu_items_purchasing VALUES (?,?,?,?)", (existing_menu_item_id, menu_item_result[0]['item_name'],purchasing["ingredient_id"], purchasing['ingredient_name'],))

                    print(f"✅ menu_items_purchasing: {existing_menu_item_id}, {menu_item_result[0]['item_name']},{purchasing['ingredient_name']}, {purchasing['purveyor']} has been added!")

                # Insert new/existing mise into mise_checklist
                for mise in mise_to_upload:
                    cursor.execute("""INSERT OR IGNORE INTO mise_checklist (mise_en_place)
                                    VALUES (?)""", (mise['mise_en_place'],))
                # Pull checklist_ids
                for mise in mise_to_upload:
                    cursor.execute("SELECT * FROM mise_checklist WHERE mise_en_place= ?",(mise['mise_en_place'],))
                    result = cursor.fetchone()
                    if result:
                        mise['checklist_id'] = result[0]
                    print(f"✅ mise_checklist:{mise} has been added!")

                # Delete existing mappings in menu_mise_checklist prior to overwrite
                for mise in mise_to_upload:
                    
                    cursor.execute("DELETE FROM menu_mise_checklist WHERE menu_item_id = ?", (existing_menu_item_id,))
                    print(f"✅ Old menu_mise_checklist mappings deleted for: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {mise}")
                    
                # Map checklist_id to existing_menu_item_id in menu_mise_checklist
                for mise in mise_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_mise_checklist VALUES (?,?,?)", (existing_menu_item_id, menu_item_result[0]['item_name'], mise['checklist_id'],))
                    print(f"✅ menu_mise_checklist: {existing_menu_item_id}, {menu_item_result[0]['item_name']}, {mise['checklist_id']} has been added!")

                # Map ingredient_id to new_menu_item_id in menu_ingredients
                for ingredient in ingredient_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_ingredients VALUES (?,?)", (existing_menu_item_id, ingredient['ingredient_id'],))
                    print(f"✅ menu_ingredient: {ingredient} ")

                # Map station_id to new_menu_item if it exists
                
                if station_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_items_stations VALUES (?,?,?)", (station_to_upload['station_id'], station_to_upload['station_name'], existing_menu_item_id, ))

                    print(f"✅ menu_item_stations: {station_to_upload['station_id'],station_to_upload['station_name']} has been added! ")
                else:
                    continue
                # Map category_id to new_menu_item_id
                
                if category_to_upload:
                    cursor.execute("INSERT OR IGNORE INTO menu_items_categories VALUES (?, ?, ?, ?)", (existing_menu_item_id, menu_item_result[0]['item_name'], category_to_upload['category_id'],category_to_upload['category_name'],))
                    print(f"✅ menu_items_categories: {existing_menu_item_id}, {menu_item_result[0]['item_name']},{ category_to_upload['category_id'],category_to_upload['category_name']} has been added! ")
                else:
                    continue

    conn.commit()
    conn.close()
# ------------------------------------------------------------------------------------------
def pull_all_data(db):

    json_file_path = "pulled_db_data.json"

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT menu_item_id FROM menu_items")

    menu_item_ids = [i[0] for i in cursor.fetchall()]

    #print(menu_item_ids)

    
    menu_items =[]

    for id in menu_item_ids:
        cursor.execute("SELECT item_name, category FROM menu_items WHERE menu_item_id =?",(id,))
    
        menu_item_rows= cursor.fetchall()


        for row in menu_item_rows:
            item_name= row["item_name"]
            item_name_category = row["category"]

            #Query DB for mapped prep procedures
            cursor.execute("""SELECT prep
                        FROM prep_list
                        JOIN menu_prep_list ON prep_list.prep_id = menu_prep_list.prep_id
                        WHERE menu_prep_list.menu_item_id = ?;""",(id,))
            prep_list = [i[0] for i in cursor.fetchall()]

            # Query DB for mapped mise checklist
            cursor.execute("""SELECT mise_en_place
                        FROM mise_checklist
                        JOIN menu_mise_checklist ON menu_mise_checklist.checklist_id = mise_checklist.checklist_id
                        WHERE menu_mise_checklist.menu_item_id = ?;""",(id,))
            checklist =[i[0] for i in cursor.fetchall()]

            # Query DB for mapped requisitioned prep
            cursor.execute("""SELECT prep, am_prep_team, sous_prep, category
                        FROM req_prep
                        JOIN menu_req_prep_list ON req_prep.req_prep_id = menu_req_prep_list.req_prep_id
                        WHERE menu_req_prep_list.menu_item_id = ?;""", (id,))
            req_prep_result = cursor.fetchall()

            req_prep =[{"prep":row["prep"], "am_prep_team":row["am_prep_team"], "sous_prep":row["sous_prep"], "category":row["category"]} for row in req_prep_result]

            # Query DB for mapped ingredients

            cursor.execute("""SELECT ingredients.ingredient_name, ingredients.purveyor, ingredients.ingredient_code
                FROM ingredients
                JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
                WHERE menu_ingredients.menu_item_id = ?;""", (id,))
            ingredient_result = cursor.fetchall()

            ingredients = [{"purveyor": i[1], "ingredient": i[0], "sku":i[2]} for i in ingredient_result]
            #print(ingredients)

            # Query DB for mapped station_name

            cursor.execute("""SELECT station_name  FROM menu_items_stations
                           WHERE menu_item_id =?""",(id,))
            station =[i[0] for i in cursor.fetchall()]
            #print(station)
            # Query DB for mapped category_name

            cursor.execute("""SELECT category_name FROM menu_items_categories
                           WHERE menu_item_id =?""",(id,))
            category =[i[0]for i in cursor.fetchall()]
            #print(category)

            # Query DB for mapped menu_items_purchasing
            cursor.execute("""SELECT purchasing.ingredient_name,  purchasing.purveyor, purchasing.item_code
                FROM menu_items_purchasing
                JOIN purchasing ON purchasing.ingredient_id = menu_items_purchasing.ingredient_id
                WHERE menu_items_purchasing.menu_item_id = ?;""", (id,))
            
            purchasing =[{"ingredient":i[0], "purveyor":i[1],"sku":i[2]} for i in cursor.fetchall()]

            #print(purchasing)
            
            #break
            menu_items.append({
                                    "item_name": item_name,
                                    "category": item_name_category,
                                    "prep": prep_list,
                                    "req_prep": req_prep,  
                                    "mise_en_place": checklist,
                                    "ingredients": ingredients,
                                    "menu_items_stations": station,
                                    "menu_items_category": category,
                                    "purchasing": purchasing
                               })

    conn.close()

        #print(prep_list)
        #print(checklist)
        #print(req_prep)
    #print(menu_items)
    data ={"menu_items": menu_items}

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


    print("✅ pulled_db_data.json updated!")

    pass
# ------------------------------------------------------------------------------------------
def ingredient_helper(item_id, ingredient_list):