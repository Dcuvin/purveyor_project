import os
import re
import sqlite3
from openai import OpenAI
from fuzzy import update_standard_menu, normalize, match_menu_items, get_standard_menu, get_standard_station_menu


def get_chatgpt_all_info(db):

    #Check filepath of the txt file that contains the copy and paste BEO 
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

    
     # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Extract and Isolate the following: Name of the event, 
                 the guest count, the event start and end time, the date of that event, the event type, the event location,
                 and all the food items, each on their own separate line. Do not label any of the extracted information, and
                 make sure that the event title
                 does not include a special character. If any info is blank, replace with N/A.
                 ."""},
                { "role": "user","content": read_file,}
            ],
            model="gpt-4o",
    )

    content = response.choices[0].message.content
    #print(content)
    content_list =content.split('\n')

    event_name = content_list[0]
    guest_count = content_list[1]
    event_time =f"{content_list[2]}"
    event_date = content_list[3]
    event_type = content_list[4]
    event_location = content_list[5]
    menu_items = content_list[6:len(content_list)]
    #menu_items_normalize = [i.normalize() for i in menu_items]


    extracted_menu_items = []
    for item in menu_items:
        split_item = item.split(',')
        for item in split_item:
                extracted_menu_items.append(item)

    choices = get_standard_menu()
    final_menu_items_choices = []
    for item in extracted_menu_items:
         final_menu_items_choices.append(match_menu_items(item, choices))
    print(final_menu_items_choices)
    
    station_choices = get_standard_station_menu()
    final_stations_choices = []
    for item in extracted_menu_items:
        final_stations_choices.append(match_menu_items(item, station_choices))
    print(final_stations_choices)

    #print(content_list)
    #print(menu_items_lower)
    #print(f"Event Name: {event_name}")
    #print(f"extracted_menu_items: {extracted_menu_items}")
    #print(f"final_standard_menu_items: {final_standard_menu_items}")

    #does_it_work = []
    item_ids = []
    station_ids = []
    final_menu_items = []
    final_stations = []
    conn = sqlite3.connect(db)
    # Cursor to execute commands
    cursor = conn.cursor()
    #for item in extracted_menu_items:
    for item in final_menu_items_choices:
        #print(item)
        try:
            cursor.execute("""
               SELECT menu_item_id
                FROM menu_items
                WHERE item_name = ?;
                """, (item,))
            #fetch the result, a list of tuples
            result = cursor.fetchall()
            #print(result)
            if not result:
                continue
            else:
                item_ids.append(result[0][0])
                final_menu_items.append(item)
           
        except sqlite3.DatabaseError:
            continue

    for station in  final_stations_choices:
        #print(item)
        try:
            cursor.execute("""
               SELECT station_id
                FROM stations
                WHERE station_name = ?;
                """, (station,))
            #fetch the result, a list of tuples
            result = cursor.fetchall()
            #print(result)
            if not result:
                continue
            else:
                station_ids.append(result[0][0])
                final_stations.append(station)
           
        except sqlite3.DatabaseError:
            continue
    conn.close()
    
    #print(does_it_work)
    #print(results)
    print(f"item_ids: {item_ids}")
    print(final_menu_items)
    print(f"station_ids: {station_ids}")
    print(final_stations)
    print(f"Time: {event_time}")
    print(f"Date: {event_date}")
    return item_ids, event_name, guest_count, event_time, event_date, event_type, event_location, station_ids
