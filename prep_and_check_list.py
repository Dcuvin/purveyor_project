from datetime import date
import pandas as pd
import sqlite3
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation
import sys #import sys modulet o access command-line arguments
import os #This statement is used to include the functionality of
#the os module, allowing you to interact with the operating system in a portable way
from docx import Document
#import openai

#----------------------------------------------------------------------------
def excel_prep_list(item_id, event_name, guest_count, event_start, event_date,db):
    
    current_date = date.today()
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    mise_list = []
    unique_item_names = []
    mise_list_final= []
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
            
            mise_list.append({'Item':str(tuple_item[0]), 'Mise':tuple_item[1], 'Need':'  '})
            # Create a list of items
            if tuple_item[0] not in unique_item_names:
                unique_item_names.append(tuple_item[0])
    conn.close()

    
    # Create a dict of items with a list of mise
    for name in unique_item_names: 
        mise_list_final.append({'Item': name, 'Mise':[], 'Need':' '})

    # Iteratively add the mise form mise_list to mise_list_2
    for item_1 in mise_list:
        for item_2 in mise_list_final:
            if item_1['Item'] == item_2['Item']:
                item_2['Mise'].append(item_1['Mise'].capitalize())

    # Iteratively title() each item name

    for item in mise_list_final:
        item['Item'] = item['Item'].title()

    print(mise_list_final)

    # Function that creates a dataframe
    def create_df(data):

        df= pd.DataFrame(data)
        return df

    df_list =[] 
    for dict_item in mise_list_final:
        df_list.append(create_df(dict_item))

    pivot_list = []
    def create_pivot(data):    
        #pivot = pd.pivot(data, columns='Item', index ='Mise', values= 'Need')
        pivot = data.pivot(index='Mise', columns='Item', values='Need')

        return pivot
    for data_frame in df_list:
        pivot_list.append(create_pivot(data_frame))

    #print(pivot_list)

    excel_file_count = 0
    # Create an excel file
    excel_file = f"prep_and_checklists/{event_name}/{event_name}_{current_date}_{excel_file_count}.xlsx"
    # Continously checks until it finds a non-existent file name
    while os.path.exists(excel_file):
        excel_file_count += 1
        # This updates the file_count, allowing for it to be checked again in the while loop
        excel_file = f"prep_and_checklists/{event_name}/{event_name}_{current_date}_{excel_file_count}.xlsx"
    
    #print(excel_file)
    # Function to format the headers and add borders
    def format_headers_and_borders(sheet, start_row, start_col, end_col):
        thin_border = Border(left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin'))
        
        # Define the font for non-header cells
        cell_font = Font(name="Calibri", size=12)

        # Define the alignment for all cells
        cell_alignment = Alignment(horizontal='center', vertical='center')

        
        # Apply font to the entire table
        for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=start_col, max_col=end_col):
             for cell in row:
                cell.font = cell_font
                # Center all data
                cell.alignment = cell_alignment
        # Format headers
        for cell in sheet.iter_cols(min_row=start_row, max_row=start_row, min_col=start_col, max_col=end_col):
            for c in cell:
                c.font = Font(bold=True, name='Calibri', size=14, color="000000")
                c.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
                c.border = thin_border

        # Apply borders to the entire table
        for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=start_col, max_col=end_col):      
            for cell in row:
                cell.border = thin_border
               
                
    # Function to set print options
    def set_print_options(sheet):
        sheet.print_options.gridLines = False
        sheet.page_setup.orientation = 'portrait'
    
    # Function to insert unformatted rows
    def insert_blank_rows(sheet, start_row):
        sheet.insert_rows(start_row, 1)

    

    # Creates an unfinished excel file
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        current_row = 3
        for pivot in pivot_list:
            pivot.to_excel(writer, sheet_name= 'prep_sheet', startrow=current_row, startcol=0)
            current_row += len(pivot) + 2 # Add space between tables

        # Create an empty (blank) order_sheet by writing an empty DataFrame
        pd.DataFrame().to_excel(writer, sheet_name="order_sheet", index=False)


    # Load the workbook and access the sheet
    workbook = load_workbook(excel_file)
    prep_sheet= workbook["prep_sheet"]
    order_sheet= workbook["order_sheet"]

    # Format the tables in the file
    start_row = 4
    start_col = 1
    for df in pivot_list:
        insert_blank_rows(prep_sheet, start_row)
        start_row += 1
        format_headers_and_borders(prep_sheet, start_row, start_col, 2)
        start_row += len(df) + 2

    # Insert Event Info
    title = prep_sheet.cell(row=1, column=1, value=f"{event_name} {guest_count} Guests {event_start} {event_date}")
    title.font = Font(name='Calibri', size=16, bold=True, underline='single', color='000000')
   
    # Set print options
    set_print_options(prep_sheet)
    set_print_options(order_sheet)

    # Save the workbook with formatting
    workbook.save(excel_file)

    # Load the workbook and select the active worksheet
    workbook = load_workbook(excel_file)
    prep_sheet= workbook["prep_sheet"]
    #---------------------------------------------------------------------------------

    # Iterate over each row and column in the sheet
    for row in prep_sheet.iter_rows():
        for cell in row:
            # Check if the cell contains 'Mise'
            if cell.value and isinstance(cell.value, str) and 'Mise' in cell.value:
                right_cell = prep_sheet.cell(row=cell.row, column=cell.column + 1)
                if right_cell.value:
                    # Replace the cell with 'Mise' with the content of the immediate right cell
                    cell.value = right_cell.value
                    # Replace the content of the right cell with 'Need'
                    right_cell.value = 'Need'

    # Save the workbook with formatting
    workbook.save(excel_file)
    return excel_file

    print("Excel Prep List Created and Reformatted!")
