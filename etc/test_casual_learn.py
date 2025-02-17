import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
import networkx as nx
import matplotlib.pyplot as plt
n_samples = 500

data = pd.DataFrame({
    'education': np.random.randint(10, 20, n_samples),  # Years of education
    'age': np.random.randint(25, 65, n_samples),       # Age in years
    'income': np.random.randint(25000, 120000, n_samples), # Annual income
    'occupation': np.random.choice(['blue-collar', 'white-collar', 'service'], n_samples),
    'location': np.random.choice(['urban', 'rural'], n_samples),
    'parental_income': np.random.randint(30000, 150000, n_samples) # Parental income
})

# Introduce some plausible relationships (for demonstration)
data['income'] = data['income'] + 2000 * data['education'] + 1000 * (data['age'] - 40) + np.random.normal(0, 10000, n_samples)
data.loc[data['occupation'] == 'white-collar', 'income'] += 15000
data.loc[data['location'] == 'urban', 'income'] += 5000
data['education'] = data['education'] + (data['parental_income'] - 80000)/5000 + np.random.normal(0, 2, n_samples)
data['education'] = np.clip(data['education'], 10, 20).astype(int) # Education should be between 10 and 20 years

data.to_csv("test.csv")

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
plt.figure(figsize=(10, 8))
nx.draw(nx_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15)

# Show the graph
plt.savefig("test.png", bbox_inches='tight')
plt.close()