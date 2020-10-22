import requests

#https://docs.mapbox.com/api/navigation/#matrix

#inputs are strings in the form latitude,longtitude (no spaces)
def doRequest(source_coord, dest_coord):
    
    base_path = "https://api.mapbox.com"
    endpoint = "/directions/v5/"
    profile = "mapbox/driving-traffic/"
    #coords = "-122.42,37.78;-122.45,37.91"
    coords = source_coord + ";" + dest_coord
    access_token = "access_token=pk.eyJ1IjoiYXhpczE3IiwiYSI6ImNrZnh5eHd5cDI2ZHAycW84bncya3A4YncifQ.wDVnZ5-pJ6iAayFHDrOUCQ"

    request_url = base_path + endpoint + profile + coords + "?" + access_token

    response = requests.get(request_url)
    json_data = response.json()

    if(json_data["code"] != "Ok"):
        raise Exception("Bad response from Mapbox")

    #see https://docs.mapbox.com/api/navigation/#response-retrieve-a-matrix for the response format
    
    print(json_data["routes"][0]["duration"]) #most optimal time
    return json_data
