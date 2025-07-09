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
from database import upload_excel, input_new_data
from openapi import get_chatgpt_all_info
from check_file import find_db, find_xlsx_db
from prep_req import req_prep, test_prep_req, req_prep_ver_2
from beo import update_dropdown_menu_selection
from fuzzy import update_standard_menu, normalize, match_menu_items, get_standard_menu,get_standard_station_menu
from scan_excel import update_product_catalog
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

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'        
        gpt_prep_list(db)

    elif sys.argv[1] == 'upload_excel':

        print(find_xlsx_db())
        excel_file_to_upload = ''
        excel_file_input = input('Specify excel file by typing the corresponding number:')

        if excel_file_input == '1':
            excel_file_to_upload = 'nine_orchard_events_db_1.xlsx'
        elif excel_file_input == '2':
            excel_file_to_upload = 'nine_orchard_events_db_2.xlsx'
        
        print(find_db())
        db = ''
        db_input = input('Specify which database to update by typing the corresponding number:')

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'
        upload_excel(excel_file_to_upload, db)

    elif sys.argv[1] == 'input_new_data':
        print("Current databases:")
        print(find_db())
        db_input = input('Specify which database to update:')
        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'
        input_new_data(db)

    elif sys.argv[1] == 'find_db':
        find_db()

    elif sys.argv[1] == 'fuzzy_test':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'
        update_standard_menu(db)
        get_chatgpt_all_info(db)
        get_standard_menu()
        get_standard_station_menu()

    elif sys.argv[1] == 'update_standard_menu':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'
        update_standard_menu(db)

    elif sys.argv[1] == 'test_prep_req':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'

        beo_info = get_chatgpt_all_info(db)
        test_prep_req(beo_info[0], db)

    elif sys.argv[1] == 'test_excel_prep_list_ver_2':
        print(find_db())
        db = ''
        db_input = input('Specify which database to query by typing the corresponding number:')

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'

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

        if db_input == '1':
            db = 'purveyor_project_db_1.db'
        elif db_input == '2':
            db = 'purveyor_project_db_2.db'
        update_dropdown_menu_selection(db)

    elif sys.argv[1] == 'test_update_product_catalog':
        update_product_catalog()
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
    # Adds Bread and butter
    if event_type in event_type_list:
        item_ids.append(37)

    # Call the master_prep_list function using the returned variables
    master_prep_list(item_ids, event_name, guest_count, event_time, event_date,event_location, db, station_ids)
#------------------------------------------------------------------------------------------
       
def master_prep_list(item_ids, event_name, guest_count, event_time, event_date,event_location, db, station_ids):
    
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
    excel_prep_list_ver_2(item_ids, event_name, guest_count, event_time, event_date, event_location, db, station_ids)
    # Create word doc checklist for mise en place by dish
    word_checklist(item_ids, event_name, guest_count, event_time, event_date, event_location,db, station_ids)
    # Fill out prep requisition sheet
    #req_prep(item_ids, new_folder_path, event_date, event_name,db)
    req_prep_ver_2(item_ids, new_folder_path, event_date, event_name,db)

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