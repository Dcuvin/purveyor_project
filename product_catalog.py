import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import numbers
import sqlite3
import json
from fuzzy import match_menu_items



"""Updates current product catalog with newly downloaded file from XtraChef"""
def update_product_catalog(db_file):

    source_file = "new_product_catalog_2025.xlsx"
    current_file = db_file
    df_source = pd.read_excel(source_file, usecols=[0,1,2,5,11,13])  # Extract 6 columns
    df_current = pd.read_excel(current_file, sheet_name="ingredients" ,usecols=[0,1,2,3,4,5,6,7])

 
    current_data = df_current[["ingredient_id", "purveyor", "ingredient_code", "ingredient_description",
                               "ingredient_name", "pack_size_unit", "purchase_price", "ingredient_type"]]
    source_data = df_source[["Item Description", "Vendor Name", "Item Code",
                               "Pack/Size/Unit", "Last Purchased Price ($)", "Product(s)"]]
    new_data_set =[]
    source_data_set = []

    for _, row in current_data.iterrows():
        new_data_set.append({
            "ingredient_id": row["ingredient_id"],
            "purveyor": row["purveyor"],
            "ingredient_code": row["ingredient_code"],
            "ingredient_description": row["ingredient_description"],
            "ingredient_name": row["ingredient_name"],
            "pack_size_unit": row["pack_size_unit"],
            "purchase_price": row["purchase_price"],
            "ingredient_type": row["ingredient_type"]
        })

    for _, row in source_data.iterrows():
        source_data_set.append({
            "ingredient_id": row["Item Description"],
            "purveyor": row["Vendor Name"],
            "ingredient_code": row["Item Code"],
            "ingredient_description": row["Item Description"],
            "pack_size_unit": row["Pack/Size/Unit"],
            "purchase_price": row["Last Purchased Price ($)"],
            "ingredient_type": row["Product(s)"]
        })

    source_lookup = {
        item["ingredient_code"]: item
        for item in source_data_set
    }

    #  Iterate through new data and update if matched
    for new_dict_item in new_data_set:
        code = new_dict_item["ingredient_code"]
        if code in source_lookup:
            match = source_lookup[code]
            new_dict_item.update({
                "purveyor": match["purveyor"],
                "ingredient_description": match["ingredient_description"],
                "pack_size_unit": match["pack_size_unit"],
                "purchase_price": match["purchase_price"],
                "ingredient_type": match["ingredient_type"]
            })
       
    # for new_dict_item in new_data_set:
    #     if isinstance(new_dict_item.get("purchase_price"), str):
    #         new_dict_item["purchase_price"] = 0.0

    #print(new_data_set)

    wb = load_workbook(current_file)
    ws = wb['ingredients']
    # Write each item into its own row 
    for row_idx, dict_items in enumerate(new_data_set, start=2):   # start=1 → Excel’s first row
        ws.cell(row=row_idx, column=1, value=dict_items["ingredient_id"])
        ws.cell(row=row_idx, column=2, value=str(dict_items["purveyor"]))
        ws.cell(row=row_idx, column=3, value=dict_items["ingredient_code"])
        ws.cell(row=row_idx, column=4, value=dict_items["ingredient_description"])
        ws.cell(row=row_idx, column=5, value=dict_items["ingredient_name"])
        ws.cell(row=row_idx, column=6, value=dict_items["pack_size_unit"])
        ws.cell(row=row_idx, column=7, value=dict_items["purchase_price"])
        ws.cell(row=row_idx, column=8, value=dict_items["ingredient_type"])
    wb.save(current_file)

    print(f"✅ Ingredients Table has been updated!")
    