#---------------------------------------------------------------------------------
def word_prep_list(item_id, event_name, guest_count, event_start, event_date,db):
    
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    procedure_list = []
    unique_item_list =[]
    final_proc_list =[]
    for i in item_id:
        cursor.execute(f""" 
                        SELECT menu_items.item_name, procedures.item_procedure
                        FROM menu_procedures
                        JOIN menu_items ON menu_procedures.menu_item_id = menu_items.menu_item_id
                        JOIN procedures ON procedures.proc_id = menu_procedures.proc_id
                        WHERE menu_procedures.menu_item_id = {i};
            
                        """)   
    
        #.fetchall() is a list of tuples
        procedures = cursor.fetchall()
        # access the tuple inside the list
        for tuple_item in procedures:
            procedure_list.append({'item':tuple_item[0], 'proc': tuple_item[1]})
            if tuple_item[0] not in unique_item_list:
                unique_item_list.append(tuple_item[0])

    for item in unique_item_list:
        final_proc_list.append({'item':item, 'proc':[]})

    for proc_1 in procedure_list:
        for proc_2 in final_proc_list:
            if proc_1['item'] == proc_2['item']:
                proc_2['proc'].append(proc_1['proc']) 

    #print(final_proc_list)
    
                
    # Create a new Word document
    file_count = 0
    doc = Document()
    doc.add_heading(f'{event_name} {event_date}', 0)
    doc.add_heading(f'Guests: {guest_count}', level=2)
    doc.add_heading(f'Start: {event_start}', level=2)

    # Create datetime variable
    current_date = date.today()
    
    for dictionary in final_proc_list:
        doc.add_heading(f"{dictionary['item']}", level=2)

        for proc in dictionary['proc']:
            doc.add_paragraph(proc.capitalize() +' ' + '\u2610', style='List Bullet')
        
    
    # Check for any duplicate html files
    docx_file_count = 0

    prep_list_file_path = f'prep_and_checklists/{event_name}/{event_name}_Prep List_{current_date}_{docx_file_count}.docx'
    
    #continously checks until it finds a non-existent file name
    while os.path.exists(prep_list_file_path):
        docx_file_count += 1
        # this updates the file_count, allowing for it to be checked again in the while loop
        prep_list_file_path = f'prep_and_checklists/{event_name}/{event_name}_Prep List_{current_date}_{docx_file_count}.docx'

    
    doc.save(prep_list_file_path)
    print("Prep List Created!")
    

    conn.close()
