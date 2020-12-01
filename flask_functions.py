from flask import Flask, jsonify, request
import csv
import pickle
import merging_functions as model


app = Flask(__name__)


'''
This version returns a dictionary with one key (hospitals).
The value at this key is a list where each entry is a dictionary (1 per hospital).
This subdictionary has name and value keys.
'''
@app.route('/hospitals', methods=['GET'])
def getHospitals():
    
    hospitals = {}
    entries = []
    
    with open('hospital.csv') as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            entries.append({'name' : row[0], 'address' : row[1]})
        
    
    hospitals['hospitals'] = entries
    return jsonify(hospitals)


'''
This is an alternate version since I wasn't sure which was better.
This version returns a dictionary where each key is the name of the hospital
and the value is a dictionary with an address key
'''
'''
@app.route('/hospitals', methods=['GET'])
def getHospitals():
    
    hospitals = {}
    
    with open('hospital.csv') as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            hospitals[row[0]] = {'Address' : row[1]}
        
    return jsonify(hospitals)
'''

'''
Returns a dictionary with one key (organs).
The value at this key is a list where each entry is a dictionary (1 per organ).
This subdictionary has name and value keys.
'''
@app.route('/organs', methods=['GET'])
def getOrgans():
    
    organs = {}
    entries = []
    added_organs = []
    
    with open('donor_data.csv') as file:
        reader = csv.reader(file, delimiter=',')
        next(reader) #skip first row (header)
        
        for row in reader:
            if(row[7] not in added_organs):
                added_organs.append(row[7])
                entries.append({'name' : row[7]})        
    
    organs['organs'] = entries
    return jsonify(organs)

'''
Returns a dictionary with one key (patients).
The value at this key is a list where each entry is a dictionary (1 per patient).
This subdictionary has name and value keys.
'''
@app.route('/patients', methods=['GET'])
def getPatients():
    
    organs = {}
    entries = []
    added_patients = []
    
    with open('donor_data.csv') as file:
        reader = csv.reader(file, delimiter=',')
        next(reader) #skip first row (header)
        
        for row in reader:
            if(row[0] not in added_patients):
                added_patients.append(row[0])
                entries.append({'name' : row[0],
                                'sex' : row[1],
                                'age' : row[2],
                                'blood_group' : row[3],
                                'weight' : row[4],
                                'height' : row[5]})        
    
    organs['patients'] = entries
    return jsonify(organs)

'''
Returns the full matching for all patients.
This function may take a few seconds to run, as it runs the
matching model rather than pulling from a file.
The updated matching is saved to output.csv.
'''
@app.route('/update', methods=['GET'])
def updateMatching():
    matching = model.main() #runs the matching model
    fixed_matching = {}
    entries = []
    
    hospital_dict = {}
    
    with open('hospital_dict.pickle', 'rb') as file:
        hospital_dict = pickle.load(file)
    
    for key in matching:
        donor_name, donor_age, donor_index, donor_organ = key.split("_")
        recipient_name, recipient_age, recipient_index, recipient_organ = matching[key].split("_")
        
        donor_index = int(donor_index)
        recipient_index = int(recipient_index)
            
        eta = getETA(donor_index, recipient_index)              
        hospital_coords = getHospitalCoords()
            
        entries.append({'donor_name' : donor_name,
                        'donor_age' : donor_age,
                        'donor_index' : str(donor_index),
                        'donor_organ' : donor_organ,
                        "donor_hospital" : getHospitalName(donor_index),
                        'recipient_name' : recipient_name,
                        'recipient_age' : recipient_age,
                        'recipient_index' : str(recipient_index),
                        'recipient_organ' : recipient_organ,
                        'eta' : eta,
                        'donor_coords' : hospital_coords[donor_index],
                        'recipient_coords' : hospital_coords[recipient_index],
                        "recipient_hospital" : getHospitalName(recipient_index)
                        })
        
    fixed_matching['matchings'] = entries
    
    return jsonify(fixed_matching)

'''
Given a recipient's name and organ, returns a pairing.
This function is fast and does not get a live update from the matching.
If the nodes in the model were changed and an update was not run, the
returned pair could be incorrect.

Remove the space between first and last name when calling.
Ex: http://127.0.0.1:8080/matching/JackNicholson/Cornea

If no pairing is found, 'No Pair Found' is returned.
'''
@app.route('/matching/<string:name>/<string:organ>')
def getMatch(name, organ):
    pair = {}
    
    name.replace(" ", "")
    
    with open('output.csv') as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            if(row == []):
                continue
            if(name in row[0].replace(" ", "") and organ in row[0]):
                recipient_name, recipient_age, recipient_index, recipient_organ = row[0].split("_")
                donor_name, donor_age, donor_index, donor_organ = row[1].split("_")
                
                donor_index = int(donor_index)
                recipient_index = int(recipient_index)
                
                hospital_coords = getHospitalCoords()
                
                entry = [{"donor_age" : donor_age,
                          "donor_coords" : hospital_coords[donor_index],
                          "donor_index" : donor_index,
                          "donor_name" : donor_name,
                          "donor_organ" : donor_organ,
                          "donor_hospital" : getHospitalName(donor_index),
                          "eta" : getETA(donor_index, recipient_index),
                          "recipient_age" : recipient_age,
                          "recipient_coords" : hospital_coords[recipient_index],
                          "recipient_index" : recipient_index,
                          "recipient_name" : recipient_name,
                          "recipient_organ" : recipient_organ,
                          "recipient_hospital" : getHospitalName(recipient_index)
                          }]
                
                pair["matching"] = entry
                
                return jsonify(pair)
                           
        return("No Pair Found")

'''
Helper function that returns dictionary of hospital coordinates
The ith position of the returned array contains the coords for
the hospital with index i.
'''
def getHospitalCoords():
    with open('hospitals_coordinates.csv') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader) #skip first row (header)
            
            #get coords for each hospital index
            hospital_coords = []
            for row in reader:
                hospital_coords.append(row[2])
            
            return hospital_coords
'''
Helper function that returns string with hospital name
given the index of the hospital.
'''       
def getHospitalName(index):
    with open('hospitals_coordinates.csv') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader) #skip first row (header)
            
            current_index = 0
            for row in reader:
                if(index == current_index):
                    return row[0]
                current_index = current_index + 1

'''
Helper function that returns the ETA between two hospital indices (ints).
The result is from the saved hospital_dict.pickle file that is saved
when a matching update is run. There could potentially be a more optimal
ETA if there has not been an update recently.
'''
def getETA(source_index, dest_index):
    with open('hospital_dict.pickle', 'rb') as file:
        hospital_dict = pickle.load(file)
        
        if(source_index not in hospital_dict.keys() or dest_index not in hospital_dict[source_index].keys()):
            eta = hospital_dict[dest_index][source_index]
        else:
            eta = hospital_dict[source_index][dest_index]
        
        return eta
    

if __name__ == '__main__':
    app.run(debug=True, port=8080, use_reloader=False)
