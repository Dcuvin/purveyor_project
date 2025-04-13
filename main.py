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
from prep_and_check_list import excel_prep_list, word_checklist, get_order_list
from database import upload_excel, input_new_data
from openapi import get_chatgpt_all_info
from check_file import find_db
#from purveyor import order_list
#------------------------------------------------------------------------------------------

def main():

    
    if len(sys.argv) == 0:  # Check if the required arguments are provided
        print("python3 functions.py 'function_name'...")  # Provide usage instructions
        return  # Exit the function if not enough arguments
    
    elif sys.argv[1] == 'gpt_prep_list':
        #prompt user to specify database
        db = input('Specify database...')
        gpt_prep_list(db)

    elif sys.argv[1] == 'upload_excel':
        print("Current databases:")
        find_db()
        excel_file_to_upload = input('Specify excel file:')

        if excel_file_to_upload == 1:
            excel_file_to_upload = 'nine_orchard_events_db_1.db'
        elif excel_file_to_upload == 2:
            excel_file_to_upload = 'nine_orchard_events_db_2.db'
        
        db = input('Specify which database to update:')

        if db == 1:
            db = 'purveyor_project_db_1.db'
        elif db == 2:
            db = 'purveyor_project_db_2.db'
        upload_excel(excel_file_to_upload, db)

    elif sys.argv[1] == 'input_new_data':
        print("Current databases:")
        find_db()
        excel_file_to_upload = input('Specify excel file:')
        db = input('Specify which database to update:')
        upload_excel(excel_file_to_upload, db)

    elif sys.argv[1] == 'find_db':
        find_db()

    elif sys.argv[1] == 'input_new_data':
        input_new_data()
    else:
        print("Invalid function name")  

def gpt_prep_list(db):

#save chosen database
    database = db
#Check filepath
    file_path = "prompt_file.txt"
    if os.path.exists(file_path):
        print("file_path is correct")
    else:
        print("ERROR")
          
    # Read the existing content
    read_file = ""
    with open("prompt_file.txt", 'r') as file:
        content = file.read()
        read_file += content
        #print(content)
    #print(read_file)

    

    # Put the function into a variable inorder to access the returned tuple
    all_info = get_chatgpt_all_info(read_file, database)

    item_ids = all_info[0]
    event_name = all_info[1]
    guest_count = all_info[2]
    event_time = all_info[3]
    event_date = all_info[4]
    event_type = all_info[5].lower()
    #print(item_ids)
    # if event_type is a seated dinner...
    event_type_list = ['seated dinner', 'seated meal', 'seated', ' ']
    # Adds Bread and butter
    if event_type in event_type_list:
        item_ids.append(37)

    # Call the master_prep_list function using the returned variables
    master_prep_list(item_ids, event_name, guest_count, event_time, event_date, db)
#------------------------------------------------------------------------------------------
       
def master_prep_list(item_ids, event_name, guest_count, event_time, event_date, db):
    
    # Specify the path of the new directory
    new_folder_path = f"prep_and_checklists/{event_name}"

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
    excel_prep_list(item_ids, event_name, guest_count, event_time, event_date,db) 
    word_checklist(item_ids, event_name, guest_count, event_time, event_date,db)
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