import networkx as nx
import pickle
import matplotlib.pyplot as plt

map = nx.Graph()

while True:
    type = input("Add?: ")
    if type == "y":
        previousnode = input("Previous Node: ")
        currentNode = input("Current Node: ")
        
        int(previousnode)
        int(currentNode)
        
        map.add_node(currentNode)
        map.add_edge(previousnode, currentNode)
        
    else:
        mapfile = open(r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\phase2graph.txt", "wb")
        pickle.dump(map, mapfile)
        mapfile.close()
        
        subax1 = plt.subplot(221)  
        nx.draw(map, with_labels = True, font_weight='bold')
        plt.show()
        break
    
        
        
    
