import random

import requests

import config
from translations import INTERESTING_PLACE, INTERESTING_PLACES_NOT_FOUND, FOOD_PLACE, FOOD_PLACES_NOT_FOUND


def get_interesting_places(lat, lon):
    url = (
        f"https://api.opentripmap.com/0.1/ru/places/radius?radius=10000&lon={lon}&lat={lat}&kinds=interesting_places&rate=3"
        f"&apikey={config.opentripmap_api_token}")
    response = requests.get(url)
    return response.json()


def get_interesting_places_response(lat, lon):
    from tools.helpers import get_location_info
    places = get_interesting_places(lat, lon)
    if places and places["features"]:
        max_rate = max([place['properties']['rate'] for place in places["features"]])
        places["features"] = [place for place in places["features"] if place['properties']['rate'] == max_rate]
        features_dict = {place['properties']['name']: place for place in places["features"]}
        places["features"] = list(features_dict.values())
        random.seed(config.random_seed)
        random.shuffle(places["features"])
        places["features"] = places["features"][:5]
        response = ""
        for place in places["features"]:
            location_info = get_location_info(place['geometry']['coordinates'][1], place['geometry']['coordinates'][0])
            response += INTERESTING_PLACE.format(name=place['properties']['name'],
                                                 address=location_info.address["display_name"])
        return response
    return INTERESTING_PLACES_NOT_FOUND


def get_foods(lat, lon):
    url = (
        f"https://api.opentripmap.com/0.1/ru/places/radius?radius=10000&lon={lon}&lat={lat}&kinds=foods&rate=3"
        f"&apikey={config.opentripmap_api_token}")
    response = requests.get(url)
    return response.json()


def get_foods_response(lat, lon):
    from tools.helpers import get_location_info
    places = get_foods(lat, lon)
    if places and places["features"]:
        max_rate = max([place['properties']['rate'] for place in places["features"]])
        places["features"] = [place for place in places["features"] if place['properties']['rate'] == max_rate]
        features_dict = {place['properties']['name']: place for place in places["features"]}
        places["features"] = list(features_dict.values())
        random.seed(config.random_seed)
        random.shuffle(places["features"])
        places["features"] = places["features"][:5]
        response = ""
        for place in places["features"]:
            location_info = get_location_info(place['geometry']['coordinates'][1], place['geometry']['coordinates'][0])
            response += FOOD_PLACE.format(name=place['properties']['name'],
                                          address=location_info.address["display_name"],
                                          rate=place['properties']['rate'])
        return response
    return FOOD_PLACES_NOT_FOUND
