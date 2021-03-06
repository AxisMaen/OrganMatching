from gekko import GEKKO
import networkx as nx


def maximum_bipartite_matching_optimization(G):
    """
    Performs LP optimization solving the maximum bipartite matching problem
    :param G: Bipartite Networkx graph G, need to specify which set each nodes by additional option
            EG: G = nx.Graph()
                # People
                G.add_nodes_from(['p' + str(i) for i in range(4)], bipartite=0) # Specifying that nodes in set 0
                # Organs
                G.add_nodes_from(['o' + str(i) for i in range(4)], bipartite=1) # Specifying that nodes in set 1
                # Edges
                G.add_edges_from([('p0', 'o0'), ('p1', 'o1'), ('p2', 'o1'), ('p2', 'o2')])

    :return: dictionary of matching where key is node, value is node in other set, it contains (a,b) and (b,a)
    """
    # remove nodes with no edges as it messes up bipartite splitter
    left_set = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
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

        tuples = [(node, i) for i in neighbors]
        # print(tuples)
        # Constraint that no node can be in matching twice
        if len(tuples) > 0:
            model.Equation(sum([variable_dict[tup] for tup in tuples]) <= 1.0)

    # Objective
    model.Obj(-1 * sum([variable_dict[variable] for variable in variable_dict]))

    # Integer Solver
    model.options.SOLVER = 1

    # Solve
    model.solve(disp=True)

    matching = {}
    # Add variables to matching
    for variable in variable_dict.items():
        print(variable)
        if int(variable[1][0]) == 1:
            matching[variable[0][0]] = variable[0][1]
            matching[variable[0][1]] = variable[0][0]
    return matching


if __name__ == "__main__":
    G = nx.Graph()
    
    # People
    name_input = input("Enter names of people nodes seperated by commas: ")
    G.add_nodes_from(list(name_input.replace(" ", "").split(",")), bipartite=0)
    #G.add_nodes_from(['p' + str(i) for i in range(4)], bipartite=0)
    
    # Organs
    organ_input = input("Enter organ nodes seperated by commas: ")
    G.add_nodes_from(list(organ_input.replace(" ", "").split(",")), bipartite=1)
    #G.add_nodes_from(['o' + str(i) for i in range(4)], bipartite=1)
    
    # Edges
    edges_input = input("Enter the first edge in the format person, organ: ")
    edges_list = [tuple(edges_input.replace(" ", "").split(","))]
    while(edges_input != 'done'):
        edges_input = input("Enter the next edge in the format person, organ (type \"done\" when done): ")
        if(edges_input != 'done'):
            edges_list.append(tuple(edges_input.replace(" ", "").split(",")))

    G.add_edges_from(edges_list)
    #G.add_edges_from([('p0', 'o0'), ('p1', 'o1'), ('p2', 'o1'), ('p2', 'o2')])
    
    matching_opt = maximum_bipartite_matching_optimization(G)
    print(matching_opt)
    matching_hk = nx.bipartite.hopcroft_karp_matching(G, top_nodes=[n for n in G.nodes if G.nodes[n]['bipartite'] == 0])
    print(matching_hk)