import matplotlib.pyplot as plt
import pickle
import networkx as nx

#Properties of a node
#id, branched, move number, type, orientationonpad

explored = []

id = [-120, 60, 120]
branchleft = False
branchright = True
moveno = 1
orientation = "N"
type = "carpet"

id2 = [120, 60, -120]
branchleft2 = True
branchright2 = True
moveno2 = 2
orientation2 = "W"
type2 = "carpet"

explored.append(id)
explored.append(id2)

map = nx.Graph()
map.add_node(str(id), t=type,bl=branchleft, br = branchright, mn = moveno, o = orientation)
map.add_node(str(id2), t=type2, bl=branchleft2, br=branchright2, mn=moveno2, o=orientation2)
map.add_edge(str(id2), "test")
map.add_node("test")
map.add_edge(str(id2), "test")
map.add_edge(str(id2), "test")
    
subax1 = plt.subplot(221)  
nx.draw(map, with_labels = True, font_weight='bold')
plt.show(block=False)

findingid = [120, 60, -120]
dataBL = nx.get_node_attributes(map, "bl")
print(nx.nodes(map))

print(dataBL.get(str(findingid)))