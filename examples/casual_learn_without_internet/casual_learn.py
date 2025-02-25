
import pandas as pd
import numpy as np
from dowhy import CausalModel
from dowhy.plotter import plot_causal_effect
from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.ConstraintBased.FCI import fci
from causallearn.utils.PCUtils.BackgroundKnowledge import BackgroundKnowledge
import networkx as nx
from causallearn.graph.GraphNode import GraphNode
from copy import deepcopy
import warnings 
warnings.filterwarnings("ignore")  # Python warnings



# <><><><><><><><><><><><><><><>
# Step 0: Prepare dataset features
# <><><><><><><><><><><><><><><>
FEATURES = {
    "Age": {"name": "age", "category": None, "independant": True},
    "Gender": {
        "name": "gender", 
        "category": {
            "Male": 0, "Female": 1, "Other": 2},
        "independant": True
    },
    "Education_Level": {
        "name": "education", 
        "category": {
            "High School": 0,
            "Bachelor's": 1,
            "Bachelor's Degree": 1,
            "Master's": 2,
            "Master's Degree": 2,
            "PhD": 3,
            "phD": 3
        },
        "independant": False
    },
    "Salary": {"name": "salary", "category": None, "independant": False}
}

PRIOR_KNOWLEDGE = {
    "required": ["Education_Level -> Salary"],
    "forbidden": ["Gender -> Education_Level"]
}

TREATMENTS_OUTCOMES = [
    {
        "treatment": {
            "name": "Education_Level",
            # "thres": None
            "thres": {
                0: ["High School", "Bachelor's", "Bachelor's Degree"],
                1: ["Master's", "Master's Degree", "PhD", "phD"]}
            },
        "outcome": {"name": "Salary"}
    },
    {
        "treatment": {
            "name": "Age",
            "thres": None,
            #"thres": {
            #    0: ["Female"],
            #    1: ["Male", "Other"]}
            }, 
        "outcome": {"name": "Salary"}
    }
]

CAUSAL_GRAPH_METHOD = "fci" # pc, manual, fci

# <><><><><><><><><><><><><><><>
# Step 1: Load required functions
# <><><><><><><><><><><><><><><>
try:
    from pyscript import display
    from pyodide.http import open_url
    import io
    import base64
    from js import document, Blob, URL

    run_local = False
    def download_png_file(png_filename):
        with open(png_filename, "rb") as f:  # If it’s a file in memory or temp storage
            fid = f.read()
        # Convert the PNG to a base64 string
        img_data = base64.b64encode(fid).decode('utf-8')

        # Create a data URL
        data_url = f"data:image/png;base64,{img_data}"

        # Use JavaScript to trigger the download
        link = document.createElement("a")
        link.href = data_url
        link.download = "downloaded_image.png"  # Name the file as desired
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

    def download_csv_file(df, csv_filename):
        csv_string = df.to_csv(index=False)  # index=False avoids adding row numbers
        data_url = "data:text/csv;charset=utf-8," + csv_string
        link = document.createElement("a")
        link.href = data_url
        link.download = csv_filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

    def download_txt_file(content, filename):
        # Create a Blob with the file content
        blob = Blob.new([content], {"type": "text/plain"})
        # Create a temporary URL for the Blob
        url = URL.createObjectURL(blob)
        # Create a hidden link element
        link = document.createElement("a")
        link.setAttribute("href", url)
        link.setAttribute("download", filename)  # Set the filename for download
        # Programmatically click the link to trigger download
        link.click()
        # Clean up the URL object
        URL.revokeObjectURL(url)

except ImportError:
    run_local = True


# <><><><><><><><><><><><><><><>
# Step 2: Load input data
# <><><><><><><><><><><><><><><>
if run_local:
    df = pd.read_csv("examples/casual_learn_without_internet/salary_data.csv")
else:
    file_content = open_url("salary_data.csv").read()
    df = pd.read_csv(io.StringIO(file_content))

df.rename(columns=lambda x:x.replace(' ', '_'),inplace=True)

numeric = ['Age', 'Years_of_Experience', 'Salary']
for col in numeric:
    df[col].fillna(df[col].mean(), inplace=True)

categorical = ['Gender', 'Education_Level']
for col in categorical:
    mode_val = df[col].mode()[0] 
    df[col].fillna(mode_val, inplace=True)

name_maps = {}
for ori_name in FEATURES:
    name_maps[ori_name] = FEATURES[ori_name]["name"]

df = df[list(FEATURES.keys())]
df = df.rename(columns=name_maps)
df = df.dropna()

for ori_name in FEATURES:
    if FEATURES[ori_name]["category"] is None:
        continue
    df[FEATURES[ori_name]["name"]] = df[
        FEATURES[ori_name]["name"]].replace(
        FEATURES[ori_name]["category"]
    )


# <><><><><><><><><><><><><><><>
# Step 3: Create casual graph
# <><><><><><><><><><><><><><><>
node_names = df.columns.tolist()

