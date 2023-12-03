import matplotlib.pyplot as plt
import pickle
import networkx as nx

#Properties of a node
#id, branched, move number, type, orientationonpad

map = nx.Graph()

mapgraphfile = open(r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\Phase 2\drone1.txt", "rb")
map = pickle.load(mapgraphfile)

subax1 = plt.subplot(221)  
nx.draw(map, with_labels = True, font_weight='bold')
plt.show()

