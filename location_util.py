from geopy.geocoders import Nominatim


class Location:
    def __init__(self, latitude: float, longitude: float, full_address: str):
        self.latitude = latitude
        self.longitude = longitude
        self.full_address = full_address

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) {self.full_address}"


def get_location_from_string(place: str) -> Location:
    geolocator = Nominatim(user_agent="MyApp")

    location = geolocator.geocode(place)

    return Location(
        latitude=location.latitude,
        longitude=location.longitude,
        full_address=str(location)
    )


if __name__ == "__main__":
    print(get_location_from_string("Sint-andreaslyceum Sint-kruis"))
