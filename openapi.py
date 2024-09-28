import os
import re
import sqlite3
from openai import OpenAI

def chatgpt_generated_prep_list(text_file):
    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response_1 = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Identify the name of the event, the guest count, the event start and end time, and the date of that event.
                 Do not include special characters."""},
                { "role": "user","content": text_file,}
            ],
            model="gpt-3.5-turbo",
    )

    response_2 = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Identify all the food items and their components and output them each on its own separate line.
                 Do not include special characters."""},
                { "role": "user","content": text_file,}
            ],
            model="gpt-3.5-turbo",
    )

    event_info = response_1.choices[0].message.content
    menu_items = response_2.choices[0].message.content
    #print(event_info)
    #print(menu_items)
    event_info_list =event_info.split('\n')
    menu_item_list =menu_items.split('\n')
    #print(event_info_list)
    #print(menu_item_list)

# ------------------------------------------------------------------------------------------
def get_chatgpt_all_info(text_file):
     # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Output the name of the event, 
                 the guest count, the event start and end time, the date of that event, the event type,
                 as well as all the food items in that order each on their own separate line. Do not label them.
                 Make sure that the event title and canapes
                 does not include a special character as the first letter, and that the canapes are not numbered or contain an empty space. """},
                { "role": "user","content": text_file,}
            ],
            model="gpt-3.5-turbo",
    )

    content = response.choices[0].message.content
    #print(content)
    content_list =content.split('\n')

    event_name = content_list[0]
    guest_count = content_list[1]
    event_time = content_list[2]
    event_date = content_list[3]
    event_type = content_list[4]
    menu_items = content_list[4:len(content_list)]

    menu_items_lower = [i.lower() for i in menu_items]

    #modified_menu_items = []
    #for item in menu_items_lower:
    #    modified_item = item.replace("&", "and")
    #    modified_menu_items.append(modified_item)

    final_menu_items = []
    for item in menu_items_lower:
        split_item = item.split(',')
        for item in split_item:
            final_menu_items.append(item)

    

    #print(content_list)
    #print(menu_items_lower)
    print(final_menu_items)
    does_it_work = []
    results = []
    conn = sqlite3.connect('purveyor_project_db.db')
    # Cursor to execute commands
    cursor = conn.cursor()
    for item in final_menu_items:
        try:
            cursor.execute("""
                SELECT menu_item_id
                FROM menu_items
                WHERE item_name = ?;
            """, (item,))
            #fetch the result
            result = cursor.fetchall()
            if result:
                #does_it_work.append("Y")
                results.append(result)
            else:
                continue
                #does_it_work.append("N")
            #does_it_work.append("Y")

        except sqlite3.DatabaseError:
            #does_it_work.append("N")
            continue
    conn.close()
    # list comprehension to access the list of lists of tuples that contain item_ids
    item_ids = [i[0][0] for i in results]
    #print(does_it_work)
    #print(results)
    print(item_ids)
    return item_ids, event_name, guest_count, event_time, event_date, event_type
#------------------------------------------------------------------------------------------

def get_chatgpt_menu_items(prompt):

    

    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
   
    response = client.chat.completions.create(
                messages=[
               {"role": "system", "content": "Identify all the food items and output them each on its own separate line"},
                { "role": "user","content": prompt,}
            ],
            model="gpt-3.5-turbo",
    )

    content = response.choices[0].message.content
    #content_list =content.split(',')
    # Regular expression pattern for multiple delimiters
    pattern = r'[\n,]'
    content_list = re.split(pattern, content)
    return content_list

    #print(content_list) 
    
#------------------------------------------------------------------------------------------
def get_chatgpt_event_info(prompt):
    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Identify the name of the event, 
                 the guest count, the event timing and the date of that event 
                 in that order each on their own separate line """},
                { "role": "user","content": prompt,}
            ],
            model="gpt-3.5-turbo",
    )

    content = response.choices[0].message.content
    content_list =content.split('\n')
    return content_list
    #print(content_list)