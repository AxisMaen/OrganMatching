from geopy.geocoders import Nominatim


def get_coordinates_from_address(address):
    """
    Given an address returns a tuple of coordinates
    :param address: String of address
    :return: 2d tuple of coordinates
    """
    geolocator = Nominatim(user_agent="vivek")
    location = geolocator.geocode(address)
    return location.latitude, location.longitude


def get_address_from_coordinates(coordinates):
    """
    Given coordinates returns address of location
    :param coordinates: 2d tuple of coordinates
    :return: Address
    """
    geolocator = Nominatim(user_agent="vivek")
    location = geolocator.reverse(coordinates)
    return location.address


def test():
    address = "265 Blue Course Drive State College PA"
    coordinates = get_coordinates_from_address(address)
    print(coordinates)
    print(get_address_from_coordinates((13.055644, 80.235491)))
    return


def main():
    test()
    return


if __name__=="__main__":
    main()