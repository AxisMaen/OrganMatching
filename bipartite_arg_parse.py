import argparse

#returns True if the given list has duplciates, False otherwise
def checkDuplicates(nodes):
    if len(nodes) == len(set(nodes)):
        return False
    else:
        return True

#returns True if nodes in an edge are not in people/organs, False otherwise
def checkEdges(edges, nodes):
    for edge in edges:
        if edge[0] not in nodes or edge[1] not in nodes:
            return True
    return False

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-p', '--people', nargs='+', type=str)
    parser.add_argument ('-o', '--organs', nargs='+', type=str)
    parser.add_argument ('-e', '--edge', nargs=3, action='append', type=str)
    
    
    args = parser.parse_args()
    people = args.people
    organs = args.organs
    edges = args.edge
    
    #args makes a list of lists, convert to list of tuples
    for i in range(len(edges)):
        edges[i][2] = int(edges[i][2])
        edges[i] = tuple(edges[i])
        
    #error checking
    if checkDuplicates(people + organs):
        raise ValueError("Duplicate found in people/organ nodes")
    
    if checkEdges(edges, people + organs):
        raise ValueError("Node in an edge does not exist in people or organ nodes")
        
    return [organs, people, edges]