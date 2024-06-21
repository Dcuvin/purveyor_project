from datetime import date
import pandas as pd
import sqlite3
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation
import sys #import sys modulet o access command-line arguments
import os #This statement is used to include the functionality of
#the os module, allowing you to interact with the operating system in a portable way
#----------------------------------------------------------------------------

def chai_prep_list(item_id, event_name):
    
    current_date = date.today()
    event_name = event_name
    conn = sqlite3.connect('purveyor_project_db.db')
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    mise_list = []
    unique_item_names = []
    final_mise_list= []
    for id in item_id:
        cursor.execute(f"""
                       SELECT menu_mise_checklist.item_name, mise_checklist.mise_en_place
                       FROM mise_checklist
                       JOIN menu_mise_checklist ON mise_checklist.checklist_id = menu_mise_checklist.checklist_id
                       WHERE menu_mise_checklist.menu_item_id = {id};
                       """)  
    

        
        #.fetchall() is a list of tuples
        mise = cursor.fetchall()
        # access the tuple inside the list
    for tuple_item in mise:
        
        mise_list.append({'item_name':tuple_item[0], 'mise':tuple_item[1]})

        if tuple_item[0] not in unique_item_names :
            unique_item_names.append(tuple_item[0])

    for item_name in unique_item_names:
        final_mise_list.append({'item_name':item_name, 'mise':[]})

    for dict_item_1 in mise_list:
        for dict_item_2 in final_mise_list: 
            if dict_item_1['item_name'] == dict_item_2['item_name']:
                dict_item_2['mise'].append(dict_item_1['mise'])
        
    


    conn.close()
    print(final_mise_list)
    #print(mise_list)

    #  Create DataFrame from mise_list, which is a list of dictionaries

    df = pd.DataFrame(mise_list)
    #print(df)

    excel_file_count = 0
    # Create an excel file
    excel_file = f"prep_and_checklists/{event_name}_{current_date}_{excel_file_count}.xlsx"
    # Continously checks until it finds a non-existent file name
    while os.path.exists(excel_file):
        excel_file_count += 1
        # This updates the file_count, allowing for it to be checked again in the while loop
        excel_file = f"prep_and_checklists/{event_name}_{current_date}_{excel_file_count}.xlsx"

    #print(excel_file)
    # Function to format the headers and add borders
    def format_headers_and_borders(sheet, start_row, start_col, end_col):
        thin_border = Border(left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin'))
        
        # Format headers
        for cell in sheet.iter_cols(min_row=start_row, max_row=start_row, min_col=start_col, max_col=end_col):
            for c in cell:
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = PatternFill(start_color="0000FF", end_color="0000FF", fill_type="solid")
                c.border = thin_border

        # Apply borders to the entire table
        for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=start_col, max_col=end_col):
            for cell in row:
                cell.border = thin_border

    # Function to set print options
    def set_print_options(sheet):
        sheet.print_options.gridLines = False
        sheet.page_setup.orientation = 'portrait'

    # Function to add DataFrame to sheet at a specific location
    def add_df_to_sheet(sheet, df, start_row, start_col):
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start_row):
            for c_idx, value in enumerate(row, start_col):
                sheet.cell(row=r_idx, column=c_idx, value=value)
        
        end_col = start_col + len(df.columns) - 1
        format_headers_and_borders(sheet, start_row, start_col, end_col)


    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'{event_name}', index=False)
    
    # Load the workbook and access the sheet
    workbook = load_workbook(excel_file)
    sheet = workbook[f'{event_name}']

    #Get unique values in the 'item_name' column
    unique_values = df['item_name'].unique()

    # Start row for the first table
    start_row = 1

    # Add separate tables for each unique value
    for value in unique_values:
        subset_df = df[df['item_name'] == value]
        add_df_to_sheet(sheet, subset_df, start_row, 1)
        start_row += len(subset_df) + 2  # Add some space between tables
    
    # Set print options
    set_print_options(sheet)

    # Save the workbook with formatting
    #workbook.save(excel_file)
#---------------------------------------------------------------------------------

