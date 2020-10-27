import requests

#coords are strings in the form latitude,longtitude (no spaces)
#takes one source coord and a list of dest coords
#returns a list of times from source coo

#distance between source and dest cannot exceed 10000km

#mapbox coords are (long,lat), should be roughly (-75, 40) +/- 5
#this is BACKWARDS compared to google maps
def doRequest(source_coord, dest_coords):
    
    base_path = "https://api.mapbox.com"
    endpoint = "/directions/v5/"
    profile = "mapbox/driving-traffic/"
    #coords = "-122.42,37.78;-122.45,37.91"  
    access_token = "access_token=pk.eyJ1IjoiYXhpczE3IiwiYSI6ImNrZnh5eHd5cDI2ZHAycW84bncya3A4YncifQ.wDVnZ5-pJ6iAayFHDrOUCQ"
    times = []
    
    for dest_coord in dest_coords:
        coords = source_coord + ";" + dest_coord
        request_url = base_path + endpoint + profile + coords + "?" + access_token
        
        #if source and dest are the same, manually return time of 0
        #mapbox sometimes has errors when using same coords so we have to manually fix
        if(source_coord == dest_coord): 
             times.append("0")
             continue
        
        response = requests.get(request_url)
        json_data = response.json()
        
        if("code" not in json_data.keys() or json_data["code"] != "Ok"):            
            raise Exception(json_data["message"])
        
        times.append(json_data["routes"][0]["duration"]) #most optimal time
        
    return times


#dests = ["-80.20292,40.45993"]
#dests = ["-122.45,37.91", "-122.45,37.91", "-122.45,37.91"]
#print(doRequest("-75.14158870992098,40.0368481", dests))
