from dataclasses import dataclass
from typing import Optional

from aiogram import types
from aiogram.types import BufferedInputFile
from geopy.geocoders import Nominatim
from sqlalchemy import inspect

from database.models import User, Travel, TravelLocation, TravelNote
from tools.map_draw import get_trip_map
from tools.markups import get_menu_keyboard_markup, get_travel_info_keyboard_markup, get_travel_list_keyboard_markup, \
    get_travel_locations_list_keyboard_markup, get_travel_location_info_keyboard_markup, \
    get_travel_notes_list_keyboard_markup, get_travel_note_info_keyboard_markup
from tools.places import get_interesting_places_response, get_foods_response
from tools.weather import get_weather_for_dates
from translations import COUNTRY_AND_CITY_RESPONSE, PROFILE_INFO, MENU_TEXT, TRAVEL_INFO, TRAVEL_INFO_DESCRIPTION, \
    TRAVEL_LIST_PAGE, ACCESS_DENIED, TRAVEL_LOCATION_INFO, TRAVEL_INFO_USERS

geolocator = Nominatim(user_agent="some_user_agent")


def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs + inspect(obj).mapper.relationships
    }


def get_country(text):
    country_info = geolocator.geocode(text, exactly_one=False, language="ru-ru")
    return [i for i in country_info if i.raw["addresstype"] == "country"][0].raw["name"]


def get_city(text, country):
    city_info = geolocator.geocode(f"{country} {text}", exactly_one=False, language="ru-ru")
    return [i for i in city_info if i.raw["addresstype"] == "city" or i.raw["addresstype"] == "town"][0].raw


def get_city_and_country(text):
    city_info = geolocator.geocode(f"{text}", exactly_one=False, language="ru-ru")
    return [i for i in city_info if i.raw["addresstype"] == "city" or i.raw["addresstype"] == "town"][0].raw


@dataclass
class LocationInfo:
    is_ok: bool
    country: Optional[str]
    city: Optional[str]
    user_output: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[dict]


def get_location_info(lat: float, lon: float) -> LocationInfo:
    location_info = geolocator.reverse((lat, lon), language="ru-ru")
    try:
        city = location_info.raw["address"].get("city", location_info.raw["address"].get("town"))
        country = location_info.raw["address"]["country"]
    except (IndexError, KeyError):
        return LocationInfo(is_ok=False, country=None, city=None, user_output=None, latitude=None, longitude=None,
                            address=None)
    return LocationInfo(is_ok=True, country=country, city=city,
                        user_output=COUNTRY_AND_CITY_RESPONSE.format(city=city, country=country), latitude=lat,
                        longitude=lon, address=location_info.raw)


def get_profile_info(user: User):
    return PROFILE_INFO.format(**object_as_dict(user))


async def send_menu(message: types.Message):
    await message.answer(MENU_TEXT, reply_markup=get_menu_keyboard_markup())


async def send_travel_info(message: types.Message | types.CallbackQuery, travel_model: Travel):
    if message.from_user.id != travel_model.owner_id and message.from_user.id not in [user.id for user in
                                                                                      travel_model.access_users]:
        if isinstance(message, types.Message):
            return await message.answer(ACCESS_DENIED)
        else:
            return await message.message.answer(ACCESS_DENIED)
    message_to_answer = TRAVEL_INFO
    if travel_model.description is not None:
        message_to_answer += TRAVEL_INFO_DESCRIPTION
    if len(travel_model.access_users) > 0:
        message_to_answer += TRAVEL_INFO_USERS
    travel_dict = object_as_dict(travel_model)
    travel_dict["users"] = ", ".join([f'<a href="tg://user?id={user.id}">{user.name}</a>' for user in travel_model.access_users])
    if isinstance(message, types.Message):
        if len(travel_model.locations) > 1:
            file = get_trip_map(travel_model)
            await message.answer_photo(BufferedInputFile(file.read(), filename="map.png"))
            file.close()
        await message.answer(message_to_answer.format(**travel_dict), parse_mode="html",
                             reply_markup=get_travel_info_keyboard_markup(travel_model,
                                                                          travel_model.owner.id == message.from_user.id))
    else:
        if len(travel_model.locations) > 1:
            file = get_trip_map(travel_model)
            await message.message.answer_photo(BufferedInputFile(file.read(), filename="map.png"))
            file.close()
        await message.message.answer(message_to_answer.format(**travel_dict), parse_mode="html",
                                     reply_markup=get_travel_info_keyboard_markup(travel_model,
                                                                                  travel_model.owner.id == message.from_user.id))
        await message.message.delete()


