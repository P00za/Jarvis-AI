from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicriphoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess as sp
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")  # Fixed: changed env_vars() to env_vars.get()
DefaultMessage = f'''(Username): Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''
subprocess_list = []  # Changed variable name to avoid conflict with imported module
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:  # Added proper file handling
        if len(File.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")

            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntrgration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"  # Added space after colon
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"  # Added space after colon
    formatted_chatlog = formatted_chatlog.replace("User", Username)  # Removed extra space
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname)  # Fixed typo in "Assistent"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
        Data = File.read()
        if len(str(Data)) > 0:
            lines = Data.split('\n')
            result = '\n'.join(lines)
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File:
                File.write(result)

def InitialExecution():
    SetMicriphoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntrgration()
    ShowChatsOnGUI()

InitialExecution()

def mainExecution():  # Fixed case to match usage (was MainExecution)
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening.....")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")  # Added space after colon
    SetAssistantStatus("Thinking....")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(  # Fixed typo in variable name (was Mearged_query)
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]  # Fixed typo in "genearal"
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution:  # Simplified condition
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\Imagegeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = sp.Popen(['python', r'Backend\ImageGeneration.py'],  # Changed to use 'sp' alias
                         stdout=sp.PIPE, stderr=sp.PIPE,
                         stdin=sp.PIPE, shell=False)
            subprocess_list.append(p1)  # Changed to use renamed list
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if (G and R) or R:  # Added parentheses for clarity
        SetAssistantStatus("Searching.....") 
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))  # Fixed variable name
        ShowTextToScreen(f"{Assistantname}: {Answer}")  # Added space after colon
        SetAssistantStatus("Answering.....")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking.....")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")  # Added space after colon
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching....")
                QueryFinal = Queries.replace("realtime", "")  # Fixed typo in "real-time"
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")  # Added space after colon
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")  # Added space after colon
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            mainExecution()  # Fixed case to match function definition
        else:
            AIStatus = GetAssistantStatus()

            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available.....")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True) 
    thread2.start()
    SecondThread()