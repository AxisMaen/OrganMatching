import requests

#https://docs.mapbox.com/api/navigation/#matrix
def doRequest():
    
    base_path = "https://api.mapbox.com"
    endpoint = "/directions-matrix/v1/"
    profile = "mapbox/driving/"
    coords = "-122.42,37.78;-122.45,37.91"
    access_token = "access_token=pk.eyJ1IjoiYXhpczE3IiwiYSI6ImNrZnh5eHd5cDI2ZHAycW84bncya3A4YncifQ.wDVnZ5-pJ6iAayFHDrOUCQ"

    request_url = base_path + endpoint + profile + coords + "?" + access_token

    response = requests.get(request_url)
    json_data = response.json()

    if(json_data["code"] != "Ok"):
        raise Exception("Bad response from Mapbox")

    #see https://docs.mapbox.com/api/navigation/#response-retrieve-a-matrix for the response format

    return json_data
