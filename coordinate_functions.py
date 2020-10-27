from geopy.geocoders import Nominatim, MapBox, Bing


class AddressNotFoundError(Exception):
    """
    Raised when coordinates are not converted to exceptions
    """

    def __init__(self, address, message='could not be converted to coordinates'):
        self.address = address
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.address} {self.message}'


def get_coordinates_from_address(address):
    """
    Given an address returns a tuple of coordinates
    :param address: String of address
    :return: 2d tuple of coordinates
    """
    geolocator = Nominatim(user_agent="vivek")
    location = geolocator.geocode(address)
    if location is None:
        geolocator2 = MapBox(api_key="pk.eyJ1Ijoidml2ZGFkZHkiLCJhIjoiY2tnbGtlNDFrMDJubTJ0cDd4NDZqeXBnMyJ9.WmwEq6ufsk_KqQXcXfqRFw")
        location = geolocator2.geocode(address)
        if location is None:
            geolocator3 = Bing(api_key="AvNtmAt-6__O9J46nHtt2Py7bOgu8geabz5yOB_zxCn0Nq51Y085O-m_4hw_4Cik")
            location = geolocator3.geocode(address)
            if location is None:
                raise AddressNotFoundError(address)
    return str(location.longitude) + ',' + str(location.latitude)


def get_address_from_coordinates(coordinates):
    """
    Given coordinates returns addresgs of location
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