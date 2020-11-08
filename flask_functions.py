from flask import Flask, jsonify, request
import csv
app = Flask(__name__)


'''
This version returns a dictionary with one key (hospitals).
The value at this key is a list where each entry is a dictionary (1 per hospital).
This subdictionary has name and value keys.

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

'''
This is an alternate version since I wasn't sure which was better.
This version returns a dictionary where each key is the name of the hospital
and the value is a dictionary with an address key
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
        
        for row in reader:
            if(row[0] not in added_patients):
                added_patients.append(row[0])
                entries.append({'name' : row[0], 'sex' : row[1], 'age' : row[2], 'blood_group' : row[3], 'weight' : row[4], 'height' : row[5]})        
    
    organs['patients'] = entries
    return jsonify(organs)


if __name__ == '__main__':
    app.run(debug=True, port=8080, use_reloader=False)
