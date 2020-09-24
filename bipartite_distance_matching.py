from gekko import GEKKO
import networkx as nx
import argparse


def maximum_bipartite_matching_distance_optimization(G):
    """
    Performs LP optimization solving the maximum bipartite matching problem
    :param G: Bipartite Networkx graph G, need to specify which set each nodes by additional option
            EG: G = nx.Graph()
                G.add_nodes_from(['o' + str(i) for i in range(5)], bipartite=0)
                G.add_nodes_from(['p' + str(i) for i in range(4)], bipartite=1)
                G.add_weighted_edges_from([('o0', 'p0', 1), ('o0', 'p1', 2), ('o1', 'p1', 3), ('o1', 'p2', 6), ('o2', 'p2', 5),
                               ('o3', 'p3', 4), ('o4', 'p3', 6)])
                First term in tuple is node in left set, 2nd term is node in right set, third term is weight of edge
    matching_opt = maximum_bipartite_matching_distance_optimization(G)

    :return: dictionary of matching where key is node, value is node in other set, it contains (a,b) and (b,a)
    """
    # remove nodes with no edges as it messes up bipartite splitter
    left_set = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
    right_set = [n for n in G.nodes if G.nodes[n]['bipartite'] == 1]
    # print("leftset ", left_set)
    # print("rightset ", right_set)
    S = get_S(G)
    model = GEKKO()
    variable_dict = {}
    for node in left_set:
        neighbors = list(G.neighbors(node))
        # print("Node is ", node)
        # print("Neighbors are ", neighbors)
        for neighbor in neighbors:
            # make variables
            # lower bound 0 upper bound 1
            variable_dict[(node, neighbor)] = model.Var(lb=0, ub=1, integer=True)
            variable_dict[(neighbor, node)] = model.Var(lb=0, ub=1, integer=True)
            model.Equation(variable_dict[(node, neighbor)] - variable_dict[(neighbor, node)] == 0)

        tuples = [(node, i) for i in neighbors]
        # print(tuples)
        # Constraint that no node can be in matching twice
        if len(tuples) > 0:
            model.Equation(sum([variable_dict[tup] for tup in tuples]) <= 1.0)

    for node in right_set:
        neighbors = list(G.neighbors(node))
        # print("Node is ", node)
        # print("Neighbors are ", neighbors)
        for neighbor in neighbors:
            # make variables
            # lower bound 0 upper bound 1
            variable_dict[(node, neighbor)] = model.Var(lb=0, ub=1, integer=True)
            model.Equation(variable_dict[(node, neighbor)] - variable_dict[(neighbor, node)] == 0)

        tuples = [(node, i) for i in neighbors]
        reversed_tuples = [(i, node) for i in neighbors]
        # print(tuples)
        # Constraint that no node can be in matching twice
        if len(tuples) > 0:
            model.Equation(sum([variable_dict[tup] for tup in tuples]) <= 1.0)


    # Objective (Only mainthing that changes from basic optimization to thing
    model.Obj(-1 * sum([variable_dict[variable] * (S - G.get_edge_data(variable[0], variable[1])['weight'])
                        for variable in variable_dict]))

    # Integer Solver
    model.options.SOLVER = 1

    # Solve
    model.solve(disp=True)

    matching = {}
    # Add variables to matching
    for variable in variable_dict.items():
        print(variable)
        if int(variable[1][0]) == 1:
            # print("Adding ", variable)
            matching[variable[0][0]] = variable[0][1]
            matching[variable[0][1]] = variable[0][0]
            # print("matching is ", matching)
    return matching


def get_S(G):
    """
    Returns the S value or sum of all edge weights
    :param G: Nx bipartite graph
    :return: sum of all edge weights
    """
    S = 0
    for edge in list(G.edges.data("weight", default=1)):
        S += edge[2]
    return S


def test_distance():
    """
    Performs basic test to see if distance is being calculated properly
    :return:
    """
    G = nx.Graph()
    G.add_nodes_from(['o' + str(i) for i in range(5)], bipartite=0)
    G.add_nodes_from(['p' + str(i) for i in range(4)], bipartite=1)
    G.add_weighted_edges_from([('o0', 'p0', 1), ('o0', 'p1', 2), ('o1', 'p1', 3), ('o1', 'p2', 6), ('o2', 'p2', 5),
                               ('o3', 'p3', 4), ('o4', 'p3', 6)])
    matching_opt = maximum_bipartite_matching_distance_optimization(G)
    print(matching_opt)
    matching_hk = nx.bipartite.hopcroft_karp_matching(G, top_nodes=[n for n in G.nodes if G.nodes[n]['bipartite'] == 0])
    print(matching_hk)
    return


#returns True if the given list has duplciates, False otherwise
def checkDuplicates(nodes):
    if len(nodes) == len(set(nodes)):
        return False
    else:
        return True

#returns True if nodes in an edge are not in people/organs, False otherwise
def checkEdges(edges, people, organs):
    for edge in edges:
        if edge[0] not in people or edge[1] not in organs:
            return True
    return False


if __name__ == '__main__':
    test_distance()