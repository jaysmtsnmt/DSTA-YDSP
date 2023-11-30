from djitellopy import Tello
from djitellopy import TelloSwarm
import networkx as nx
import pickle
import matplotlib.pyplot as plt

MAPGRAPHPATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapgraph.txt"
MAPDATAPATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapdata.txt"

map = nx.Graph()
mapfile = open(MAPGRAPHPATH, "rb")
map = pickle.load(mapfile)

subax1 = plt.subplot(221)  
nx.draw(map, with_labels = True, font_weight='bold')
plt.show()

dataBL = nx.get_node_attributes(map, "bl")
dataBR = nx.get_node_attributes(map, "br")


        





