from colorama import Fore
import networkx as nx
import matplotlib.pyplot as plt

z = {1: {"br": False,
		 "bl": True}}

x = 1
while True:
	
	if x > 12:
		if x > 20:
			break
	
	x += 1
	print(x)
	
print(Fore.RESET + Fore.RED +"breaked"+Fore.RESET)
print("Hello")

map = nx.Graph()
map.add_node(1)
map.add_edge(1, 2)
map.add_node(2)
map.add_edge(2, 3)
map.add_edge(2, 4)
map.add_edge(3, 10)
map.add_edge(2, 5)
map.add_edge(4,6)
map.add_edge(6, 7)
print("tst")
neighbours = map.neighbors(2)
print(map[2])
print(nx.shortest_path(map, 1, 7))

nodeNeighboursDict = map[3] #dict
number_of_neighbours = len(nodeNeighboursDict)
nodeNeighboursList = []

x = 0
while x <= 48:
    try: #try find the node in nodeNeighbours
        nodeNeighboursDict[x]
        nodeNeighboursList.append(x)
        x+=1

    except KeyError:
        x += 1

print(nodeNeighboursDict)
print(nodeNeighboursList)

shortest_path = nx.shortest_path(map, 1, 7)

print(f"shortest path: {shortest_path}")
def addtoPath(padcoord):
	global shortest_path
	pathto = nx.shortest_path(map, 1, padcoord)
	pathfrom = nx.shortest_path(map, padcoord, 7)
	
	for node in pathfrom:
		if node != padcoord:
			pathto.append(node)
			
		else:
			pass
		
	shortest_path = pathto

addtoPath(10)
print(shortest_path)

subax1 = plt.subplot(221)  
nx.draw(map, with_labels = True, font_weight='bold')
plt.show()

