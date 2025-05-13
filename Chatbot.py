from groq import Groq #importing the Groq library to use its API.
from json import load ,dump #importing the loads function from the json library to parse JSON data.
import datetime #importing the datetime module for real-time date and time information.
from dotenv import dotenv_values #importing the dotenv_values function from the dotenv library to load environment variables from .env file.

#load environment variables from .env file
env_vars = dotenv_values(".env")

#Retrive specific environment variable for username, Assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with the provided API key.
client = Groq(api_key = GroqAPIKey)

#Initialize an empty list to store chat messages.
messages = []

#  Define a system message that provides context to the API chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
#  A list of system instructions that the chatbot will follow to provide a helpful and informative response.
SystemChatBot =[
    {"role":"system","content":System}
]
# Attempt to load the chatbot's knowledge base from a JSON file.
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f) #Load existing messages from the chat log.
except FileNotFoundError:
    # If the file does not exist, create an empty JSON fole to store chat log.
    with open(r"Data\ChatLog.json","w") as f:
        dump([],f) #Create an empty list to store chat log.
# Functions to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now() # Get the current date and time.
    day = current_date_time.strftime("%A") #  day of the week.
    date = current_date_time.strftime("%d") # day of the month.
    month = current_date_time.strftime("%B") #  full month name.
    year = current_date_time.strftime("%Y") #  year in four digits.
    hour = current_date_time.strftime("%H") #  hour in 24-hour format.
    minute = current_date_time.strftime("%M") #  minute as a zero-padded decimal number
    second = current_date_time.strftime("%S") #  second as a zero-padded decimal number

    # Format the information into a string.
    data = f" Please use this real-time information if needed,\n"
    data += f"Day:{day}\n Date:{date}\n Month:{month}\n Year:{year}\n"
    data += f"Time:{hour} hours :{minute}minutes:{second}seconds.\n"
    return data
# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n') # Split the answer into lines.
    non_empty_lines =[ line for line in lines if line.strip() ] # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines) # Join the non-empty lines back into a string.
    return modified_answer
# Main Chatbot functions to handle user input and provide responses.
def ChatBot(Query):
    """ This function sends the user's query to the Groq API and returns the response. """
    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json","r") as f:
            messages = load(f)
        # Append the user's query to the chat log.
        messages.append({"role": "user", "content": f"{Query}"})

        #Make a request to the Groq API with the user's query for response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192", # Specify the AI model to use.
            messages = SystemChatBot + [{"role":"system","content":RealtimeInformation()}]+ messages, # Include system instructions, real-time info, and Chat history.
            max_tokens=1024, # Set the maximum number of tokens in the response.
            temperature=0.7 ,# Set the temperature for the response.
            top_p=1, # Use nucleus sampling to control diversity.
            stream= True ,# Enables the streaming of the response.
            stop = None # Allow the model to determine when to stop generating text.
        )
        Answer = "" # Initialize an empty string to store the response.

        # Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content: # Check if the chunk contains  current content.
                Answer += chunk.choices[0].delta.content # Append the content to the answer.
        
        Answer = Answer.replace("</s>","") # Clean up any unwanted tokens from the response.

        # Append the chatbot's response to the chat log.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json","w") as f:
            dump(messages , f , indent=4)

        # Return the formatted response.
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        # Handling errors by printing the exceptions and resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json","w") as f:
            dump([],f,indent=4)
        return ChatBot(Query) # Retry the query after resetting the chat log.
    
# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question:") # prompt the user for a question.
        print(ChatBot(user_input)) # send the question to the chatbot and print the response.