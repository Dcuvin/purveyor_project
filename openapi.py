import os
import re
import sqlite3
from openai import OpenAI


def get_chatgpt_all_info(text_file, db):

    #save chosen database into a string
    database = db
     # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Output the name of the event, 
                 the guest count, the event start and end time, the date of that event, event_type,
                 as well as all the food items in that order each on their own separate line. Do not label them.
                 Make sure that the event title
                 does not include a special character, and that the canapes are not numbered or contain an empty space. 
                 ."""},
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
    menu_items = content_list[5:len(content_list)]
    menu_items_lower = [i.lower() for i in menu_items]


    final_menu_items = []
    for item in menu_items_lower:
        split_item = item.split(',')
        for item in split_item:
            final_menu_items.append(item)

    

    #print(content_list)
    #print(menu_items_lower)
    print(event_name)
    print(final_menu_items)

    #does_it_work = []
    results = []
    new_menu_item = []
    conn = sqlite3.connect(database)
    # Cursor to execute commands
    cursor = conn.cursor()
    for item in final_menu_items:
        try:
            cursor.execute("""
                SELECT CAST(menu_item_id AS INTEGER) as menu_item_id
                FROM menu_items
                WHERE item_name = ?;
            """, (item,))
            #fetch the result
            result = cursor.fetchall()
            if result:
                #does_it_work.append("Y")
                results.append(result)
            else:
                new_menu_item.append(item)
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
    print(new_menu_item)
    return item_ids, event_name, guest_count, event_time, event_date, event_type
#------------------------------------------------------------------------------------------

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