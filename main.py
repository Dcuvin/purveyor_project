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
from prep_and_check_list import excel_prep_list
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

    if function_name == 'upload_excel':  # Check if the function name is ' upload_purveyor_contact'
        upload_excel(function_arg_1)  # Call the  upload_purveyor_contact function
        
    elif function_name == 'generate_email_html':
        generate_email_html(function_arg_1)
    
    elif function_name == 'prep_and_checklist':
        #function_arg_1 must look like this: ' 1 2 3 '
        #convert string into an iterable list to pass into new_prep_list
        arg_list = function_arg_1.split()
        prep_and_checklist(arg_list)
    elif function_name == 'excel_prep_list':
    #function_arg_1 must look like this: ' 1 2 3 '
    #convert string into an iterable list to pass into new_prep_list
        arg_list = function_arg_1.split()
        excel_prep_list(arg_list, function_arg_2)
    elif function_name == 'order_sheet':
        arg_list = function_arg_1.split()
        order_sheet(arg_list)
    else:
        print("Invalid function name")  # Print an error message if the function name is unrecognized
    #Function that appends to purveyor_contact.db

#------------------------------------------------------------------------------------------
    

 
   
    
def prep_and_checklist(item_id):
    
    conn = sqlite3.connect('purveyor_project_db.db')
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    procedure_list = []
    for i in item_id:
        cursor.execute(f""" 
                        SELECT procedures.item_procedure
                        FROM procedures
                        JOIN menu_procedures ON procedures.proc_id = menu_procedures.proc_id
                        WHERE menu_procedures.menu_item_id = {i};
            
                        """)   
    

        
        #.fetchall() is a list of tuples
        procedures = cursor.fetchall()
        # access the tuple inside the list
        for tuple_item in procedures:
            for item in tuple_item:
                procedure_list.append(item.split(','))

    # Create a procedure_bullet_points variable to hold updated html strings            
    procedure_row_count = 0
    procedure_html = ""
    unpacked_procedure_list = []
    procedure_col_1 = []
    procedure_col_2 = []
    longest_proc_list_length = 0

    for procedures in procedure_list:
        for procedure in procedures:
            unpacked_procedure_list.append(procedure)

    len_unpacked_procedure_list = len(unpacked_procedure_list)

    for i in range(len_unpacked_procedure_list):
            if i % 2 != 0:
                procedure_col_1.append(unpacked_procedure_list[i])
            else:
                procedure_col_2.append(unpacked_procedure_list[i])

    
    if len(procedure_col_1) > len(procedure_col_2):
            longest_proc_list_length = len(procedure_col_1)
    else:
            longest_proc_list_length = len(procedure_col_2)
    for i in range(longest_proc_list_length):
        try:
            procedure_html += f"""<tr>
                                    <td><li>{procedure_col_1[i].capitalize()}</li></td>
                                    <td>
                                            <form action="/action_page.php">
                                                <label for="need"></label>
                                                <input type="text" id="need" name="need">
                                            </form>
                                    </td>
                                    <td><li>{procedure_col_2[i].capitalize()}</li></td>
                                    <td>
                                            <form action="/action_page.php">
                                                <label for="need"></label>
                                                <input type="text" id="need" name="need">
                                            </form>
                                    </td>
                                </tr>"""
        except IndexError:
        # Handle cases where procedure does not have at least two elements
            if len(procedure_col_1) > len(procedure_col_2):   
                procedure_html += f"""<tr>
                                        <td><li>{procedure_col_1[i].capitalize()}</li></td>
                                        <td>
                                            <form action="/action_page.php">
                                                <label for="need"></label>
                                                <input type="text" id="need" name="need">
                                            </form>
                                        </td>
        
                                    </tr>"""
            else:
                procedure_html += f"""<tr>
                                    <td><li>{procedure_col_2[i].capitalize()}</li></td>
                                    <td>
                                            <form action="/action_page.php">
                                                <label for="need"></label>
                                                <input type="text" id="need" name="need">
                                            </form>
                                    </td>
     
                                </tr>"""
    
   
    mise_en_place_list_of_lists= []
    for id in item_id:
        cursor.execute(f"""
                       SELECT mise_checklist.mise_en_place
                       FROM mise_checklist
                       JOIN menu_mise_checklist ON mise_checklist.checklist_id = menu_mise_checklist.checklist_id
                       WHERE menu_mise_checklist.menu_item_id = {id};
                       """)
        #.fetchall() is a list of tuples
        mise_en_place = cursor.fetchall()
        # access the tuples inside the list
        for mise_tuple in mise_en_place:
            for item in mise_tuple:
                mise_en_place_list_of_lists.append(item.split(','))
        
    # Create a checkboxes variable to hold updated html strings
    mise_row_count = 0
    mise_en_place_col_1= []
    mise_en_place_col_2 = []
    mise_en_place = []
    mise_en_place_html = ""
    for mise_list in mise_en_place_list_of_lists:
        for mise in mise_list:
            mise_en_place.append(mise)
            #mise_row_count += 1
            #if mise_row_count % 2 == 0:
            #    mise_en_place_col_2.append(mise)
            #else:
            #    mise_en_place_col_1.append(mise)
    #col_1_html = ""
    #col_2_html= ""
    #for mise in mise_en_place_col_1:
    #    col_1_html += f""" <li><input type="checkbox" id="{mise.lower()}" name="{mise.lower()}" value= "{mise.lower()}">
    #   <label for="{mise.lower()}">{mise.capitalize()}</label></li>"""
       
    #for mise in mise_en_place_col_2:
    #    col_2_html += f"""<li><input type="checkbox" id="{mise.lower()}" name="{mise.lower()}" value= "{mise.lower()}">
    #    <label for="{mise.lower()}">{mise.capitalize()}</label></li>"""

    for mise in mise_en_place:
         mise_en_place_html += f"""<li><input type="checkbox" id="{mise.lower()}" name="{mise.lower()}" value= "{mise.lower()}">
        <label for="{mise.lower()}">{mise.capitalize()}</label></li>"""
       
    procedure_and_checklist_html_template = f"""
        
    <!DOCTYPE html>

    <html lang="en">
    <head>
        <meta charset="utf-8"/>
        <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
        <title>Prep list and Checklist</title>
            <link rel="stylesheet" href="../styles.css">

    </head>
    <body id="prep_and_checklist"> 
    <h1>Prep and Checklist</h1>
    <h3>Prep: {current_date}</h3>
    <br>
        <form>
            <table>
            <tr>
                <td>Item</td>
                <td>Need</td>
                <td>Item</td>
                <td>Need</td>
            </tr>
                {procedure_html}
            </table> 
        </form>      
    <br><br>
    <h3>Mise en Place Checklist</h3>
    <br>
        <form>
            
          {mise_en_place_html}          
             
        </form>      
    </body>
    </html>
           
    """
                
    # Create a new Word document
    #file_count = 0
    #doc = Document()
    #doc.add_heading('Prep List', level=1)
    
    # Create datetime variable
    #current_date = date.today()
    
    #for items in procedure_list:
    #    for item in items:
    #        doc.add_paragraph(
    #        item.capitalize(), style='List Bullet'
    #        )
    
    
    # Check for any duplicate html files
    file_count = 0

    prep_list_file_path = f'prep_and_checklists/Prep List {file_count} {current_date}.html'
    
    #continously checks until it finds a non-existent file name
    while os.path.exists(prep_list_file_path):
        file_count += 1
        # this updates the file_count, allowing for it to be checked again in the while loop
        prep_list_file_path = f'prep_and_checklists/Prep List {file_count} {current_date}.html'

    
    #doc.save(prep_list_file_path)
    #print("Prep list created!")
       
    # Save the HTML to a file

    with open(prep_list_file_path, "w") as file:
        file.write(procedure_and_checklist_html_template)

    conn.close()

    print("HTML prep_and_checklist file successfuly created!")
        
#------------------------------------------------------------------------------------------

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