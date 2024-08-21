import io
import random
from tempfile import NamedTemporaryFile

import mercantile
import requests
from cairo import ImageSurface, FORMAT_ARGB32, Context


def get_map(west, south, east, north, zoom):
    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    for t in tiles:
        server = random.choice(['a', 'b', 'c'])
        url = 'https://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        response = requests.get(url, headers={"User-Agent": "some-valid-user-agent"}).content
        img = ImageSurface.create_from_png(io.BytesIO(response))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()

    bounds = {
        "left": min([mercantile.xy_bounds(t).left for t in tiles]),
        "right": max([mercantile.xy_bounds(t).right for t in tiles]),
        "bottom": min([mercantile.xy_bounds(t).bottom for t in tiles]),
        "top": max([mercantile.xy_bounds(t).top for t in tiles]),
    }

    kx = map_image.get_width() / (bounds['right'] - bounds['left'])
    ky = map_image.get_height() / (bounds['top'] - bounds['bottom'])

    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    offset_left = (left_top[0] - bounds['left']) * kx
    offset_top = (bounds['top'] - left_top[1]) * ky
    offset_right = (bounds['right'] - right_bottom[0]) * kx
    offset_bottom = (right_bottom[1] - bounds['bottom']) * ky

    map_image_clipped = ImageSurface(
        FORMAT_ARGB32,
        map_image.get_width() - int(offset_left + offset_right),
        map_image.get_height() - int(offset_top + offset_bottom),
    )

    ctx = Context(map_image_clipped)
    ctx.set_source_surface(map_image, -offset_left, -offset_top)
    ctx.paint()
    return map_image_clipped


def get_trip_map(trip):
    west = 180
    south = 90
    east = -180
    north = -90
    locations = trip.locations
    locations.sort(key=lambda location: location.start_date)
    coords = ";".join([f"{location.longitude},{location.latitude}" for location in locations])
    route = requests.get(f"https://router.project-osrm.org/route/v1/driving/{coords}", params={
        "geometries": "geojson",
        "overview": "full",
    })
    route = route.json()
    for coord in route['routes'][0]['geometry']['coordinates']:
        west = min(west, float(coord[0]))
        south = min(south, float(coord[1]))
        east = max(east, float(coord[0]))
        north = max(north, float(coord[1]))

    zoom = 2
    while True:
        tiles = list(mercantile.tiles(west, south, east, north, zoom))
        if len(tiles) >= 10:
            break
        zoom += 1
    map_image = get_map(west, south, east, north, zoom)
    coordinates = route['routes'][0]['geometry']['coordinates']
    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)

    kx = map_image.get_width() / (right_bottom[0] - left_top[0])
    ky = map_image.get_height() / (right_bottom[1] - left_top[1])
    context = Context(map_image)
    for c in coordinates:
        x, y = mercantile.xy(c[0], c[1])
        x = (x - left_top[0]) * kx
        y = (y - left_top[1]) * ky
        context.line_to(x, y)

    context.set_source_rgba(1, 0, 0, 0.5)
    context.set_line_width(10)
    context.stroke()
    f = NamedTemporaryFile(mode="w+b", suffix=".png")
    map_image.write_to_png(f.name)
    return f


def get_trip_route(trip, user):
    from tools.helpers import get_city

    west = 180
    south = 90
    east = -180
    north = -90
    user_city_coords = get_city(user.city, user.country)["lat"], get_city(user.city, user.country)["lon"]
    locations = trip.locations
    locations.sort(key=lambda location: location.start_date)
    coords = ";".join([f"{location[1]},{location[0]}" for location in
                       [user_city_coords, [locations[0].latitude, locations[0].longitude]]])
    route = requests.get(f"https://router.project-osrm.org/route/v1/driving/{coords}", params={
        "geometries": "geojson",
        "overview": "full",
    })
    route = route.json()
    for coord in route['routes'][0]['geometry']['coordinates']:
        west = min(west, float(coord[0]))
        south = min(south, float(coord[1]))
        east = max(east, float(coord[0]))
        north = max(north, float(coord[1]))

    zoom = 2
    while True:
        tiles = list(mercantile.tiles(west, south, east, north, zoom))
        if len(tiles) >= 10:
            break
        zoom += 1
        if zoom == 18:
            break
    map_image = get_map(west, south, east, north, zoom)
    coordinates = route['routes'][0]['geometry']['coordinates']
    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    if right_bottom[0] - left_top[0] == 0 or right_bottom[1] - left_top[1] == 0:
        return None
    kx = map_image.get_width() / (right_bottom[0] - left_top[0])
    ky = map_image.get_height() / (right_bottom[1] - left_top[1])
    context = Context(map_image)
    for c in coordinates:
        x, y = mercantile.xy(c[0], c[1])
        x = (x - left_top[0]) * kx
        y = (y - left_top[1]) * ky
        context.line_to(x, y)

    context.set_source_rgba(1, 0, 0, 0.5)
    context.set_line_width(10)
    context.stroke()
    f = NamedTemporaryFile(mode="w+b", suffix=".png")
    map_image.write_to_png(f.name)
    return f
