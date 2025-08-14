# purveyor_project
I'am a Chef by trade, and have been in the hospitality industry since highschool. When the pandemic hit in 2019, I, like many, decided to learn a new skill to pass the time. Thus my coding journey began. Like many, I struggled to find a good idea for a coding project, but I kept learning in my free time while I freelanced working events.Fast forward to 2024 I started a new job as a Banquet Sous Chef in April for a hotel in NYC. It was here that I came up with the idea for this project. When it comes to Banquets, no two events are the same. That means differing menus, prep lists, checklists, and order lists. You can imagine how much more challenging that can be when dealing with multiple events happening everyday in a week. I immediately saw the benefits that automation and digitization could bring in order to create a more efficient workflow.



Functions:

database.py

db_input()
Prompts user to enter a number that corresponds to the database that they are trying to access.

excel_file_to_upload()
Prompts the user to enter a number that corresponds to the excel file that they are trying to upload to a database.

upload_excel()
Takes the database excel file, deletes the old data in the database, and reuploads the excel file into the existing database.

input_new_data()
Opens a json file with data for a new menu item to be added to the database, and checks the database to see if the menu item exists, and if not, add it to the database.