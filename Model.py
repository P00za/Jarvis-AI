import cohere # Import the cohere library for AI Services.
from rich import print  # Import the print function from the rich library for pretty printing.and enhancing terminal output.
from dotenv import dotenv_values # Import the dotenv library for loading environment variables from a .env file.

# Load environment variables from a .env file
env_vars = dotenv_values(".env")

# Retrieving API Keys.
CohereAPIKey =env_vars.get("CohereAPIKey")

#Create a cohere client using the provided API Key.
co = cohere.Client(api_key= CohereAPIKey)

# Define a list of recognizing function keywords for task categorization.
funcs=[
    "exit", "general", "realtime","open","close","play","generate image",
    "system","content","google search","reminder","youtube search"
]

# Initialize an empty list to store user messages.
messages =[]

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define a chat history with predefined user-client interaction s for context.
ChatHistory =[
    {"role":"USER","message":" Hello, how are you?"},
    {"role":"CHATBOT","message":" general Hello,how are you?"},
     {"role":"USER","message":" do you like pizza"},
    {"role":"CHATBOT","message":" general do you like pizza"},
     {"role":"USER","message":"open chrome and tell me about Mahatma Gandhi"},
    {"role":"CHATBOT","message":"open chrome, general tell me about Mahatma Gandhi "},
     {"role":"USER","message":" open chrome and firefox"},
    {"role":"CHATBOT","message":" open chrome , open firefox"},
    {"role":"USER","message":" what is today's date , remind me that I have a dance performance on 5th May at 11pm"},
    {"role":"CHATBOT","message":" general what is today's date, reminder 11:00pm 5th May dance performance"},
    {"role":"USER","message":" Chat with me."},
    {"role":"CHATBOT","message":" general Chat with me."},
]

# Define the main function for decision making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to messages list.
    messages.append({"role": "user","content":f"{prompt}"})

    # Create a streaming chat sesssion with the AI model.
    stream = co.chat_stream(
        model= 'command-r-plus',  #Specify the Cohere model to use.
        message=prompt, # pass the user's query to the AI model.
        temperature=0.7, # Set the creativity level of the model.
        chat_history=ChatHistory, # Provide the pre-defined chat history for context.
        prompt_truncation='OFF',# Ensures that the prompt is not truncated.
        connectors=[], # No additional connectors are needed.
        preamble=preamble #Pass the detailed preamble to guide the AI model.
    )

    # Initialize an empty string to store the AI model's response.
    response = ""

    # Itrate over the events in the stream  and captures  the text generation events.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text # Append generated text to the response string.

    # Remove newlines characters and split responses into individual tasks. 
    response = response.replace("\n","")
    response = response.split(",")

    # Strip leading and trailing whitespaces from each tasks.
    response = [i.strip() for i in response]

    # Initialize an empty list to filter valid tasks.
    temp = []

    # Filter the tasks based on recognized function keywords.
    for task in response :
        for func in funcs:
            if task.startswith(func):
                temp.append(task)  # Add valid tasks to the filtered list.

    # Update the response with the filtered list of tasks.
    response = temp

    # if '(query)' is  in the response,  recursively call the function for the further classification.
    if "(query)" in response:
        response = FirstLayerDMM(prompt=prompt)
        return newresponse # Return the response from the recursive call.
    else:
        return response # Return the filtered list of tasks.

# Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input until they choose to exit.
    while True:
        print(FirstLayerDMM(input(">>>")))