#----------------------------------------------------------------------------------------
def input_menu_ingredient(db_excel_file, db):

    current_file = db_excel_file
    df_current = pd.read_excel(current_file, sheet_name="ingredients" ,usecols=[0,1,2,3,4,5,6,7])
    
    file_path = "input_product_catalog.json"
    data_to_insert=[]
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()

    cursor.execute("""
                SELECT ingredient_name
                FROM ingredients;
                  """)
    
    results = cursor.fetchall()

    ingredient_names=[result[0] for result in results ]
    #print(ingredient_names)

    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing content
    with open("input_product_catalog.json", 'r') as file:
        #data is a list of dict
        data = json.load(file)
   
    last_id = df_current['ingredient_id'].iloc[-1]
    new_id = last_id + 1
    new_menu_item = []

    for dict_item in data:
        data_to_insert.append({
                 "ingredient_id": new_id, 
                 "purveyor":dict_item["purveyor"], 
                 "ingredient_code": dict_item["ingredient_code"], 
                 "ingredient_description": dict_item["ingredient_description"],
                 "ingredient_name": dict_item["ingredient_name"], 
                 "pack_size_unit":dict_item["pack_size_unit"], 
                 "purchase_price": dict_item["purchase_price"], 
                 "ingredient_type": dict_item["ingredient_type"]})

        new_menu_item.append(dict_item["ingredient_name"])
 
    for menu_item_name in new_menu_item:
        if match_menu_items(menu_item_name, ingredient_names) is not None:
            print(f"❌ {menu_item_name} Already Exists!" )


        else:
            wb = load_workbook(current_file)
            ws = wb['ingredients']
            # +1 to last row, since pandas starts indexing at 0; + 1 more to access the empty row after it.
            last_empty_row = len(df_current) + 2
            print(last_empty_row)
            # Write each item into its own row 
            for row_idx, dict_items in enumerate(data_to_insert, start= last_empty_row):   # start=1 → Excel’s first row
                ws.cell(row=row_idx, column=1, value=dict_items["ingredient_id"])
                ws.cell(row=row_idx, column=2, value=dict_items["purveyor"])
                ws.cell(row=row_idx, column=3, value=dict_items["ingredient_code"])
                ws.cell(row=row_idx, column=4, value=dict_items["ingredient_description"])
                ws.cell(row=row_idx, column=5, value=dict_items["ingredient_name"])
                ws.cell(row=row_idx, column=6, value=dict_items["pack_size_unit"])
                ws.cell(row=row_idx, column=7, value=dict_items["purchase_price"])
                ws.cell(row=row_idx, column=8, value=dict_items["ingredient_type"])

            wb.save(current_file)

            for dict_item in data_to_insert:
                print(f"""✅ Inserted the following ingredients:
                        \n"ingredient_id": {dict_item["ingredient_id"]}, 
                        \n"purveyor": {dict_item["purveyor"]}, 
                        \n"ingredient_code":  {dict_item["ingredient_code"]}, 
                        \n"ingredient_description":  {dict_item["ingredient_description"]},
                        \n"ingredient_name":  {dict_item["ingredient_name"]}, 
                        \n"pack_size_unit": {dict_item["pack_size_unit"]}, 
                        \n"purchase_price":  {dict_item["purchase_price"]}, 
                        \n"ingredient_type":  {dict_item["ingredient_type"]}  """)
                
#----------------------------------------------------------------------------------------
def get_menu_item_ingredients(db):

    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()

    results= []
    final_results =[]
    cursor.execute("""
                SELECT menu_item_id, item_name 
                FROM menu_items;
                  """)
    
    menu_items = cursor.fetchall()
    for tuple_item in menu_items:
            results.append({"menu_item_id": tuple_item[0], "item_name": tuple_item[1], "ingredient_ids": [],
               "ingredient_name": "", "ingredient_code": "", "purveyor": "", "purchase_price": 0.0})

    for dict_item in results:
        cursor.execute("""
                SELECT ingredient_id
                FROM menu_ingredients
                WHERE menu_item_id = ?;
                """, (dict_item["menu_item_id"],)
            )
        
        
        ingredients = cursor.fetchall()
        for ingredient in ingredients:
            dict_item["ingredient_ids"].append(ingredient[0])
    
    for result in results:
        for id in result["ingredient_ids"]:
               final_results.append({
                "menu_item_id":result["menu_item_id"],
                "item_name":result["item_name"],
                "ingredient_id":id,
                })
               
    for result in final_results:
        cursor.execute("""
        SELECT ingredient_name, ingredient_code, purveyor, purchase_price
        FROM ingredients
        WHERE ingredient_id = ?;
    """, (result["ingredient_id"],))
    
        ingredient_data = cursor.fetchone()
   
        if ingredient_data:
            result["ingredient_name"] = ingredient_data[0]
            result["ingredient_code"] = ingredient_data[1]
            result["purveyor"] = ingredient_data[2]
            result["purchase_price"] = ingredient_data[3]

    # for result in final_results:     
    #     print(f"\n {result}")
    

    excel_file_count = 0
    # Create an excel file
    excel_file = f"updated_menu_ingredient_list.xlsx"

    # Load the workbook and select the active worksheet
    workbook = load_workbook(excel_file)
    ingredient_sheet= workbook["ingredients"]

    # # Iterate over each row and column in the sheet
    # Write each menu item + ingredient combination to the Excel sheet
    for row, dict_items in enumerate(final_results, start=2):
        ingredient_sheet.cell(row=row, column=1, value=dict_items.get("menu_item_id", ""))
        ingredient_sheet.cell(row=row, column=2, value=dict_items.get("item_name", ""))
        ingredient_sheet.cell(row=row, column=3, value=dict_items.get("ingredient_id", ""))
        ingredient_sheet.cell(row=row, column=4, value=dict_items.get("ingredient_name", ""))
        ingredient_sheet.cell(row=row, column=5, value=dict_items.get("ingredient_code", ""))
        ingredient_sheet.cell(row=row, column=6, value=dict_items.get("purveyor", ""))
        ingredient_sheet.cell(row=row, column=7, value=dict_items.get("purchase_price", 0.0))

    workbook.save(excel_file)
    print("✅ updated_menu_ingredient_list.xlsx has been updated!")
