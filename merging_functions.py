from coordinate_functions import get_coordinates_from_address
from bipartite_mapbox import doRequest
import os.path
import pandas as pd
import networkx as nx
import pickle
import numpy as np
from bipartite_distance_matching import maximum_bipartite_matching_distance_optimization
import csv

def read_data():
    """
    reads data from csv files for donor, recipient and hospital data
    :return: pandas df for donors, recipients, hospitals
    """
    donors = pd.read_csv('donor_data.csv')
    cols = ['name', 'age', 'hospital', 'organ']
    donors['node_name'] = donors[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    recipients = pd.read_csv('recipient_data.csv')
    recipients['node_name'] = recipients[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    if not os.path.isfile("hospitals_coordinates.csv"):
        hospitals = pd.read_csv('hospital.csv')
        hospitals['coordinates'] = hospitals['address'].map(get_coordinates_from_address)
        # print(get_coordinates_from_address(hospitals['address'][4]))
        hospitals['token'] = range(0, len(hospitals))
        hospitals.to_csv("hospitals_coordinates.csv", index=False)
    else:
        hospitals = pd.read_csv('hospitals_coordinates.csv')
    return donors, recipients, hospitals


def get_compatible_recipients(G, donors, recipients, child_age, num_hospitals):
    """
    Gets the compatible recipients for each donor. Also adds placeholder edges to graph.
    :param G: Initialized Bipartite G
    :param donors: dataframe with donors
    :param recipients: dataframe with recipients
    :param child_age: age to determine if child or not
    :param hospital_distance_matrix: initialized matrix for distances between hospitals
    :return: updated G, hospital dict with destinations to query
    """
    # initialize dictionary with various hospitals
    hospital_dict = {new_list: set([]) for new_list in range(num_hospitals)}
    for index, donor_row in donors.iterrows():
        donor_age = donor_row['age']
        # get recipients with same blood group and organ as donor
        possible_recipients = recipients[(recipients['blood_group'] == donor_row['blood_group']) & (donor_row['organ'] == recipients['organ'])]
        # remove children from list of recipients if donor is not a kid
        if donor_age > child_age:
            possible_recipients = possible_recipients[possible_recipients['age'] > child_age]
        else:
            possible_recipients = possible_recipients[possible_recipients['age'] <= child_age]
        # Fill in various entries
        donor_hospital = donor_row['hospital']
        recipient_hospitals = set(possible_recipients['hospital'])
        donor_name = donor_row['node_name']
        # Add placeholder edges between donor and recipients with dummy edgges.
        G.add_nodes_from([donor_name], bipartite=0)
        possible_recipients_names = possible_recipients['node_name'].tolist()
        G.add_nodes_from(possible_recipients_names, bipartite=1)
        # print("Possible recipients are ", possible_recipients_names)
        G.add_weighted_edges_from([(donor_name, recipient_name, -1) for recipient_name in possible_recipients_names])
        # Update hospital dict
        hospital_dict[donor_hospital] = hospital_dict[donor_hospital].union(set(possible_recipients['hospital']))

    return G, hospital_dict


def query_distance_between_hospitals(hospital_dict,  hospitals, query=False):
    """
    Wraps data for query to mapbox for distances between hospitals
    :param hospital_dict: dictionary with sources and destinations
    :param hospitals: dataframe of hospitals
    :param query: boolean to indicate whether to query mapbox or not. If it doesn't it uses a cached version obtained
                previous query in pickle file.
    :return: updated hospital dictionary
    """
    if query:
        for source_hospital, destination_hospitals in hospital_dict.items():
            hospital_dict[source_hospital] = sorted(list(hospital_dict[source_hospital]))
            source_coordinates = hospitals[hospitals['token'] == source_hospital]['coordinates'].tolist()[0]
            destination_coordinates = list(hospitals[hospitals['token'].isin(destination_hospitals)]['coordinates'])
            # print("Source coordinates is ", source_coordinates)
            # print("Destination coordinates is ", destination_coordinates)
            times = doRequest(source_coordinates, destination_coordinates)
            hospital_dict[source_hospital] = {destination: distance for destination, distance in zip(hospital_dict[source_hospital], times)}
        with open("hospital_dict.pickle", 'wb') as f:
            pickle.dump(hospital_dict, f)
    else:
        with open("hospital_dict.pickle", 'rb') as f:
            hospital_dict = pickle.load(f)
    return hospital_dict


def update_edges(G, hospital_dict, donors, recipients):
    """
    Updates edges in G after querying mapbox
    :param G: bipartite graph
    :param hospital_dict: dictionary with sources and destinations
    :param donors: dataframe of donors
    :param recipients: dataframe of recipients
    :return: updated G
    """
    edges = G.edges.data("weight", default=1)
    # print("edges are ", edges)
    G.add_weighted_edges_from([(edge[0], edge[1], get_weight(donors, recipients, hospital_dict, edge)) for edge in edges])
    return G


def get_weight(donors, recipients, hospital_dict, edge):
    """
    Gets the time to go between hospitals as queried by mapbox
    :param donors: donors extracted by read_data() it is a pandas dataframe
    :param recipients: recipients extracted by read_data() it is a pandas dataframe
    :param hospital_dict: dictionary for destinations queried from each hospital by mapbox
    :param edge: each edge in the Graph
    :return: float
    """
    # print(hospital_dict)
    # print(donors)
    donor = donors[donors['node_name'] == edge[0]]
    # print(donors)
    # print("donor: ", donor)
    # print("edge is", edge)
    # print(donor.empty)
    if donor.empty:
        donor = recipients[recipients['node_name'] == edge[0]]
        recipient = donors[donors['node_name'] == edge[1]]
        # print("donor is ", donor)
        # print("recipient is ", recipient)
        return hospital_dict[recipient.iloc[0]['hospital']][donor.iloc[0]['hospital']]
    else:
        recipient = recipients[recipients['node_name'] == edge[1]]
        # print("donor is ", donor)
        # print("recipient is ", recipient)
        return hospital_dict[donor.iloc[0]['hospital']][recipient.iloc[0]['hospital']]


def main():
    """
    Runs the entire merged model together
    :return:
    """
    print("Reading data")
    donors, recipients, hospitals = read_data()
    # init graph
    G = nx.Graph()
    # Get all compatible recipients for each donor
    print("Getting potential recipients")
    G, hospital_dict = get_compatible_recipients(G, donors, recipients, 15, len(hospitals))
    # Query mapbox using matt's function for distances between relevant hospitals
    print("Querying mapbox")
    hospital_dict = query_distance_between_hospitals(hospital_dict, hospitals, query=True)
    # Add the times into the edges
    print("G edges are ", G.edges.data("weight", default=1))
    print("Updating Graph with times")
    G = update_edges(G, hospital_dict, donors, recipients)
    # Run optimization model
    print("Running optimization model")
    matching = maximum_bipartite_matching_distance_optimization(G)
    print("Matching is \n",matching)
    w = csv.writer(open("output.csv", "w+"))
    for key, val in matching.items():
        w.writerow([key, val])
    return


if __name__ == '__main__':
    main()