#------------------------------------------------------------------------------------------
def word_checklist(item_id, event_name, guest_count, event_start, event_date,db):
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    #the updated version will take a list of menu_item_ids
    #It will then query a junction table and pull all procedures associated with the id.          
    mise_list = []
    unique_item_list =[]
    final_mise_list =[]
    for i in item_id:
        cursor.execute(f""" 
                        SELECT menu_mise_checklist.item_name, mise_checklist.mise_en_place
                        FROM menu_mise_checklist
                        JOIN mise_checklist ON menu_mise_checklist.checklist_id = mise_checklist.checklist_id
                        WHERE menu_mise_checklist.menu_item_id = {i};
            
                        """)   
    
        #.fetchall() is a list of tuples
        mise_en_place = cursor.fetchall()
        # access the tuple inside the list
        for tuple_item in mise_en_place:
            mise_list.append({'item':tuple_item[0], 'mise': tuple_item[1]})
            if tuple_item[0] not in unique_item_list:
                unique_item_list.append(tuple_item[0])

    for item in unique_item_list:
        final_mise_list.append({'item':item, 'mise':[]})

    for mise_1 in mise_list:
        for mise_2 in final_mise_list:
            if mise_1['item'] == mise_2['item']:
                mise_2['mise'].append(mise_1['mise']) 

    # capitalize the first letter 
    for menu_item in final_mise_list:
        menu_item['item'].title()
        for mise in menu_item['mise']:
            mise.title()

    #print(final_proc_list)
    final_mise_list.append({'item': 'Dry Goods/Tools', 'mise':['Maldon','EVOO','C-folds','Vodka Spray','Quarter Sheet Trays','Half Sheet Trays','Catering Trays', 'Cutting boards', 'Mixing Bowls', 'Sani-wipes','Gloves', 'Tasting Spoons','Piping Bags', 'Quarts','Pints', 'Lids']})
    # Adding dry-goods/ tools section to checklist
           
    # Create a new Word document
    file_count = 0
    doc = Document()
    doc.add_heading(f'{event_name} {event_date}', 0)
    doc.add_heading(f'Guests: {guest_count}', level=2)
    doc.add_heading(f'Start: {event_start}', level=2)

    # Create datetime variable
    current_date = date.today()
    
    for dict in final_mise_list:
        doc.add_heading(f"{dict['item']}", level=2)

        # Add items as paragraphs with a checkbox
        for mise in dict['mise']:
            doc.add_paragraph('\u2610' + ' ' + mise.capitalize())
            
        
    
    # Check for any duplicate html files
    docx_file_count = 0

    checklist_file_path = f'prep_and_checklists/{event_name}/{event_name}_Checklist_{current_date}_{docx_file_count}.docx'
    
    #continously checks until it finds a non-existent file name
    while os.path.exists(checklist_file_path):
        file_count += 1
        # this updates the file_count, allowing for it to be checked again in the while loop
        checklist_file_path = f'prep_and_checklists/{event_name}/{event_name}_Checklist_{current_date}_{docx_file_count}.docx'

    
    doc.save(checklist_file_path)
    print("Checklist Created!")
    

    conn.close()
#------------------------------------------------------------------------------------------
def get_order_list(item_id,event_name,db):

    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    current_date = date.today()
    result_list = []
    for id in item_id:
        cursor.execute("""
                SELECT ingredients.ingredient_name, ingredients.purveyor
                FROM ingredients
                JOIN menu_ingredients ON ingredients.ingredient_id = menu_ingredients.ingredient_id
                WHERE menu_ingredients.menu_item_id = ?;
            """, (id,)
        )
        
        results = cursor.fetchall()
        #print(results)
        for tuple_item in results:
        #    result_list.append({'Ingredient': tuple_item[0], 'Purveyor':tuple_item[1]})
             result_list.append([tuple_item[0], tuple_item[1]])
    #print(result_list)
    final_result_list = {'Ingredient':[], 'Purveyor':[]}
    for result in result_list:
        final_result_list['Ingredient'].append(result[0])
        final_result_list['Purveyor'].append(result[1])
        
    print(final_result_list)

    # Convert the final_result_list to a DataFrame
    df = pd.DataFrame(final_result_list)

    # Check for file existence and update the file name accordingly
    excel_file_count = 0
    excel_file = f"prep_and_checklists/{event_name}/{event_name}_{current_date}_{excel_file_count}.xlsx"

    while os.path.exists(excel_file):
        excel_file_count += 1
        excel_file = f"prep_and_checklists/{event_name}/Order_List_{event_name}_{current_date}_{excel_file_count}.xlsx"

    # Write the DataFrame to Excel
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=event_name, startrow= 2, index=False)

    # Optionally, load the workbook and apply formatting
    workbook = load_workbook(excel_file)
    order_sheet = workbook[order_sheet]

    # Add event title in the first cell
    order_sheet['A1'] = f"Order List: {event_name}"
    order_sheet['A1'].font = Font(name='Calibri', size=16, bold=True, underline='single', color='000000')

    # Input values based on purveyor

    
    # Save the workbook with formatting
    workbook.save(excel_file)
    print('Order sheet succesfully created!')
