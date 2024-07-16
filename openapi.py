import os
from openai import OpenAI

def get_chatgpt_master(event_info, menu_items):


    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response_1 = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Output the name of the event, 
                 the guest count, the event timing and the date of that event 
                 in that order each on their own separate line """},
                { "role": "user","content": event_info,}
            ],
            model="gpt-3.5-turbo",
    )
   
    response_2 = client.chat.completions.create(
                messages=[
               {"role": "system", "content": "Identify the food items that have capital letters and output them each on its own separate line"},
                { "role": "user","content": menu_items,}
            ],
            model="gpt-3.5-turbo",
    )

    content_1 = response_1.choices[0].message.content
    content_list_1 =content_1.split('\n')
    content_2 = response_2.choices[0].message.content
    content_list_2 =content_2.split('\n')
    #return content_list

    print(content_list_1)
    print(content_list_2) 
def get_chatgpt_menu_items(prompt):

    

    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
   
    response = client.chat.completions.create(
                messages=[
               {"role": "system", "content": "Identify the food items that have capital letters and output them each on its own separate line"},
                { "role": "user","content": prompt,}
            ],
            model="gpt-3.5-turbo",
    )

    content = response.choices[0].message.content
    content_list =content.split('\n')
    #return content_list

    print(content_list) 
    
#------------------------------------------------------------------------------------------
def get_chatgpt_event_info(prompt):
    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
                messages=[
                {"role": "system", "content": """Output the name of the event, 
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