def prep_and_checklist(item_id, event_name):
    
    event_name = event_name
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
                                            <label for="fname">Qty:</label>
                                            <input type="text" id="qty" name="qty">
                                            <label for="lname">Unit:</label>
                                            <input type="text" id="unit" name="unit">
                                        </form>
                                    </td>
                                    <td><li>{procedure_col_2[i].capitalize()}</li></td>
                                    <td>
                                        <form action="/action_page.php">
                                            <label for="qty">Qty:</label>
                                            <input type="text" id="qty" name="qty">
                                            <label for="unit">Unit:</label>
                                            <input type="text" id="unit" name="unit">
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
                                                <label for="qty">Qty:</label>
                                                <input type="text" id="qty" name="qty">
                                                <label for="unit">Unit:</label>
                                                <input type="text" id="unit" name="unit">
                                            </form>
                                        </td>
        
                                    </tr>"""
            else:
                procedure_html += f"""<tr>
                                    <td><li>{procedure_col_2[i].capitalize()}</li></td>
                                    <td>
                                        <form action="/action_page.php">
                                            <label for="qty">Qty:</label>
                                            <input type="text" id="qty" name="qty">
                                            <label for="unit">Unit:</label>
                                            <input type="text" id="unit" name="unit">
                                        </form>
                                    </td>
     
                                </tr>"""
    
   
    mise_en_place_list_of_lists= []
    for i in item_id:
        cursor.execute(f"""
                       SELECT mise_checklist.mise_en_place
                       FROM mise_checklist
                       JOIN menu_mise_checklist ON mise_checklist.checklist_id = menu_mise_checklist.checklist_id
                       WHERE menu_mise_checklist.menu_item_id = {i};
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
    <body id="email_template"> 
    <h3>Prep: {current_date}</h3>
    <br>
        <form>
            <table>
            <tr>
                <td>Item</td>
                <td>Quantity</td>
                <td>Item</td>
                <td>Quantity</td>
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

    #with open(prep_list_file_path, "w") as file:
        #file.write(procedure_and_checklist_html_template)

    conn.close()

    print("HTML prep_and_checklist file successfuly created!")
    

#------------------------------------------------------------------------------------------



