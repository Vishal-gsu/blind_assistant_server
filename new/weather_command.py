# import requests
# import pyttsx3

# api_key = "850ea6341b6f8c549de9073d78cb793f"  # Replace with your actual API key

# # Function to get weather information
# def get_weather(api_key, city):
#     base_url = "http://api.openweathermap.org/data/2.5/weather"
#     params = {
#         'q': city,
#         'appid': api_key,
#         'units': 'metric'
#     }
#     response = requests.get(base_url, params=params)
#     data = response.json()

#     if response.status_code == 200:
#         weather_description = data['weather'][0]['description']
#         temperature = data['main']['temp']
#         return f"The weather in {city} is {weather_description} with a temperature of {temperature} degrees Celsius."
#     else:
#         return f"Failed to get weather information. Error: {data.get('message', 'Unknown error')}"

# # Function to speak the weather information
# def speak_weather(api_key, city):
#     weather_info = get_weather(api_key, city)
#     engine = pyttsx3.init()
#     engine.say(weather_info)
#     engine.runAndWait()

# # Example usage
# city = "Bangalore"  # Corrected city name (note the correct spelling)
# speak_weather(api_key, city)



import requests
import pyttsx3
import speech_recognition as sr

api_key = "850ea6341b6f8c549de9073d78cb793f"  # Replace with your actual API key

# Initialize speech engine
engine = pyttsx3.init()

def get_voice_input():
    """Get city name through voice input"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Listening for city name...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
        
    try:
        return recognizer.recognize_google(audio).capitalize()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "Error: Speech service unavailable"

def get_weather(api_key, city):
    """Get weather information from OpenWeatherMap API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"The weather in {city} is {weather_description} with a temperature of {temperature}°C."
        return f"Error: {data.get('message', 'Unknown error')}"
    except requests.exceptions.RequestException:
        return "Failed to connect to weather service"

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def weather_report():
    """Main function to handle weather reporting flow"""
    speak("Which city's weather would you like to know?")
    city = get_voice_input()
    
    if not city or "Error" in city:
        speak("Sorry, I didn't catch that. Please try again.")
        return
    
    weather_info = get_weather(api_key, city)
    speak(weather_info)
    
    # Print results to console
    print(f"City: {city}")
    print(weather_info)

if __name__ == "__main__":
    weather_report()