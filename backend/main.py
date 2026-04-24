from fastapi import FastAPI 

from fastapi.middleware.cors import CORSMiddleware

#lets us define the shape of the data
from pydantic import BaseModel 

from dotenv import load_dotenv

from groq import Groq

import os

#gives python tools it needs to read and work with JSON data
import json

load_dotenv()

#creating a FastAPI application and storing it in a variable called app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*",]
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#creation of a data model/creating a blueprint for the data
#a valid chat request must have a field called message and value must be text
class ChatRequest(BaseModel):
    message: str

#opens the json file and reads(r) it. file is the variable name for the opened file
with open("knowledge.json", "r") as file:
    #takes the json data inside the file and converts it into a python dictionary
    f1_knowledge = json.load(file)


def search_knowledge(user_message):
    user_words = user_message.lower().split()
    matches = []

    for item in f1_knowledge:
        text = json.dumps(item).lower()
        score = 0

        for word in user_words:
            if word in text:
                score += 1

        if score > 0:
            matches.append((score, item))

    matches.sort(reverse=True, key=lambda x: x[0])

    top_matches = [item for score, item in matches[:5]]

    return top_matches

                

#a GET request sent to the browser which when run returns the function home()
@app.get("/")
def home():
    return{"message": "F1 Chatbot backend is running"}

#a POST request that comes to/chat, run the function chat()
@app.post("/chat")

#the function expects a request to follow the ChatRequest structure
def chat(request: ChatRequest):
    user_message = request.message

    relevant_knowledge = search_knowledge(user_message)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful Formula 1 chatbot. "
                    "Always prioritize the provided F1 knowledge when answering. "
                    "If the answer exists in the provided knowledge, use it directly. "
                    "Do NOT mention knowledge cutoffs. "
                    "Keep track of the conversation context. "
                    "When the user says 'he', 'him', 'his', 'that driver', or 'they', infer who they mean from the most recent driver, team, race, or topic discussed. "
                    "If the user replies with short follow-ups like 'yes', 'yeah', 'continue', 'tell me more', or 'go on', continue explaining the previous topic instead of treating it as a new question. "
                    "If the reference is genuinely unclear, ask a short clarifying question. "
                    "Keep answers clear, accurate, beginner-friendly, and focused on Formula 1."
                ),
            },
            {
                "role": "user",
                "content": f"Relevant F1 knowledge: {relevant_knowledge}",
            },
            {
                "role": "user",
                "content": user_message
            },
        ],
    )

    reply = response.choices[0].message.content

    return {
        "reply": reply
    }

    
            
            

