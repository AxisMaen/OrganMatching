## Installation

Ensure that Python is install on your system. You can download Python here.
https://www.python.org/downloads/

To verify that Python is installed, open your command prompt or terminal and type "python" (no quotes). If you encounter an error, Python is not correctly installed.

This program depends on GEKKO Optimization Suite and NetworkX. This can be installed by typing "pip install gekko" and "pip install networkx".  

To view the Python files themselves, almost any text editor or Python IDE can be used. PyCharm is usually a popular one. https://www.jetbrains.com/pycharm/  

## How To Use

To run the organ matching program, download it from the Github repository and place it anywhere on your computer.
Open command prompt in location of the OrganMatching folder (you can use cd "filepath" to change the directory the command prompt is in).
Once in the correct directory, the program can be run by typing in the format "python bipartite_matching_allocation.py -p p1 p2 -o o1 o2 -e p1 o1 -e p2 o2"

Arguments:  
-p: The names of the people nodes. For example, "-p p1 p2 p3" creates 3 people nodes, but each node can be named anything you want (no duplicates).  
-o: The names of the organ nodes. Follows a similar format to the people nodes.  
-e: Creates an edge between people and organs. Each -e creates a single edge only and takes two arguments where the first is a person node and the second is an organ node.  
For example, to create two edges you would type "-e p1 o1 -e p2 o2".
