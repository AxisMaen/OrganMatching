import os
from gekko import GEKKO
import networkx as nx


def main():
    print("Vivek")
    return


def maximum_bipartite_matching_optimization(G):
    """
    Performs LP optimization solving the maximum bipartite matching problem
    :param G: Bipartite Networkx graph G
    :return: dictionary of matching where key is node, value is node in other set
    """

    model = GEKKO()
    variable_dict = {}
    intermediates = [None] * len(G.nodes)
    for node in list(G.nodes):
        neighbors = list(G.neighbors(node))
        print("Node is ", node)
        print("Neighbors are ", neighbors)
        for neighbor in neighbors:
            # make variables
            # lower bound 0 upper bound 1
            variable_dict[(node, neighbor)] = model.Var(lb=0, ub=1, integer=True)

        tuples = [(node, i) for i in neighbors]

        # Constraint that no node can be in matching twice
        model.Equation(sum([variable_dict[tup] for tup in tuples]) <= 1)

    for variable in variable_dict:
        print(variable, tuple(reversed(variable)))
        model.Equation(variable_dict[variable] == variable_dict[tuple(reversed(variable))])

    # Objective
    model.Obj(-1 * sum([variable_dict[variable] for variable in variable_dict]))

    # Integer Solver
    model.options.SOLVER = 1

    # Solve
    model.solve()

    matching = {}
    # Add variables to matching
    for variable in variable_dict.items():
        print(variable)
        if int(variable[1][0]) == 1:
            matching[variable[0][0]] = variable[0][1]
    return matching


if __name__ == "__main__":
    G = nx.Graph()
    G.add_edges_from([(0, 3), (0, 6), (1, 3), (1, 4), (2, 4), (2, 5)])
    matching_opt = maximum_bipartite_matching_optimization(G)
    print(matching_opt)
    matching_hk = nx.bipartite.hopcroft_karp_matching(G)
    print(matching_hk)