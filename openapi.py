import os
from openai import OpenAI

def get_chatgpt_response(prompt):

    

    # Get the API key from the environment variable
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    #print(prompt)

    # Check if the API key is available
    #if not api_key:
    #    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    # Set the API key for the OpenAI client
    #print(api_key)

    response = client.chat.completions.create(
                messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
    )
    print(response)
    #try:
    #    print("Sending request to OpenAI API...")  # Logging request
        # Make a request to the OpenAI API
    #    response = response = client.completions.create(model="gpt-3.5-turbo",
    #                                        prompt=prompt,
    #                                        max_tokens=150,
    #                                        temperature=0.7,
    #                                        n=1,
    #                                        stop=None)
    #    print("Received response from OpenAI API")  # Logging response

        # Return the response text
    #    return response.choices[0].text.strip()
    #except openai.OpenAIError as e:
        # Handle errors from the API
    #    return f"An error occurred: {e}"
