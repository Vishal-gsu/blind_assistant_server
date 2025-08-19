# llm.py

import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# Weather API configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Default city, can be changed by user
DEFAULT_CITY = "Bengaluru"

def extract_city(user_input):
    match = re.search(r"(?:weather|temperature|forecast) (?:in|at|for) ([a-zA-Z ]+)", user_input.lower())
    if match:
        return match.group(1).strip().title()
    match = re.search(r"in ([a-zA-Z ]+)", user_input.lower())
    if match:
        return match.group(1).strip().title()
    return None

def get_intent(user_input):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")

    # REFINED: Added more keywords and a new intent
    keyword_to_intent = {
        "object_detection": ["object", "detect", "what do you see", "look around"],
        "face_recognition": ["who is this", "who do you see"],
        "save_face": ["save face", "save this person", "remember this person"], # NEW INTENT
        "weather": ["weather", "temperature", "forecast", "hot", "cold", "rain"],
        "ocr": ["read", "text", "document", "what does this say"],
        "set_city": ["set city", "change location", "my location"],
        "exit": ["exit", "quit", "goodbye", "stop application"],
    }

    for intent, keywords in keyword_to_intent.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            return intent

    # REFINED: More direct system prompt for the LLM
    system_prompt = (
        "You are an intent recognition system for a blind assistive device. "
        "Your ONLY job is to classify the user's command into one of the following categories: "
        "'object_detection', 'face_recognition', 'weather', 'ocr', 'exit', 'set_city', 'save_face', or 'unknown'. "
        "Do not provide explanations. Respond with only the category name."
    )
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        intent = response.json()["choices"][0]["message"]["content"].strip().lower().replace("'", "")
        if intent in keyword_to_intent or intent == "unknown":
            return intent
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API for intent: {e}")
    
    return "unknown"

def get_weather_data(city):
    if not WEATHER_API_KEY: return None
    params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': city,
                'description': data['weather'][0]['description'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None

def get_response(user_input, intent, city=None):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    # REFINED: A much stricter prompt for concise, spoken-friendly answers.
    system_prompt = (
        "You are a voice assistant for a visually impaired user. Your responses MUST be extremely concise, "
        "direct, and factual. State the information directly. Do not use conversational filler like 'Sure!' "
        "or 'Here is the weather'. Just state the fact. For weather, give a single, short sentence. "
        "For confirming a city change, just say 'Location set to [City].'"
    )
    
    if intent == "weather":
        city = city or extract_city(user_input) or DEFAULT_CITY
        weather_data = get_weather_data(city)
        if weather_data:
            user_input_for_llm = (
                f"The weather in {weather_data['city']} is {weather_data['description']} "
                f"at {weather_data['temperature']:.0f} degrees, feeling like {weather_data['feels_like']:.0f} degrees. "
                f"Summarize this in one brief, natural sentence."
            )
        else:
            user_input_for_llm = f"I could not get weather for {city}. Apologize concisely."
    elif intent == "set_city":
        city = extract_city(user_input)
        if not city:
            # If city is not in the phrase, the user might say it next.
            # This logic is now handled in main.py, here we just confirm.
            return f"Which city would you like to set?", None
        user_input_for_llm = f"Confirm that the default city has been set to {city}."
    else: # For 'unknown' or other general queries
        user_input_for_llm = user_input

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input_for_llm}
        ]
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    reply = response.json()["choices"][0]["message"]["content"].strip()
    return reply, city

def set_default_city(new_city):
    global DEFAULT_CITY
    if new_city:
        DEFAULT_CITY = new_city.title()
    return DEFAULT_CITY