import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3


def upload_excel(name_of_excel_file):
    
    table_name = [ 'menu_items', 'menu_restrictions', 'restrictions', 'ingredients', 'menu_ingredients', 'menu_procedures', 'procedures', 'vendors']
    # Connect to the SQLite database
    conn = sqlite3.connect('purveyor_project_db.db')
    cursor = conn.cursor()
    # Load the Excel file
    # To read all sheets, use sheet_name=None
    #.read_excel creates a dictionaryseke
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
    
    if len(table_names) == 8:
    
        for sheet_name, df in excel_data.items():
            print(f"Uploading sheet: {sheet_name}")
            df.to_sql(sheet_name, conn, if_exists='replace', index=False)    
    else: 
        print("Error with uploading excel file!")
    
        conn.close()
        
    # Commit the transaction
    conn.commit()
        
    # Close the connection
    conn.close()
    print("Excel file upload successful!")