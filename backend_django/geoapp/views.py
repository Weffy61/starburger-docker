import requests
from geopy import distance

from .models import Coordinate
from star_burger.settings import YANDEX_API_GEOCODER


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": YANDEX_API_GEOCODER,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    coordinate = Coordinate.objects.create(
        address=address,
        lat=lat,
        lon=lon
    )
    return coordinate


def get_distance(restaurant, restaurant_address, order_address, coords):
    try:
        restaurant_coords = next((coord for coord in coords if coord.address == restaurant_address), 0)
        if not restaurant_coords:
            restaurant_coords = fetch_coordinates(restaurant_address)
            coords.append(restaurant_coords)

        order_coords = next((coord for coord in coords if coord.address == order_address), 0)
        if not order_coords:
            order_coords = fetch_coordinates(order_address)
            coords.append(order_coords)

    except requests.exceptions:
        return 'Ошибка определения координат'
    total_distance = round(distance.distance((restaurant_coords.lat, restaurant_coords.lon),
                                             (order_coords.lat, order_coords.lon)).km, 3)
    return f'{restaurant} - {total_distance} км'
