from colorama import Fore
import networkx as nx

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
map.add_node(1, br=True, bl=False)
print(nx.get_node_attributes(map, "br"))
print(nx.get_node_attributes(map, "bl"))
nx.set_node_attributes(map, False, "br")
print(nx.get_node_attributes(map, "br"))
print(nx.get_node_attributes(map, "bl"))

print(z)
z[0]
y = z[1]
y["bl"] = True
y["b0"] = True
print(z)