import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
import networkx as nx
import matplotlib.pyplot as plt
import pyscript
import io

file_path = "etc/test.csv"

try:
    from pyodide.http import open_url
    file_content = open_url(file_path).read()
    data = pd.read_csv(io.StringIO(file_content))
except ImportError:
    data = pd.read_csv(file_path)

data = pd.get_dummies(data, columns=['occupation', 'location'])
var_names = data.columns.tolist()
columns_to_convert = [
    col for col in data.columns if col.startswith(
        'occupation') or col.startswith('location')]
data[columns_to_convert] = data[columns_to_convert].astype(int)
data = data.to_numpy()

cg = pc(
    data, 
    alpha=0.05, 
    indep_test='fisherz', 
    stable=True, 
    background_knowledge=None,
    node_names=var_names,
    verbose=True)

# Create a networkx graph
nx_graph = nx.DiGraph()

all_nodes = cg.G.get_nodes()
for node in all_nodes:
    nx_graph.add_node(node.get_name())

# Add edges
for edge in cg.G.get_graph_edges():
    nx_graph.add_edge(edge.get_node1().get_name(), edge.get_node2().get_name())

# Draw the graph
pos = nx.spring_layout(nx_graph)  # Layout for better visualization

fig, ax = plt.subplots(figsize=(10, 8))
nx.draw(
    nx_graph, 
    pos, 
    with_labels=True, 
    node_color='lightblue', 
    edge_color='gray', 
    node_size=2000, 
    font_size=15)

pyscript.display("plot", fig)