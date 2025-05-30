import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
import time
import os



def check_excel(name_of_excel_file):
# loop through the joint tables in the database to look for duplicates prior to uploading.

    # joint tables list

    joint_tables = ['menu_req_prep', 'menu_prep_list', 'menu_mise_checklist', 'menu_procedures', 'menu_ingredients']

    pass
    
# ------------------------------------------------------------------------------------------

def upload_excel(name_of_excel_file, db):
    
    table_name = [ 'menu_items', 'menu_restrictions', 'restrictions', 'ingredients', 'menu_ingredients', 'menu_procedures', 'procedures', 'vendors', 'master_product_catalog', 'menu_prep_list','prep_list', 'req_prep', 'menu_req_prep_list']
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
    table_names = []
    
    for name in table_name:
        
        try:
            cursor.execute(f'SELECT * FROM {name}')
            table_names.append('y')

        except sqlite3.OperationalError:

            continue
    print(table_names)

    if len(table_names) == 13:
    
        for sheet_name, df in excel_data.items():
            print(f"Uploading sheet: {sheet_name}")
            # Drop the table if it exists before replacing it with new data
            # this helped solve the locked table that kept occuring
            #cursor.execute(f'DROP TABLE IF EXISTS {sheet_name}')
            # Clear all data from the table while keeping its schema intact.
            cursor.execute(f'DELETE FROM {sheet_name}')
            # Append the new data to the existing (now empty) table.
            df.to_sql(sheet_name, conn, if_exists='append', index=False)
            #df.to_sql(sheet_name, conn, if_exists='replace', index=False)    
    else: 
        print("Error with uploading excel file!")
    
        conn.close()
        
    # Commit the transaction
    conn.commit()
        
    # Close the connection
    conn.close()
    print("Excel file upload successful!")

# ------------------------------------------------------------------------------------------

def input_new_data():

    #Check filepath
    file_path = "db_input_file.txt"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing content
    read_file = ""
    with open("db_input_file.txt", 'r') as file:
        content = file.read()
        read_file += content
        #print(content)
    #print(read_file)



# ------------------------------------------------------------------------------------------
# Create a function that automatically updates the a separate database that matches the standard menu item name to alternative names

