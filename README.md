## Installation

Ensure that Python is install on your system. You can download Python here.
https://www.python.org/downloads/

To verify that Python is installed, open your command prompt or terminal and type "python" (no quotes). If you encounter an error, Python is not correctly installed.

This program depends on GEKKO Optimization Suite and NetworkX. This can be installed by typing "pip install gekko" and "pip install networkx".  

To view the Python files themselves, almost any text editor or Python IDE can be used. PyCharm is usually a popular one. https://www.jetbrains.com/pycharm/  

## How To Use

To run the organ matching program, download it from the Github repository and place it anywhere on your computer.
Open command prompt in location of the OrganMatching folder (you can use cd "filepath" to change the directory the command prompt is in).
Once in the correct directory, the program can be run by typing in the format "python bipartite_distance_matching.py -p <people> -o <organs> -e <edge>".  
For example, "python bipartite_distance_matching.py -p p1 p2 -o o1 o2 -e o1 p1 2 -e o2 p2 3".  


Arguments:  
-p: The names of the people nodes. For example, "-p p1 p2 p3" creates 3 people nodes, but each node can be named anything you want (no duplicates).  
-o: The names of the organ nodes. Follows a similar format to the people nodes.  
-e: Creates a weighted edge between people and organs. Each -e creates a single edge only and takes three arguments where the first is a node, the second is another node, and the third is the weight as an integer. 
You can put a person node followed by an organ node or vice versa as the first two arguments, but the order MUST be consistent across all edges. Additionally, you can not have two nodes of the same type for a single edge.    

For example, to create two edges with weights 2 and 3, you would type "-e o1 p1 2 -e o2 p2 3" or "-e p1 o1 2 -e p2 o2 3" for the same result.
  