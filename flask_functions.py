from flask import Flask, jsonify, request
import csv
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
    matching, hospital_dict = model.main() #runs the matching model
    fixed_matching = {}
    entries = []
    
    for key in matching:
        key_name, key_age, key_index, key_organ = key.split("_")
        val_name, val_age, val_index, val_organ = matching[key].split("_")
        
        key_index = int(key_index)
        val_index = int(val_index)
        
        if(key_index not in hospital_dict.keys() or val_index not in hospital_dict[key_index].keys()):
            eta = hospital_dict[val_index][key_index]
        else:
            eta = hospital_dict[key_index][val_index]
        
        
        with open('hospitals_coordinates.csv') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader) #skip first row (header)
            
            #get coords for each hospital index
            hospital_coords = []
            for row in reader:
                hospital_coords.append(row[2])
            
            entries.append({'donor_name' : key_name,
                        'donor_age' : key_age,
                        'donor_index' : str(key_index),
                        'donor_organ' : key_organ,
                        'recipient_name' : val_name,
                        'recipient_age' : val_age,
                        'recipient_index' : str(val_index),
                        'recipient_organ' : val_organ,
                        'eta' : eta,
                        'donor_coords' : hospital_coords[key_index],
                        'recipient_coords' : hospital_coords[val_index]})
        
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
    
    name.replace(" ", "")
    
    with open('output.csv') as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            if(row == []):
                continue
            if(name in row[0].replace(" ", "") and organ in row[0]):
                return jsonify(row)
                           
        return("No Pair Found")

if __name__ == '__main__':
    app.run(debug=True, port=8080, use_reloader=False)
