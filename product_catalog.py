import pandas as pd
import os
from openpyxl import load_workbook, Workbook
from openpyxl.styles import numbers, Font, PatternFill, Border, Side, Alignment
import sqlite3
import json
from fuzzy import match_menu_items
from datetime import date
from excel_format import format_table
from database import create_df
from openpyxl.utils import get_column_letter
from excel_format import format_table_ver_2



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

#----------------------------------------------------------------------------------------

def menu_cost(db):
    current_date = date.today()
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    menu_item_cost = []
    cursor.execute(
        """ SELECT *
            FROM menu_items;
        """)
    item_id_tuple = cursor.fetchall()
    for id in item_id_tuple:
       menu_item_cost.append({"item_id":id[0], "item_name":id[1], "ingredients":[]})

    #print(menu_item_cost)

    for item in menu_item_cost:
        cursor.execute(f"""
                       SELECT ingredients.ingredient_id,  ingredients.ingredient_name, ingredients.purveyor, ingredients.ingredient_code, ingredients.pack_size_unit, 
                       CAST (ingredients.purchase_price AS FLOAT)
                       FROM ingredients
                       JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
                       WHERE menu_ingredients.menu_item_id = {item["item_id"]};
                       """)  
        ingredient_tuple = cursor.fetchall()
        #print(ingredient_tuple)
        for ing_tuple in ingredient_tuple:
            try:
                item["ingredients"].append({"ingredient_id":ing_tuple[0],
                                        "ingredient_name":ing_tuple[1],
                                        "purveyor": ing_tuple[2],
                                        "ingredient_code": ing_tuple[3],
                                        "pack_size_unit": ing_tuple[4],
                                        "price": ing_tuple[5]})
            
            except:
                continue
    conn.close()

    for item in menu_item_cost:
        item["ingredients"] = create_df(item["ingredients"])
        
    print(menu_item_cost)

 
    # Create an excel file
    excel_file_count = 0
    excel_file = f"Events_Menu_Cost_{excel_file_count}_{current_date}.xlsx"

   
    
    # Continously checks until it finds a non-existent file name
    while os.path.exists(excel_file):
        excel_file_count += 1
        # This updates the file_count, allowing for it to be checked again in the while loop
        excel_file = f"Events_Menu_Cost_{excel_file_count}_{current_date}.xlsx"
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "menu_cost"
        wb.save(excel_file)
        print(f"✅ {excel_file} Created!")

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        item_name_row = 3
        item_id_row = 4
        df_row = 4
        current_col = 0  # 0-based for pandas
        column_A = 1 #1-based for openpyxl (col A)
        column_F = 6 #6-based for openpyxl (col F)
        column_E = 5
        pd.DataFrame().to_excel(writer, sheet_name='menu_cost', index=False)
        for item_dict in menu_item_cost:

            current_col_letter = get_column_letter(column_A)
            end_col_letter = get_column_letter(column_F)

            ws = writer.sheets['menu_cost']

            # prepares cells for item_name
            cell_item_name = ws[f"{current_col_letter}{item_name_row}"]
            cell_item_name.value = item_dict['item_name'].capitalize()
            cell_item_name.border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
            cell_item_name.alignment = Alignment(horizontal='center', vertical='center')
            cell_item_name.fill = PatternFill(start_color="FFC9DAF8", end_color="FFC9DAF8", fill_type="solid")
            cell_item_name.font = Font(name='Calibri', size=14,bold=True, color="FF000000")
            ws.merge_cells(f"{current_col_letter}{item_name_row}:{end_col_letter}{item_name_row}")

            # prepares cells for item_id
            cell_item_id =  ws[f"{current_col_letter}{item_id_row}"]
            cell_item_id.value = f'Item_ID: {item_dict["item_id"]}'
            cell_item_id.border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
            cell_item_id.alignment = Alignment(horizontal='center', vertical='center')
            cell_item_id.fill = PatternFill(start_color="FFC9DAF8", end_color="FFC9DAF8", fill_type="solid")
            cell_item_id.font = Font(name='Calibri', size=14,bold=True, color="FF000000")
            ws.merge_cells(f"{current_col_letter}{item_id_row}:{end_col_letter}{item_id_row}")


            # populates cells with ingredients
            item_dict['ingredients'].to_excel(writer, sheet_name= 'menu_cost', startrow=df_row, startcol=current_col, index=False)

            format_table_ver_2(ws, df_row, column_A, item_dict['ingredients'])

            df_length = len(item_dict['ingredients'])
            first_price_cell =f"{end_col_letter}{df_row + 2}"
            last_price_cell = f"{end_col_letter}{df_row + df_length + 1}"

            
            sum_row = df_row + len(item_dict['ingredients'])  + 2
            # print(f"df_length: {df_length}")
            #print(f"Sum Row: {sum_row}")
            # sum_cell = ws[f"{end_col_letter}{sum_row}"]
            total_sum_cost = ws.cell(row=sum_row, column=column_F)
            total_sum_cost.value = f"=SUM({first_price_cell}:{last_price_cell})"
            total_sum_cost.border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
            total_sum_cost.alignment = Alignment(horizontal='center', vertical='center')
            total_sum_cost.font = Font(bold=True, name='Calibri', size=12, color="000000")


            total_cost_string = ws.cell(row=sum_row, column=column_E)
            total_cost_string.value = "TOTAL COST"
            total_cost_string.border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
            total_cost_string.alignment = Alignment(horizontal='center', vertical='center')
            total_cost_string.font = Font(bold=True, name='Calibri', size=12, color="000000")

            #format_table(ws, df_row, current_category_col, item_dict['ingredients'])
            #this is openpyxl based and starts at 1 for indexing
            df_row += len(item_dict["ingredients"]) + 5 # Add space between tables
            item_id_row += len(item_dict["ingredients"]) + 5
            item_name_row += len(item_dict["ingredients"]) + 5
            #insert_blank_rows(ws, df_row + 1 )
          
#----------------------------------------------------------------------------------------

def menu_cost_ver_2(db):
    pass