def get_paginated_travel_list(user: User, offset=0):
    all_travels = user.created_travels + user.access_travels
    all_travels.sort(key=lambda x: -x.id)
    travels_out = all_travels[offset:offset + 5]
    offset_left = -1 if offset - 5 < 0 else offset - 5
    offset_right = -1 if min(offset + 5, len(all_travels)) == len(all_travels) else min(offset + 5, len(all_travels))
    markup = get_travel_list_keyboard_markup(travels_out, offset_left, offset_right)
    return TRAVEL_LIST_PAGE.format(current_page=offset // 5 + 1,
                                   total_pages=max((len(all_travels) + 4) // 5, 1)), markup


def get_paginated_travel_locations_list(user_model: User, travel_model: Travel, offset=0):
    all_locations = travel_model.locations
    all_locations.sort(key=lambda x: x.start_date)
    locations_out = all_locations[offset:offset + 5]
    offset_left = -1 if offset - 5 < 0 else offset - 5
    offset_right = -1 if min(offset + 5, len(all_locations)) == len(all_locations) else min(offset + 5,
                                                                                            len(all_locations))
    markup = get_travel_locations_list_keyboard_markup(travel_model.id, locations_out, offset_left, offset_right,
                                                       user_model.id == travel_model.owner_id)
    return TRAVEL_LIST_PAGE.format(current_page=offset // 5 + 1,
                                   total_pages=max((len(all_locations) + 4) // 5, 1)), markup


async def send_travel_location_info(message: types.Message | types.CallbackQuery, location_model: TravelLocation):
    if message.from_user.id != location_model.travel.owner_id and message.from_user.id not in [user.id for user in
                                                                                               location_model.travel.access_users]:
        if isinstance(message, types.Message):
            return await message.answer(ACCESS_DENIED)
        else:
            return await message.message.answer(ACCESS_DENIED)
    object_dict = object_as_dict(location_model)
    object_dict["start_date"] = object_dict["start_date"].strftime("%d.%m.%Y")
    object_dict["end_date"] = object_dict["end_date"].strftime("%d.%m.%Y")
    object_dict["weather"] = get_weather_for_dates(location_model.start_date, location_model.end_date,
                                                   float(location_model.latitude), float(location_model.longitude))
    object_dict["interesting_places"] = get_interesting_places_response(location_model.latitude, location_model.longitude)
    object_dict["food_places"] = get_foods_response(location_model.latitude, location_model.longitude)
    if isinstance(message, types.Message):
        await message.answer(TRAVEL_LOCATION_INFO.format(**object_dict),
                             reply_markup=get_travel_location_info_keyboard_markup(location_model,
                                                                                   location_model.travel.owner.id == message.from_user.id))
    else:
        await message.message.edit_text(TRAVEL_LOCATION_INFO.format(**object_dict),
                                        reply_markup=get_travel_location_info_keyboard_markup(location_model,
                                                                                              location_model.travel.owner.id == message.from_user.id))


def get_paginated_travel_notes_list(user_model: User, travel_model: Travel, offset=0):
    all_notes = travel_model.notes
    if user_model.id != travel_model.owner_id:
        all_notes = [note for note in all_notes if note.is_public]
    all_notes.sort(key=lambda x: -x.id)
    notes_out = all_notes[offset:offset + 5]
    offset_left = -1 if offset - 5 < 0 else offset - 5
    offset_right = -1 if min(offset + 5, len(all_notes)) == len(all_notes) else min(offset + 5, len(all_notes))
    markup = get_travel_notes_list_keyboard_markup(travel_model.id, notes_out, offset_left, offset_right,
                                                   user_model.id == travel_model.owner_id)
    return TRAVEL_LIST_PAGE.format(current_page=offset // 5 + 1,
                                   total_pages=max((len(all_notes) + 4) // 5, 1)), markup


async def send_travel_note_info(message: types.Message | types.CallbackQuery, note_model: TravelNote):
    if message.from_user.id != note_model.travel.owner_id and message.from_user.id not in [user.id for user in
                                                                                           note_model.travel.access_users] \
            or (message.from_user.id != note_model.travel.owner_id and not note_model.is_public):
        if isinstance(message, types.Message):
            return await message.answer(ACCESS_DENIED)
        else:
            return await message.message.answer(ACCESS_DENIED)
    if isinstance(message, types.Message):
        await message.answer_document(note_model.file_id,
                                      reply_markup=get_travel_note_info_keyboard_markup(note_model,
                                                                                        note_model.travel.owner.id == message.from_user.id))
    else:
        await message.message.answer_document(note_model.file_id,
                                              reply_markup=get_travel_note_info_keyboard_markup(note_model,
                                                                                                note_model.travel.owner.id == message.from_user.id))
        await message.message.delete()
