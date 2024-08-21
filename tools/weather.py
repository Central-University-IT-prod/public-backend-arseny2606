import datetime

import requests

import config
from translations import WEATHER_NOT_FOUND


def get_weather_for_dates(date_start: datetime.date, date_end: datetime.date, lat: float, lon: float) -> str:
    weather = []
    date = date_start
    now = datetime.datetime.now().date()
    while date <= date_end and len(weather) < 5:
        try:
            if date < now:
                r = requests.get(
                    f"https://api.weatherapi.com/v1/history.json?q={lat},{lon}&dt={date.strftime('%Y-%m-%d')}&lang=ru&key={config.weather_api_token}")
                weather.append(
                    f"{date.strftime('%d.%m.%Y')}: {r.json()['forecast']['forecastday'][0]['day']['condition']['text']}, {r.json()['forecast']['forecastday'][0]['day']['avgtemp_c']}°C")
            elif date - datetime.timedelta(days=14) <= now:
                r = requests.get(
                    f"https://api.weatherapi.com/v1/forecast.json?q={lat},{lon}&dt={date.strftime('%Y-%m-%d')}&lang=ru&key={config.weather_api_token}")
                weather.append(
                    f"{date.strftime('%d.%m.%Y')}: {r.json()['forecast']['forecastday'][0]['day']['condition']['text']}, {r.json()['forecast']['forecastday'][0]['day']['avgtemp_c']}°C")
            else:
                r = requests.get(
                    f"https://api.weatherapi.com/v1/future.json?q={lat},{lon}&dt={date.strftime('%Y-%m-%d')}&lang=ru&key={config.weather_api_token}")
                weather.append(
                    f"{date.strftime('%d.%m.%Y')}: {r.json()['forecast']['forecastday'][0]['day']['condition']['text']}, {r.json()['forecast']['forecastday'][0]['day']['avgtemp_c']}°C")
        except (KeyError, IndexError):
            break
        date += datetime.timedelta(days=1)
    if not weather:
        return WEATHER_NOT_FOUND
    return '\n'.join(weather)
