from datetime import date
import pandas as pd
import sqlite3
import re
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
import sys #import sys modulet o access command-line arguments
import os #This statement is used to include the functionality of
#the os module, allowing you to interact with the operating system in a portable way
from bs4 import BeautifulSoup
import openai
#from docx import Document
from prep_and_check_list import excel_prep_list, word_checklist, get_order_list, excel_prep_list_ver_2
from database import upload_excel, input_update_data, db_input, excel_file_to_upload, delete_data, get_ingredients
from openapi import get_chatgpt_all_info
from check_file import find_db, find_xlsx_db, find_xlsx_item_library
from prep_req import req_prep, test_prep_req, req_prep_ver_2
from beo import update_dropdown_menu_selection
from fuzzy import update_standard_menu, normalize, match_menu_items, get_standard_menu,get_standard_station_menu
from product_catalog import update_ingredient_table, input_menu_ingredient, get_menu_item_ingredients, menu_cost, upload_xtrachef_item_library
#------------------------------------------------------------------------------------------

def main():

    
    if len(sys.argv) == 0:  # Check if the required arguments are provided
        print("python3 functions.py 'function_name'...")  # Provide usage instructions
        return  # Exit the function if not enough arguments
    
    elif sys.argv[1] == 'gpt_prep_list':
        #prompt user to specify database
        print(find_db())
        db = ''
        db_input = input('Specify which database to use by typing the corresponding number:')
     

        db = f"purveyor_project_db_{db_input}.db"

        gpt_prep_list(db)

    elif sys.argv[1] == 'upload_excel':

        print(find_xlsx_db())
        excel_file_to_upload = ''
        excel_file_input = input('Specify excel file by typing the corresponding number:')



        excel_file_to_upload = f"nine_orchard_events_db_{excel_file_input}.xlsx"
        print(find_db())
        db = ''
        db_input = input('Specify which database to update by typing the corresponding number:')

 

        db = f"purveyor_project_db_{db_input}.db"

        upload_excel(excel_file_to_upload, db)
        update_standard_menu(db)

    # Updates / Inputs data pythonically into desired database.
    elif sys.argv[1] == 'input_data':
        print("Current databases:")
        print(find_db())
        db_input = input('Specify which database to use:')

       

        db = f"purveyor_project_db_{db_input}.db"

        input_update_data(db)
        #get_ingredients(db)

    elif sys.argv[1] == 'find_db':
        find_db()

    elif sys.argv[1] == 'fuzzy_test':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

       

        db = f"purveyor_project_db_{db_input}.db"

        update_standard_menu(db)
        get_chatgpt_all_info(db)
        get_standard_menu()
        get_standard_station_menu()

    elif sys.argv[1] == 'update_standard_menu':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        

        db = f"purveyor_project_db_{db_input}.db"

        update_standard_menu(db)

    elif sys.argv[1] == 'test_prep_req':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

       

        db = f"purveyor_project_db_{db_input}.db"


        beo_info = get_chatgpt_all_info(db)
        test_prep_req(beo_info[0], db)

    elif sys.argv[1] == 'test_excel_prep_list_ver_2':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

     

        db = f"purveyor_project_db_{db_input}.db"


        all_info = get_chatgpt_all_info(db)
        # Specify the path of the new directory
        new_folder_path = f"prep_and_checklists/Test"

        # Create the directory
        try:
            os.makedirs(new_folder_path, exist_ok=True)
            print(f"Directory '{new_folder_path}' created successfully")
        except FileExistsError:
            print(f"Directory '{new_folder_path}' already exists")
        except FileNotFoundError:
            print(f"Parent directory does not exist")
        except Exception as e:
            print(f"An error occurred: {e}")

        else:
            print("Invalid function name")  

        excel_prep_list_ver_2(all_info[0], all_info[1], all_info[2], all_info[3], all_info[4], all_info[6], db, all_info[7])

    elif sys.argv[1] == 'update_beo_form':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')


        db = f"purveyor_project_db_{db_input}.db"

        update_dropdown_menu_selection(db)

    # Updates the ingredient table inside desired database using the normalized item_library file downloaded from Xtra Chef

    elif sys.argv[1] == 'update_ingredient_table':
        
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')


        db = f"purveyor_project_db_{db_input}.db"

        file_count = 0
        item_library_file ={}

        for i in find_xlsx_item_library():
            file_count += 1
            item_library_file[str(file_count)] = i
            print(f"{file_count}.  {i}")
        
        item_library_input = input('Specify item_library excel file by typing the corresponding number: ')

        chosen_item_library_file = item_library_file[str(item_library_input)]

        print(chosen_item_library_file)

        update_ingredient_table(db,  chosen_item_library_file)
    
    elif sys.argv[1] == "input_menu_ingredient":
        print(find_db())
        excel_file_to_upload = ''
        excel_file_input = input('Specify db file by typing the corresponding number:')

  

        excel_file_to_upload = f"nine_orchard_events_db_{excel_file_input}.xlsx"

        
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

     
        db = f"purveyor_project_db_{db_input}.db"

        input_menu_ingredient(excel_file_to_upload,db)

    elif sys.argv[1] == 'get_menu_item_ingredients':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')


        db = f"purveyor_project_db_{db_input}.db"

        get_menu_item_ingredients(db)

    elif sys.argv[1] == 'menu_cost':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')


        db = f"purveyor_project_db_{db_input}.db"

        menu_cost(db)
    
    elif sys.argv[1] == 'delete_data':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')
        item_ids = input('Specify item_ids: ')

        db = f"purveyor_project_db_{db_input}.db"

        delete_data(item_ids,db)

    elif sys.argv[1] == 'get_ingredients':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        db = f"purveyor_project_db_{db_input}.db"

        get_ingredients(db)

    #Takes the newly downloaded item library from Xtra Chef and creates a normalized item description column withing the same file. It then queries the desired database for any existing entries and uses INSERT OR REPLACE

    elif sys.argv[1] == 'normalize_item_library':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        db = f"purveyor_project_db_{db_input}.db"

        file_count = 0
        item_library_file ={}

        for i in find_xlsx_item_library():
            file_count += 1
            item_library_file[str(file_count)] = i
            print(f"{file_count}.  {i}")
        
        item_library_input = input('Specify item_library excel file by typing the corresponding number: ')

        chosen_item_library_file = item_library_file[str(item_library_input)]

        print(chosen_item_library_file)
        upload_xtrachef_item_library(chosen_item_library_file, db)
