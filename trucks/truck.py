from urllib import response
import requests
from shapely.geometry import shape
from shapely.ops import linemerge
import random
import datetime

# List of cities and their longitude and latitude values.
CITIES = [
    ('Helsinki', (24.9342, 60.1756)),
    ('Oulu', (25.4719, 65.0142)),
    ('Jyväskylä', (25.7333, 62.2333)),
    ('Kuopio', (27.6783, 62.8925)),
    ('Lahti', (25.655, 60.9804)),
    ('Kouvola', (26.7042, 60.8681)),
    ('Pori', (21.7972, 61.4847)),
    ('Joensuu', (29.7639, 62.6)),
    ('Lappeenranta', (28.1861, 61.0583)),
    ('Hämeenlinna', (24.4414, 61)),
    ('Vaasa', (21.6167, 63.1)),
    ('Rovaniemi', (25.7285, 66.5028)),
    ('Seinäjoki', (22.8403, 62.7903)),
    ('Mikkeli', (27.2736, 61.6875)),
    ('Kokkola', (23.132, 63.8376)),
    ('Kajaani', (27.7333, 64.225)),
]
OSM_SERVICE_URL = "https://routing.openstreetmap.de/routed-car/route/v1/driving/{},{};{},{}?overview=false&geometries=geojson&steps=true&continue_straight=true"


class Truck:
    route = None
    distance = 0
    distance_traveled = 0
    start_city = ''
    destination_city = ''
    start_point = (0,0)
    destination_point = (0,0)
    last_updated = None  
    
    def __init__(self, name, speed=None) -> None:
        self.name = name
        if speed:
            self.speed = speed
        else:
            self.speed = random.randint(1000, 2000)

    def update(self) -> dict:
        """
        Update the position of the truck based on the time ELAPSED
        """
        if not self.destination_city:
            # We're starting a new delivery.
            self.get_route()
            self.log("Started route from {0} to {1}".format(self.start_city, self.destination_city))

        now = datetime.datetime.now()
        if self.last_updated:
            delta = now - self.last_updated
            self.distance_traveled += float(delta.seconds) / 60 / 60 * self.speed * 1000
        self.last_updated = now

        if self.distance_traveled >= self.distance:
            lon, lat = self.destination_point
            self.log("Reached destination {0}".format(self.destination_city))
            # We've reaced the destination start a new route on enxt update.
            self.start_city, self.start_point = self.destination_city, self.destination_point
            self.destination_city = None
            self.distance_traveled = 0
            eta = now
        else:
            current_point = self.route.interpolate(self.distance_traveled / self.distance, normalized=True)
            lon, lat = current_point.x, current_point.y
            eta_seconds = (self.distance - self.distance_traveled) / self.speed
            eta = now + datetime.timedelta(seconds=eta_seconds)
            self.log("Driving at position {0}, {1}. Distance traveled: {2}".format(lat, lon, self.distance_traveled))

        return {
            "start_city": self.start_city,
            "destination_city": self.destination_city,
            "dinstance": self.distance - self.distance_traveled,
            "longitude": lon,
            "latitude": lat,
            "eta": eta.strftime("%m/%d/%Y, %H:%M")
        }


    def get_route(self) -> list:
        """
        Get a random route between the cities. If start city already exists. Start from that positition.
        """
        if self.start_city:
            while self.start_city == self.destination_city or self.destination_city is None:
                self.destination_city, self.destination_point = random.choice(CITIES)
        else:
            (self.start_city, self.start_point), (self.destination_city, self.destination_point) = random.sample(CITIES, 2)

        r = requests.get(
            OSM_SERVICE_URL.format(
                self.start_point[0], self.start_point[1],
                self.destination_point[0], self.destination_point[1]
                )
        )
        data = r.json()
        # Gather all the geometries of the route to construct one single linestring
        self.distance = data['routes'][0]['distance']
        # Gather the geojson geometries from json and turn them to shapely objects.
        geometries = [shape(step['geometry']) for step in data['routes'][0]['legs'][0]['steps']]
        self.route = linemerge(geometries)

    def log(self, message):
        print("{0}: {1}".format(self.name, message))
