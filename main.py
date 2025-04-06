from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
import chainlit as cl
import os
from typing import Optional, Dict
from agents.tool import function_tool
import requests

load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
weather_api_key = os.getenv('WEATHER_API_KEY')

provider = AsyncOpenAI(
    api_key=google_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=provider
)

run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)


BASE_URL = "https://api.weatherapi.com/v1/current.json"

@function_tool
def get_weather(location: str, unit: str = 'C') -> str:
    """Fetch weather for a given location and return detailed weather information"""
    params = {"key": weather_api_key, "q": location}
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "error" not in data:
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        feels_like_c = data["current"]["feelslike_c"]
        feels_like_f = data["current"]["feelslike_f"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]
        wind_mph = data["current"]["wind_mph"]
        condition = data["current"]["condition"]["text"]
        
        temp = temp_c if unit.upper() == 'C' else temp_f
        feels_like = feels_like_c if unit.upper() == 'C' else feels_like_f
        wind_speed = wind_kph if unit.upper() == 'C' else wind_mph
        unit_symbol = "°C" if unit.upper() == 'C' else "°F"
        wind_unit = "km/h" if unit.upper() == 'C' else "mph"

        return (
            f"📍 **Weather in {location}:** {condition} \n"
            f"🌡️ Temperature: {temp}{unit_symbol} (Feels like {feels_like}{unit_symbol}) \n"
            f"💧 Humidity: {humidity}% \n"
            f"🌬️ Wind Speed: {wind_speed} {wind_unit} \n"
            
        )
    else:
        return "❌ Error fetching weather data. Check location name."

weather_agent = Agent(
    name='weatherry',
    instructions="You are Weatherry, a friendly AI assistant specializing in weather information. Your goal is to provide helpful and accurate weather forecasts and conditions. Use the available tools to fetch the latest weather data for any location the user asks about. If a user asks a question that isn't related to weather, politely explain that you can only help with weather-related topics and redirect them back to your main function",
    tools=[get_weather]
)

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    """Handle the Auth callback from the Github 
    return the user object if the authentication is successful, None otherwise"""
    print(f"Provider: {provider_id}")
    print(f"user data: {raw_user_data}")

    return default_user


@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set('history', [])
    await cl.Message(content="Hey, there I am a Weather Agent").send()


@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get('history')
    history.append({'role':'user','content':message.content})

    result = await Runner.run(
    weather_agent,
    input=history,
    run_config=run_config
    )
    history.append({'role':'assistant','content':result.final_output})
    cl.user_session.set('history', history)

    await cl.Message(
        content=result.final_output
    ).send()