#------------------------------------------------------------------------------------------
def gpt_prep_list(db):

    # Put the function into a variable inorder to access the returned tuple
    all_info = get_chatgpt_all_info(db)

    item_ids = all_info[0]
    event_name = all_info[1]
    guest_count = all_info[2]
    event_time = all_info[3]
    event_date = all_info[4]
    event_type = all_info[5].lower()
    event_location = all_info[6]
    station_ids = all_info[7]
    #print(item_ids)
    # if event_type is a seated dinner...
    event_type_list = ['seated dinner', 'seated meal', 'seated', ' ']
    # Adds Bread and butter for db_3
    if event_type in event_type_list:
       item_ids.append(37)

    # Call the master_prep_list function using the returned variables
    master_prep_list(item_ids, event_name, guest_count, event_time, event_date,event_location, db, station_ids,event_type)
#------------------------------------------------------------------------------------------
       
def master_prep_list(item_ids, event_name, guest_count, event_time, event_date,event_location, db, station_ids, event_type):
    
    # Specify the path of the new directory
    new_folder_path = f"prep_and_checklists/{event_name}"

    # Create the directory
    try:
        os.makedirs(new_folder_path, exist_ok=True)
        print(f"✅ Directory '{new_folder_path}' created successfully!")
    except FileExistsError:
        print(f"👀 Directory '{new_folder_path}' already exists")
    except FileNotFoundError:
        print(f"Parent directory does not exist")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Update standard_menu names for fuzzy logic
    update_standard_menu(db)
    # Create excel prep and order list
    #excel_prep_list(item_ids, event_name, guest_count, event_time, event_date, event_location, db) 
    final_ids = excel_prep_list_ver_2(item_ids, event_name, guest_count, event_time, event_date, event_location, db, station_ids,event_type)
    # Create word doc checklist for mise en place by dish
    word_checklist(final_ids, event_name, guest_count, event_time, event_date, event_location,db, station_ids)
    # Fill out prep requisition sheet
    #req_prep(item_ids, new_folder_path, event_date, event_name,db)
    req_prep_ver_2(final_ids, new_folder_path, event_date, event_name,db)

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