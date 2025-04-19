#Fills out a requisition form for AM prep team for events prep.
# Saved into the event_name folder as a separate xlsx file to be later uploaded to a shared google drive
#*** Need to add a boolean column in db for am prep
#*** Need to add sql query to check boolean column

import pandas as pd
from openpyxl import load_workbook #imports python library for reading and writting excel files
import sqlite3
import time
import os
import shutil


def req_prep(item_ids, excel_folder_path, event_date, event_name):
    
    # Get the current working directory
    cwd = os.getcwd()
    
    # Create name for new event_req xlsx file
    new_file_name = f"EVENTS REQ {event_date}.xlsx"

    # EVENTS REQ TEMPLATE file_path
    event_req_template_file_path = os.path.join(cwd, 'EVENTS REQ - TEMPLATE.xlsx')

    # File path for the folder where the copied template will be saved to
    dest_dir = os.path.join(cwd, excel_folder_path)

    # File path of 
    dest_path = os.path.join(dest_dir, new_file_name)

    # 3. Sanity check that the source exists
    if not os.path.isfile(event_req_template_file_path ):
        raise FileNotFoundError(f"Source file not found: {event_req_template_file_path }")

    # 4. Create destination folder if needed
    os.makedirs(dest_dir, exist_ok=True)

    # 5. Copy (using copy2 to preserve metadata)
    shutil.copy2(event_req_template_file_path , dest_path)

    print(f"Copied:\n  {event_req_template_file_path }\n→ {dest_path}")
    return dest_path

    pass