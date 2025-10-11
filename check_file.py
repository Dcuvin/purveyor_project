import os

current_directory = os.getcwd()
db_files = []
def find_db():
    """Walk through directory and yield full paths of files ending with '.db'."""
    for root, _, files in os.walk(current_directory):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    return db_files

#------------------------------------------------------------------------------------------
xlsx_files = []
def find_xlsx_db():
    """Walk through directory and yield full paths of xlsx files ending with 'db'."""
    for root, _, files in os.walk(current_directory):
        for file in files:
            if "nine_orchard_events_db" in file and file.endswith('.xlsx'):
                xlsx_files.append(os.path.join(root, file))
    return xlsx_files

#------------------------------------------------------------------------------------------

item_library_xlsx_files = []
def find_xlsx_item_library():
    """Walk through directory and yield full paths of xlsx files with 'item_library'."""
    for root, _, files in os.walk(current_directory):
        for file in files:
            if "item_library" in file and file.endswith('.xlsx'):
                item_library_xlsx_files.append(os.path.join(file))
    return item_library_xlsx_files
