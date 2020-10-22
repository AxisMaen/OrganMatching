from coordinate_functions import get_coordinates_from_address


def make_sources_destinations(donor, G, mappings):
    recipients = list(G.neighbors(donor))
    donor_coordinates = get_coordinates_from_address(mappings[donor])
    recipient_coordinates = [get_coordinates_from_address(mappings[recipient]) for recipient in recipients]
    return donor_coordinates, recipient_coordinates

