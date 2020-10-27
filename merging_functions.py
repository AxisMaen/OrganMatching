from coordinate_functions import get_coordinates_from_address
from bipartite_mapbox import doRequest
import os.path
import pandas as pd
import networkx as nx
import numpy as np
from bipartite_distance_matching import maximum_bipartite_matching_distance_optimization


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


def get_compatible_recipients(G, donors, recipients, child_age, hospital_distance_matrix):
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
    hospital_dict = {new_list: set([]) for new_list in range(len(hospital_distance_matrix[0]))}
    for index, donor_row in donors.iterrows():
        donor_age = donor_row['age']
        # get recipients with same blood group and organ as donor
        possible_recipients = recipients[(recipients['blood_group'] == donor_row['blood_group']) & (donor_row['organ'] == recipients['organ'])]
        # remove children from list of recipients if donor is not a kid
        if donor_age > child_age:
            possible_recipients = recipients[recipients['age'] > child_age]
        else:
            possible_recipients = recipients[recipients['age'] <= child_age]
        # Fill in various entries
        donor_hospital = donor_row['hospital']
        recipient_hospitals = set(possible_recipients['hospital'])
        donor_name = donor_row['node_name']
        # Add placeholder edges between donor and recipients with dummy edgges.
        G.add_nodes_from([donor_row['node_name']], bipartite=0)
        possible_recipients_names = list(possible_recipients['node_name'])
        G.add_nodes_from(possible_recipients_names, bipartite=1)
        G.add_weighted_edges_from([(donor_name, recipient_name, -1) for recipient_name in possible_recipients_names])
        # Update hospital dict
        hospital_dict[donor_hospital] = hospital_dict[donor_hospital].union(set(possible_recipients['hospital']))

    return G, hospital_dict


def query_distance_between_hospitals(hospital_dict, hospitals):
    """
    Wraps data for query to mapbox for distances between hospitals
    :param hospital_dict: dictionary with sources and destinations
    :param hospitals: dataframe of hospitals
    :return: updated hospital dictionary
    """
    for source_hospital, destination_hospitals in hospital_dict.items():
        source_coordinates = hospitals[hospitals['token'] == source_hospital]['coordinates'].tolist()[0]
        print("Source coordinates is", source_coordinates)
        destination_coordinates = list(hospitals[hospitals['token'].isin(destination_hospitals)]['coordinates'])
        print(destination_coordinates)
        # print("Source coordinates is ", source_coordinates)
        # print("Destination coordinates is ", destination_coordinates)
        times = doRequest(source_coordinates, destination_coordinates)
        hospital_dict[source_hospital] = list(times)
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
    return hospital_dict[donors['node_name'==edge[0]]['hospital']][recipients['node_name'==edge[1]]['hospital']]


def main():
    """
    Runs the entire merged model together
    :return:
    """
    donors, recipients, hospitals = read_data()
    # Hospital distances stored as a matrix
    hospital_distance_matrix = np.full((len(hospitals), len(hospitals)), 0)
    # init graph
    G = nx.Graph()
    #Get all compatible recipients for each donor
    G, hospital_dict = get_compatible_recipients(G, donors, recipients, 15, hospital_distance_matrix)
    print(hospital_dict)
    # Query mapbox using matt's function for distances between relevant hospitals
    hospital_dict = query_distance_between_hospitals(hospital_dict, hospitals)
    # Add the times into the edges
    G = update_edges(G, hospital_dict, donors, recipients)
    # Run optimization model
    matching = maximum_bipartite_matching_distance_optimization(G)
    print(matching)
    return


if __name__ == '__main__':
    main()
