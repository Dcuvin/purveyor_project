from datetime import date
import pandas as pd
import sqlite3
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
import sys #import sys modulet o access command-line arguments
import os #This statement is used to include the functionality of
#the os module, allowing you to interact with the operating system in a portable way
from bs4 import BeautifulSoup
#from docx import Document
from prep_and_check_list import excel_prep_list, word_prep_and_checklist, prep_and_checklist
from database import upload_excel
#------------------------------------------------------------------------------------------

def main():
    if len(sys.argv) == 0:  # Check if the required arguments are provided
        print("Usage: python functions.py <function> <name>")  # Provide usage instructions
        return  # Exit the function if not enough arguments
    function_name = sys.argv[1]  # Get the function name from the first command line argument
    function_arg_1 = sys.argv[2]  # Get the name from the second command line argument
    function_arg_2 = ""
    function_arg_3 = ""
    try:
        function_arg_2 = sys.argv[3]
    except:
        pass

    try:
        function_arg_3 = sys.argv[4]
    except:
        pass
    try:
        function_arg_4 = sys.argv[5]
    except:
        pass

    try:
        function_arg_5 = sys.argv[6]
    except:
        pass

    if function_name == 'upload_excel':  # Check if the function name is ' upload_purveyor_contact'
        upload_excel(function_arg_1)  # Call the  upload_purveyor_contact function
        
    elif function_name == 'generate_email_html':
        generate_email_html(function_arg_1)
    
    elif function_name == 'prep_and_checklist':
        #function_arg_1 must look like this: ' 1 2 3 '
        #convert string into an iterable list to pass into new_prep_list
        arg_list = function_arg_1.split()
        prep_and_checklist(arg_list)

    elif function_name == 'master_prep_list':
        arg_list = function_arg_1.split()
        master_prep_list(arg_list, function_arg_2, function_arg_3, function_arg_4, function_arg_5)
    elif function_name == 'excel_prep_list':
    #function_arg_1 must look like this: ' 1 2 3 '
    #convert string into an iterable list to pass into new_prep_list
        arg_list = function_arg_1.split()
        excel_prep_list(arg_list, function_arg_2, function_arg_3, function_arg_4, function_arg_5)
    elif function_name == 'word_prep_and_checklist':
        arg_list = function_arg_1.split()
        word_prep_and_checklist(arg_list, function_arg_2, function_arg_3, function_arg_4, function_arg_5)
    elif function_name == 'order_sheet':
        arg_list = function_arg_1.split()
        order_sheet(arg_list)
    else:
        print("Invalid function name")  # Print an error message if the function name is unrecognized
    #Function that appends to purveyor_contact.db

#------------------------------------------------------------------------------------------
       
def master_prep_list(arg_list, function_arg_2, function_arg_3, function_arg_4, function_arg_5):
    
    item_id = arg_list
    event_name = function_arg_2
    guest_count = function_arg_3
    event_start = function_arg_4
    event_date = function_arg_5

    # Specify the path of the new directory
    new_folder_path = f"prep_and_checklists/{event_name}"

    # Create the directory
    try:
        os.makedirs(new_folder_path)
        print(f"Directory '{new_folder_path}' created successfully")
    except FileExistsError:
        print(f"Directory '{new_folder_path}' already exists")
    except FileNotFoundError:
        print(f"Parent directory does not exist")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    excel_prep_list(item_id, event_name, guest_count, event_start, event_date)
#------------------------------------------------------------------------------------------
def order_sheet(item_id):
    
    current_date = date.today
    conn = sqlite3.connect('purveyor_project_db.db')  # Specify your database file here
    cursor = conn.cursor()
    # Query the database
    to_order_list = []
    for id in item_id:

        cursor.execute(f"""SELECT ingredients.ingredient_name, ingredients.brand, ingredients.purveyor, ingredients.item_code
                        FROM ingredients
                        JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
                        WHERE menu_ingredients.menu_item_id = {id}""") 
        to_order = cursor.fetchall()
        to_order_list.append(to_order)
    
    
    
    print(to_order_list)
#------------------------------------------------------------------------------------------
    
def generate_email_html(purveyor_name):
    
    # Connect to the SQLite database
    conn = sqlite3.connect('purveyor_contact.db')  # Specify your database file here
    cursor = conn.cursor()
    
    # Query the database
    cursor.execute("SELECT * FROM vendors WHERE purveyor = ?", (purveyor_name,))  # Modify query as needed
    vendor = cursor.fetchall()
    #print(vendor)
    #iterate over vendor and stringify
    final_email_template = " "
    item_list = []
    for tuple_item in vendor:
        
        for item in tuple_item:
    
            item_list.append(item)
            
    contact_info = f"""
<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Email Template</title>
</head>
<body id="email_template"> 
        Purveyor: {item_list[0]}<br><br>

        Contact: {item_list[2]}<br><br>

        Email: {item_list[3]}<br><br>

        Phone: {item_list[4]}<br><br>

        Ordering Info: {item_list[5]}<br><br>

        Deadline: {item_list[6]}<br><br>

        Min.: {item_list[7]}<br><br><br>
        
        Hi {item_list[2]},<br><br>

        
        Can I please have the following for input_date:<br><br>

        <li>input_item</li>
        <li>input_item</li>
        <li>input_item</li><br>
            
        Thanks!<br><br>

        
        David Cuvin<br>
    ---------------------------------------------------------------------------------------------------      
        

</body>
</html>

        """
                  
    #Check filepath
    file_path = "email_template/email.html"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing HTML content
    with open("email_template/email.html", 'r', encoding='utf-8') as file:
    # Create a BeautifulSoup object
        soup = BeautifulSoup(file, 'html.parser')
   
   
    # Save the changes back to the file
    with open("email_template/email.html", 'w', encoding='utf-8') as updated_file:
        # Update blank html file with newly generated html code
        updated_file.write(final_email_template)
   
    conn.close()
    
#------------------------------------------------------------------------------------------

    
# Check if the script is run as the main module
if __name__ == "__main__":
    # Print a message before calling main to indicate the script status
    print("__name__ is __main__, about to call main()")
    # Call the main function if this script is executed directly
    main()
    
#If you run a script directly from the command line (or an IDE, etc.), 
#Python sets __name__ to "__main__". This indicates that the script is 
#the main program being executed. 