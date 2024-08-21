from unittest import mock

import pytest

from tools.helpers import get_country, get_city, get_city_and_country, get_location_info, get_profile_info, LocationInfo


@pytest.mark.parametrize("text, expected", [
    ("Россия", "Россия"),
    ("Франция", "Франция"),
    ("Германия", "Германия"),
    ("США", "Соединённые Штаты Америки"),
])
def test_get_country(text, expected):
    assert get_country(text) == expected


@pytest.mark.parametrize("text, country, expected", [
    ("Москва", "Россия", "Москва"),
    ("Париж", "Франция", "Париж"),
    ("Берлин", "Германия", "Берлин"),
    ("Нью-Йорк", "США", "Нью-Йорк"),
])
def test_get_city(text, country, expected):
    assert get_city(text, country)["name"] == expected


@pytest.mark.parametrize("text, expected", [
    ("Москва, Россия", "Москва"),
    ("Париж, Франция", "Париж"),
    ("Берлин, Германия", "Берлин"),
    ("Нью-Йорк, США", "Нью-Йорк"),
])
def test_get_city_and_country(text, expected):
    assert get_city_and_country(text)["name"] == expected


@pytest.mark.parametrize("lat, lon, expected", [
    (55.7522, 37.6156, LocationInfo(is_ok=True, country="Россия", city="Москва",
                                    user_output="Твоя страна Россия и город Москва сохранены.",
                                    latitude=55.7522, longitude=37.6156,
                                    address=mock.ANY)),
    (48.8566, 2.3522, LocationInfo(is_ok=True, country="Франция", city="Париж",
                                   user_output="Твоя страна Франция и город Париж сохранены.",
                                   latitude=48.8566, longitude=2.3522,
                                   address=mock.ANY)),
    (52.5200, 13.4050, LocationInfo(is_ok=True, country="Германия", city="Берлин",
                                    user_output="Твоя страна Германия и город Берлин сохранены.",
                                    latitude=52.5200, longitude=13.4050,
                                    address=mock.ANY)),
    (40.7128, -74.0060,
     LocationInfo(is_ok=True, country="Соединённые Штаты Америки", city="Нью-Йорк",
                  user_output="Твоя страна Соединённые Штаты Америки и город Нью-Йорк сохранены.",
                  latitude=40.7128, longitude=-74.0060,
                  address=mock.ANY)),
    (0, 0, LocationInfo(is_ok=False, country=None, city=None,
                        user_output=None,
                        latitude=None, longitude=None, address=None)),
])
def test_get_location_info(lat, lon, expected):
    assert get_location_info(lat, lon) == expected


def test_get_profile_info():
    from database.models.User import User
    user = User(id=1, name="Test", age=20, country="Russia", city="Moscow",
                bio="test")
    assert get_profile_info(user) == ("Профиль:\n\n"
                                      "Имя: {name}\n"
                                      "Возраст: {age}\n"
                                      "Страна и город: {country}, {city}\n"
                                      "Краткое описание: {bio}").format(name=user.name, age=user.age,
                                                                        country=user.country, city=user.city,
                                                                        bio=user.bio)