if CAUSAL_GRAPH_METHOD in ["pc", "fci"]:

    df_value = df.to_numpy()

    prior_knowledge = BackgroundKnowledge()

    independant_vars = []
    for ori_name in FEATURES:
        if FEATURES[ori_name]["independant"]:
            independant_vars.append(FEATURES[ori_name]["name"])

    for proc_var in independant_vars:
        for proc_node_name in node_names:
            if proc_var == proc_node_name:
                continue
            prior_knowledge.add_forbidden_by_node(GraphNode(proc_node_name), GraphNode(proc_var))

    for knowledge_type in ["required", "forbidden"]:

        for proc_knowledge in PRIOR_KNOWLEDGE[knowledge_type]:
            proc_knowledge = proc_knowledge.split("->")
            start_node = proc_knowledge[0].strip()
            end_node = proc_knowledge[1].strip()
    
            if knowledge_type == "required":
                prior_knowledge.add_required_by_node(
                    GraphNode(FEATURES[start_node]["name"]),
                    GraphNode(FEATURES[end_node]["name"]),
                )
            elif knowledge_type == "forbidden":
                prior_knowledge.add_forbidden_by_node(
                    GraphNode(FEATURES[start_node]["name"]),
                    GraphNode(FEATURES[end_node]["name"]),
                )
    if CAUSAL_GRAPH_METHOD == "pc":
        cg = pc(
            df_value, 
            alpha=0.05, 
            indep_test='fisherz', 
            stable=True, 
            background_knowledge=prior_knowledge,
            node_names=node_names,
            verbose=True)
        all_nodes = cg.G.get_nodes()
        all_edges = cg.G.get_graph_edges()
    elif CAUSAL_GRAPH_METHOD == "fci":
        G, all_edges = fci(
            dataset=df_value, 
            independence_test_method='fisherz',
            background_knowledge=prior_knowledge,
            node_names=node_names
        )
        all_nodes = G.get_nodes()

    causal_graph = nx.DiGraph()
    for node in all_nodes:
        causal_graph.add_node(node.get_name())

    # Add edges
    for edge in all_edges:
        causal_graph.add_edge(
            edge.get_node1().get_name(), edge.get_node2().get_name())

elif CAUSAL_GRAPH_METHOD == "manual":
    causal_graph = """
    digraph {
        age;
        gender;
        education;
        salary;
        gender -> education;
        gender -> education;
        age -> education;
        age -> education;
        gender -> education;
    }   
    """
    causal_graph = causal_graph.replace("\n", " "),

# <><><><><><><><><><><><><><><>
# Step 4: Set up Causal models
# <><><><><><><><><><><><><><><>
model_graph_plot = False
all_outputs = []
for proc_treatment_outcome in TREATMENTS_OUTCOMES:

    proc_df = deepcopy(df)
    proc_treatment_name = FEATURES[proc_treatment_outcome["treatment"]["name"]]["name"]
    proc_outcome_name = FEATURES[proc_treatment_outcome["outcome"]["name"]]["name"]

    if proc_treatment_outcome["treatment"]["thres"] is not None:
        for proc_feature in FEATURES:
            if FEATURES[proc_feature]["name"] != proc_treatment_name:
                continue
            
            for proc_thres in [0, 1]:
                values_to_replace = list(set([FEATURES[proc_feature]["category"][item] for 
                        item in proc_treatment_outcome["treatment"]["thres"][proc_thres]]))
                proc_df[proc_treatment_name] = proc_df[
                    proc_treatment_name].replace(values_to_replace, proc_thres)
            
    model= CausalModel(
        data = proc_df,
        graph=causal_graph,
        treatment=proc_treatment_name,
        outcome=proc_outcome_name)

    if not model_graph_plot:
        model.view_model(file_name="causal_model")
        model_graph_plot = True

    estimands = model.identify_effect(proceed_when_unidentifiable=True)

    # estimands_df = pd.DataFrame(estimands.estimands)
    # estimands_df["treatment"] = proc_treatment
    # estimands_df["outcome"] = TREATMENTS_OUTCOMES[proc_treatment]

    try:
        estimate= model.estimate_effect(
            identified_estimand=estimands,
            method_name='backdoor.propensity_score_weighting',
            confidence_intervals=True,
            test_significance=True,
            # common_causes=['gender']
        )
    except Exception:
        estimate= model.estimate_effect(
            identified_estimand=estimands,
            method_name='backdoor.linear_regression',
            confidence_intervals=True,
            test_significance=True
        )
        # plot_causal_effect(estimate, proc_df[proc_treatment_name], proc_df[proc_outcome_name])

    # Save to a text file
    filename = f"{proc_treatment_name}_{proc_outcome_name}_estimates.txt"

    output_text = "<><><><><><><><><><><><><><>\nParameters\n<><><><><><><><><><><><><><>\nTreatment: " + \
        f"{proc_treatment_name}\nOutcome: {proc_outcome_name}\n\n"

    output_text += f"<><><><><><><><><><><><><><>\nResults\n<><><><><><><><><><><><><><>\n{str(estimate)}\n\n"
    if run_local:
        print(f'Estimate of causal effect: {estimate}')
    else:
        display(f'Estimate of causal effect: {estimate}')

    # <><><><><><><><><><><><><><><>
    # Step 5: Refute model
    # <><><><><><><><><><><><><><><>
    refutel_common_cause=model.refute_estimate(estimands,estimate,"random_common_cause")
    output_text += f"\n\n<><><><><><><><><><><><><><>\nRefutel_common_cause\n<><><><><><><><><><><><><><>\n{str(refutel_common_cause)}"
    with open(filename, "w") as file:
        file.write(output_text)

    all_outputs.append(filename)

# <><><><><><><><><><><><><><><>
# Step 6: Download model outputs
# <><><><><><><><><><><><><><><>
if run_local:
    print(estimands)
    # estimands_df.to_csv("estimands.csv")
else:
    display(estimands)
    # download_csv_file(estimands_df, "estimands.csv")
    download_png_file("causal_model.png")

    for proc_output in all_outputs:
        with open(proc_output, "r") as f:
            file_content = f.read()
        download_txt_file(file_content, proc_output)