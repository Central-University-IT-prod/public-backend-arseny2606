import os

from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
redis_password = os.getenv("REDIS_PASSWORD")
database_url = os.getenv("POSTGRES_CONN")
weather_api_token = os.getenv("WEATHER_API_TOKEN")
opentripmap_api_token = os.getenv("OPENTRIPMAP_API_TOKEN")
random_seed = os.getenv("RANDOM_SEED")
