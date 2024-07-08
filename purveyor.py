
import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
from datetime import date


def order_sheet(item_id):
    
    current_date = date.today
    conn = sqlite3.connect('purveyor_project_db.db')  # Specify your database file here
    cursor = conn.cursor()
    # Query the database
    to_order_list = []
    for id in item_id:

        cursor.execute(f"""
                        SELECT ingredients.ingredient_name, ingredients.brand, ingredients.purveyor, ingredients.item_code
                        FROM ingredients
                        JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
                        WHERE menu_ingredients.menu_item_id = {id}""") 
        to_order = cursor.fetchall()
        to_order_list.append(to_order)
    
    
    
    print(to_order_list)