def prep_and_checklist(item_id):
    
    conn = sqlite3.connect('purveyor_project_db.db')
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()

    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    
    #procedure_list = []
    procedure_list_dict =[]
    for i in item_id:
        cursor.execute(f""" 
                        SELECT menu_items.item_name, procedures.item_procedure
                        FROM procedures
                        JOIN menu_procedures ON procedures.proc_id = menu_procedures.proc_id
                        JOIN menu_items ON menu_items.menu_item_id = menu_procedures.menu_item_id
                        WHERE menu_procedures.menu_item_id = {i};
        
                        """)   
        
        #.fetchall() is a list of tuples
        procedures = cursor.fetchall()

        # access the tuple inside the list
        #for tuple_item in procedures:
        #    for item in tuple_item:
        #        procedure_list.append(item.split(','))

    # Create a list of dict of item_name:procedure

    for tuple_item in procedures:
       dict_item = {'name': tuple_item[0], 'proc': tuple_item[1]}
       procedure_list_dict.append(dict_item)
    print(procedure_list_dict)

    # Create a procedure_bullet_points variable to hold updated html strings            
    procedure_row_count = 0
    procedure_html = ""
    unpacked_procedure_list = []
    procedure_col_1 = []
    procedure_col_2 = []
    longest_proc_list_length = 0

    print(procedure_list_dict)
    #for procedures in procedure_list:
    #    for procedure in procedures:
    #        unpacked_procedure_list.append(procedure)

    #len_unpacked_procedure_list = len(unpacked_procedure_list)
    #for i in range(len_unpacked_procedure_list):
    #        if i % 2 != 0:
    #            procedure_col_1.append(unpacked_procedure_list[i])
    #        else:
    #            procedure_col_2.append(unpacked_procedure_list[i])

    proc_length = len(procedure_list_dict)
    for i in range(proc_length):
        if i % 2 != 0:
            procedure_col_1.append(procedure_list_dict[i])
        else:
            procedure_col_2.append(procedure_list_dict[i])

    
    if len(procedure_col_1) > len(procedure_col_2):
            longest_proc_list_length = len(procedure_col_1)
    else:
            longest_proc_list_length = len(procedure_col_2)
    for i in range(longest_proc_list_length):
        try:
            procedure_html += f""" <form>
                    <table>
                        <tr>
                            <th>{procedure_col_1[i].name}</th>
                        </tr>
                        <tr>
                            <td>Item</td>
                            <td>Need</td>
                        </tr>
                        <tr>
                            <td>{procedure_col_1[i].proc}</td>
                            <td>
                                <form action="/action_page.php">
                                    <label for="need"></label>
                                    <input type="text" id="need" name="need">
                                </form>
                            </td>
                        </tr>
                    </table>
                </form>
                <form>
                    <table>
                        <tr>
                            <th>{procedure_col_2[i].name}</th>
                        </tr>
                        <tr>
                            <td>Item</td>
                            <td>Need</td>
                        </tr>
                        <tr>
                            <td>{procedure_col_2[i].proc}</td>
                            <td>
                                <form action="/action_page.php">
                                    <label for="need"></label>
                                    <input type="text" id="need" name="need">
                                </form>
                            </td>
                        </tr>
                    </table>
                </form>
                                
             """
        except IndexError:
        # Handle cases where procedure does not have at least two elements
            if len(procedure_col_1) > len(procedure_col_2):   
                procedure_html += f"""<tr>
                                        <td><li>{procedure_col_1[i].capitalize()}</li></td>
                                        <td>
                                            <form action="/action_page.php">
                                                <label for="qty">Qty:</label>
                                                <input type="text" id="qty" name="qty">
                                                <label for="unit">Unit:</label>
                                                <input type="text" id="unit" name="unit">
                                            </form>
                                        </td>
        
                                    </tr>"""
            else:
                procedure_html += f"""<tr>
                                    <td><li>{procedure_col_2[i].capitalize()}</li></td>
                                    <td>
                                        <form action="/action_page.php">
                                            <label for="qty">Qty:</label>
                                            <input type="text" id="qty" name="qty">
                                            <label for="unit">Unit:</label>
                                            <input type="text" id="unit" name="unit">
                                        </form>
                                    </td>
     
                                </tr>"""
    
   
    mise_en_place_list_of_lists= []
    for i in item_id:
        cursor.execute(f"""
                       SELECT mise_checklist.mise_en_place
                       FROM mise_checklist
                       JOIN menu_mise_checklist ON mise_checklist.checklist_id = menu_mise_checklist.checklist_id
                       WHERE menu_mise_checklist.menu_item_id = {i};
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
    <body id="prep_list"> 
    <h3>Prep: {current_date}</h3>
        <div class="table-container">

            <br>
                
            <br><br>
            <h3>Mise en Place Checklist</h3>
            <br>
                <form>
                    
                {mise_en_place_html}          
                    
                </form>
        </div>      
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
    #while os.path.exists(prep_list_file_path):
    #    file_count += 1
        # this updates the file_count, allowing for it to be checked again in the while loop
    #    prep_list_file_path = f'prep_and_checklists/Prep List {file_count} {current_date}.html'

    
    #doc.save(prep_list_file_path)
    #print("Prep list created!")
        
    # Save the HTML to a file
    #with open(prep_list_file_path, "w") as file:
    #    file.write(procedure_and_checklist_html_template)

    conn.close()

    print("HTML prep_and_checklist file successfuly created!")
#--------------------------------------------------------------------------------------   
# Check if the script is run as the main module
if __name__ == "__new_prep_and_cheklist__":
    # Print a message before calling main to indicate the script status
    print("Calling __new_prep_and_cheklist__")
    # Call the main function if this script is executed directly
    prep_and_checklist()
    
#If you run a script directly from the command line (or an IDE, etc.), 
#Python sets __name__ to "__main__". This indicates that the script is 
#the main program being executed. 