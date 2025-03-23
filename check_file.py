import os

current_directory = os.getcwd()

def find_db():
    """Walk through directory and yield full paths of files ending with '.db'."""
    for root, _, files in os.walk(current_directory):
        for file in files:
            if file.endswith('.db'):
                yield os.path.join(root, file)

db_files = list(find_db())

if db_files:
    # Print each .db file found on a new line
    for file in db_files:
        print(file)
else:
    print("No .db files found.")    