#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard Python implementation of Erdős–Rényi Network Evaluation with WebID/RDF export
Based on original Google Colab notebook: https://colab.research.google.com/drive/1Dmo63p16DDcOahcvQ0CKPvTTC9J-mOZQ

Original paper methodology:
* Generate Erdős–Rényi networks with N=45 nodes
* 25 equally-spaced values of p from 0.2 to 1.0
* 12 networks per p value (total 300 networks)
* Each node has attributes: accuracy, speed, reliability, random tasks from A-I
* Evaluate node ranking using weighted multi-factor algorithm
* Export/import networks as RDF/TTL WebID format

@authors: Dr. Albert Esterline, Chris Paradis
"""

# -------------------------- ALL IMPORTS AT TOP ------------------------------
import os
import sys
import math
import shutil
import statistics
from operator import itemgetter
import functools

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph, Namespace, RDF, URIRef, Literal

# -------------------------- GLOBAL CONSTANTS --------------------------------
TASK_LIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
TARGET_TASKS = {'B', 'D', 'F'}

# RDF Namespaces
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
CUSTOM_NS = Namespace("http://ncat.edu/custom/")

# Set random seed for reproducibility
np.random.seed(42)


# -------------------------- DATA CLASSES ------------------------------------
class WebidData:
    """Container class for WebID person data"""
    def __init__(self, name='', accuracy=0.0, speed=0.0, reliability=0.0, tasks=None, friends=None):
        self.name = str(name)
        self.accuracy = float(accuracy)
        self.speed = float(speed)
        self.reliability = float(reliability)
        self.tasks = tasks if tasks is not None else []
        self.friends = friends if friends is not None else []

    def __str__(self):
        attributes = ", ".join(f"{attr}={value}" for attr, value in self.__dict__.items())
        return f"WebidData({attributes})"

    def to_dict(self):
        return vars(self)


# -------------------------- NETWORK GENERATION ------------------------------
def decorate_nodes(G):
    """
    Add randomly generated values for all 4 attributes for all nodes of G.
    For each node n, randomly generate values for attributes accuracy, speed,
    and reliability, for each, from a uniform [0.0, 1.0) distribution. Also,
    for attribute tasks, randomly select a random number in [2,5] of tasks
    from the global task list.
    """
    for n in G.nodes():
        # Performance attributes
        accuracy, speed, reliability = np.random.uniform(size=3)
        G.nodes()[n]['accuracy'] = accuracy
        G.nodes()[n]['speed'] = speed
        G.nodes()[n]['reliability'] = reliability

        # Tasks attribute: 2-5 random tasks without replacement
        x = np.random.randint(2, 6)
        G.nodes()[n]['tasks'] = list(np.random.choice(TASK_LIST, size=x, replace=False))


def gen_network(p, node_count=45):
    """Generate single Erdős–Rényi network with given edge probability p"""
    G = nx.erdos_renyi_graph(node_count, p)
    decorate_nodes(G)
    return G


# -------------------------- RANKING ALGORITHMS ------------------------------
def total_rank(d):
    """Given a dictionary d, return keys ordered in non-increasing order of values"""
    ss = sorted(d.items(), key=itemgetter(1), reverse=True)
    return [x for x, _ in ss]


def tasks_covered(EG, tasks):
    """Return True if all tasks are covered by nodes in ego network EG"""
    lis = [EG.nodes()[n]['tasks'] for n in EG.nodes()]
    return set(tasks) <= set(functools.reduce(lambda a, b: set(a) | set(b), lis))


def mean_centrality(G):
    """Calculate harmonic mean of betweenness and eigenvector centrality"""
    bc = nx.betweenness_centrality(G)
    ec = nx.eigenvector_centrality(G)
    
    # Normalize eigenvector centrality
    sum_ec = sum(ec.values())
    ec_normalized = {k: v/sum_ec for k, v in ec.items()}
    
    # Harmonic mean
    return {k: (bc[k] * ec_normalized[k]) ** 0.5 for k in ec_normalized.keys()}


def relative_rank(n, sorted_nodes):
    """Return normalized rank (1.0 = highest, 0.0 = lowest)"""
    return 1.0 - sorted_nodes.index(n) / (len(sorted_nodes) - 1)


def average_rank(EG, sorted_nodes):
    """Average relative rank of all nodes in ego network"""
    return sum([relative_rank(n, sorted_nodes) for n in EG.nodes()]) / len(EG)


def combed_centrality_rank(EG, G, n):
    """Combined centrality rank for node n"""
    sorted_nodes = total_rank(mean_centrality(G))
    return (relative_rank(n, sorted_nodes) + average_rank(EG, sorted_nodes)) / 2


def relative_core_num(G, n, max_core_num):
    """Normalized core number for node n"""
    CN = nx.core_number(G)
    return CN[n] / max_core_num


def average_k(EG, G, max_core_num):
    """Average normalized core number for ego network"""
    CN = nx.core_number(EG)
    return (sum(CN.values()) / len(CN)) / max_core_num


def min_k(EG, G, max_core_num):
    """Minimum normalized core number for ego network"""
    return min(nx.core_number(EG).values()) / max_core_num


def combed_core_num(EG, G, n):
    """Combined core number metric for node n"""
    max_core_num = max(nx.core_number(G).values())
    if max_core_num == 0:
        max_core_num = 1
    
    rel = relative_core_num(G, n, max_core_num)  # ✅ BUG FIXED: was always passing 0
    ave = average_k(EG, G, max_core_num)
    mn = min_k(EG, G, max_core_num)
    
    return (rel + ave + mn) / 3.0


def min_max_all_attrs(G, attrs):
    """Calculate min and max values for each attribute across whole graph"""
    def min_max_attr(G, attr):
        mn, mx = 1.0, 0.0
        present = False
        for n in G.nodes():
            if attr in G.nodes()[n]:
                present = True
                val = G.nodes()[n][attr]
                if val > mx:
                    mx = val
                if val < mn:
                    mn = val
        if not present:
            raise Exception(f'Attribute {attr} not present in network')
        return mn, mx

    return {attr: min_max_attr(G, attr) for attr in attrs}


def ave_all_attr_values_norm(EG, attrs, attr_minmax):
    """Average normalized attribute values for ego network"""
    def ave_attr_value_norm(EG, attr, mx):
        sm, cnt = 0.0, 0
        for n in EG.nodes():
            if attr in EG.nodes()[n]:
                sm += EG.nodes()[n][attr]
                cnt += 1
        return (sm/cnt)/mx if cnt > 0 else 0

    return sum([ave_attr_value_norm(EG, attr, attr_minmax[attr][1]) for attr in attrs]) / len(attrs)


def g_mean_min_attr_values_norm(EG, attrs, attr_minmax):
    """Geometric mean of minimum normalized attribute values"""
    def min_attr_value_norm(EG, attr, mn, mx):
        mn1 = 1.0
        for n in EG.nodes():
            if attr in EG.nodes()[n]:
                val = EG.nodes()[n][attr]
                if val < mn1:
                    mn1 = val
        
        if mx == mn:
            return 1.0
        
        # Guard against zero
        return (0.003 + 0.997 * ((mn1 - mn) / (mx - mn))) ** (1/5)

    return math.prod([min_attr_value_norm(EG, attr, *attr_minmax[attr])
                      for attr in attrs]) ** (1/len(attrs))


def ave_min_all_attr_values_norm(EG, G, attrs):
    global_dict = min_max_all_attrs(G, attrs)
    return (ave_all_attr_values_norm(EG, attrs, global_dict),
            g_mean_min_attr_values_norm(EG, attrs, global_dict))


def average_assortativity(EG, attrs):
    """Average normalized assortativity for performance attributes"""
    assort = [nx.numeric_assortativity_coefficient(EG, x) for x in attrs]
    return ((sum(assort) / 3.0) + 1) / 2


def average_degree(EG, G, max_deg):
    """Normalized average degree for ego network"""
    return (sum(dict(G.degree(nbunch=EG.nodes())).values()) / len(EG)) / max_deg


def min_degree(EG, max_deg):
    """Normalized minimum degree for ego network"""
    return min(dict(EG.degree()).values()) / max_deg


def combed_degree(EG, G):
    """Combined degree metric"""
    max_deg = max(dict(G.degree()).values())
    if max_deg == 0:
        max_deg = 1
    return (average_degree(EG, G, max_deg) + min_degree(EG, max_deg)) / 2.0


def normed_combed_deg_assort(G, EG):
    """Normalized degree assortativity"""
    deg_assort_full = nx.degree_assortativity_coefficient(G)
    deg_assort_embed_ego = nx.degree_assortativity_coefficient(G, nodes=EG.nodes())
    deg_assort_ego = nx.degree_assortativity_coefficient(EG)
    
    deg_assort_embed_ego_norm = (deg_assort_embed_ego - deg_assort_full) / 2
    deg_assort_ego_norm = (deg_assort_ego - deg_assort_full) / 2
    
    return (((deg_assort_embed_ego_norm + deg_assort_ego_norm) / 2.0) + 1) / 2


def overall(EG, G, n):
    """
    Final weighted overall score for node n
    Weights:
    35% centrality, 23% core number, 15% average performance,
    9% min performance, 7% assortativity, 6% degree, 4% degree assortativity
    """
    attrs = ['accuracy', 'speed', 'reliability']
    ave_perf, min_perf = ave_min_all_attr_values_norm(EG, G, attrs)
    
    return (0.35 * combed_centrality_rank(EG, G, n)
            + 0.23 * combed_core_num(EG, G, n)
            + 0.15 * ave_perf
            + 0.09 * min_perf
            + 0.07 * average_assortativity(EG, attrs)
            + 0.06 * combed_degree(EG, G)
            + 0.04 * normed_combed_deg_assort(G, EG))


def global_ranking(G, tasks):
    """Calculate ranking for all nodes in graph G"""
    fails = 0
    ranking = {}
    
    for n in G.nodes():
        EG = nx.ego_graph(G, n)
        if tasks_covered(EG, tasks):
            ranking[n] = round(overall(EG, G, n), 3)
        else:
            fails += 1
    
    return ranking, fails


# -------------------------- TRIAL EXECUTION ---------------------------------
def run_trials(strt=0.2, stp=1.0, num=25, reps=12):
    """
    Run full network generation and evaluation trials
    Returns: ps, average mins, average maxs, average aves, average fails
    """
    ps, ave_mins, ave_maxs, ave_aves, ave_fails = [], [], [], [], []
    debug_counter = 0
    
    for p in np.linspace(strt, stp, num=num):
        mins, maxs, aves, fails = [], [], [], []
        
        for cnt in range(reps):
            G = gen_network(p)
            rnking, fls = global_ranking(G, TARGET_TASKS)
            
            fails.append(fls)
            vals = sorted(rnking.values())
            mins.append(vals[0])
            maxs.append(vals[-1])
            aves.append(statistics.mean(vals))
            
            debug_counter += 1  # ✅ BUG FIXED: counter was not incrementing
            
            # Print first 10 networks for debugging
            if debug_counter < 11:
                print(f'\nNetwork {debug_counter} (p={p:.3f}):')
                print(f'  Nodes: {len(G.nodes())}')
                print(f'  Edges: {len(G.edges())}')
                print(f'  Coverage failures: {fls}')
        
        ps.append(p)
        ave_fails.append(statistics.mean(fails))
        ave_mins.append(statistics.mean(mins))
        ave_maxs.append(statistics.mean(maxs))
        ave_aves.append(statistics.mean(aves))
        
        print(f'Completed p={p:.3f} | Avg fails: {ave_fails[-1]:.2f} | Avg score: {ave_aves[-1]:.3f}')
    
    return ps, ave_mins, ave_maxs, ave_aves, ave_fails


# -------------------------- RDF / WEBID EXPORT ------------------------------
def nxgraphs_to_dictionaries(er_networks):
    """Convert list of NetworkX graphs to list of WebidData objects"""
    all_networks = []
    
    for network in er_networks:
        this_network = []
        graph_dict = nx.to_dict_of_dicts(network).items()
        
        for node_id, neighbors in graph_dict:
            person = WebidData(
                name=str(node_id),
                accuracy=network.nodes()[node_id]['accuracy'],
                speed=network.nodes()[node_id]['speed'],
                reliability=network.nodes()[node_id]['reliability'],
                tasks=network.nodes()[node_id]['tasks'],
                friends=[str(f) for f in neighbors.keys()]
            )
            this_network.append(person)
        
        all_networks.append(this_network)
    
    return all_networks


def make_rdf_for(person, folder_name='000', write_to_file=False, print_to_screen=False):
    """Generate RDF/TTL file for a single person"""
    rdf_graph = Graph()
    
    base_uri = f"http://{person.name.lower()}.test"
    p = URIRef(base_uri)
    
    rdf_graph.add((p, RDF.type, FOAF.Person))
    rdf_graph.add((p, FOAF.name, Literal(person.name)))
    
    # Performance attributes
    rdf_graph.add((p, CUSTOM_NS.speed, Literal(person.speed)))
    rdf_graph.add((p, CUSTOM_NS.accuracy, Literal(person.accuracy)))
    rdf_graph.add((p, CUSTOM_NS.reliability, Literal(person.reliability)))
    
    # Tasks
    for task in person.tasks:
        rdf_graph.add((p, CUSTOM_NS.tasks, Literal(task)))
    
    # Friends
    for friend in person.friends:
        friend_node = URIRef(f"http://{friend.lower()}.test/webid.ttl")
        rdf_graph.add((p, FOAF.knows, friend_node))
        rdf_graph.add((friend_node, RDF.type, FOAF.Person))
        rdf_graph.add((friend_node, FOAF.name, Literal(friend)))
    
    if write_to_file:
        os.makedirs(folder_name, exist_ok=True)
        output_file = os.path.join(folder_name, f'{person.name.zfill(2)}.ttl')
        rdf_graph.serialize(destination=output_file, format='ttl')
    
    if print_to_screen:
        print('-' * 60)
        print(f'PERSON: {person.name}')
        print(rdf_graph.serialize(format='ttl'))


def write_network_to_rdfs(network_list, folder_name='000', write_to_file=False, print_to_screen=False):
    """Write entire network to RDF files in numbered folder"""
    for person in network_list:
        make_rdf_for(person, folder_name, write_to_file, print_to_screen)


def export_all_networks(network_list, start_index=0):
    """Export all networks to numbered folders"""
    print(f'\nExporting {len(network_list)} networks to disk...')
    
    # Clean up existing folders
    delete_all_folders()
    
    for i, network in enumerate(network_list):
        folder_name = str(i + start_index).zfill(3)
        write_network_to_rdfs(network, folder_name=folder_name, write_to_file=True, print_to_screen=False)
        
        if i % 40 == 0:
            print()
        print('.', end='', flush=True)
    
    print(f'\nExport complete. {len(network_list)} networks written.')


def delete_all_folders(start=0, end=300):
    """Delete all numbered network folders"""
    for i in range(start, end + 1):
        folder_name = str(i).zfill(3)
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)


# -------------------------- RDF / WEBID IMPORT ------------------------------
def read_in_a_network(folder_path):
    """Read folder of RDF/TTL files and reconstruct NetworkX graph"""
    new_graph = nx.Graph()
    file_list = os.listdir(folder_path)
    network = []
    
    for file in file_list:
        g = rdflib.Graph()
        file_name = os.path.join(folder_path, file)
        g.parse(file_name, format='turtle')
        
        subjects = sorted(set(str(subj) for subj, _, _ in g))
        
        new_p = WebidData()
        new_p.friends = []
        new_p.tasks = []
        new_p.name = file.replace('.ttl', '')
        
        for subj in subjects:
            for _, pred, obj in g.triples((rdflib.URIRef(subj), None, None)):
                pred_str = str(pred)
                obj_str = str(obj)
                
                if pred_str == 'http://ncat.edu/custom/accuracy':
                    new_p.accuracy = float(obj_str)
                elif pred_str == 'http://ncat.edu/custom/reliability':
                    new_p.reliability = float(obj_str)
                elif pred_str == 'http://ncat.edu/custom/speed':
                    new_p.speed = float(obj_str)
                elif pred_str == 'http://ncat.edu/custom/tasks':
                    new_p.tasks.append(obj_str)
                elif pred_str == 'http://xmlns.com/foaf/0.1/name':
                    if "webid.ttl" in subj:
                        new_p.friends.append(obj_str)
        
        network.append(new_p)
    
    # Add nodes first
    for p in network:
        new_graph.add_node(
            int(p.name),
            speed=p.speed,
            accuracy=p.accuracy,
            reliability=p.reliability,
            tasks=p.tasks
        )
    
    # Add edges
    for p in network:
        for f in p.friends:
            if int(p.name) != int(f):
                new_graph.add_edge(int(p.name), int(f))
    
    return new_graph


# -------------------------- PLOTTING FUNCTIONS ------------------------------
def plot_results(ps, a_mins, a_maxs, a_aves, a_fails):
    """Plot score and failure graphs"""
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(ps, a_mins, 'k^', label='Minimum')
    plt.plot(ps, a_aves, 'k-', label='Average')
    plt.plot(ps, a_maxs, 'k--', label='Maximum')
    plt.legend(fontsize=8)
    plt.xlabel('p (probability of an edge between any 2 nodes)')
    plt.ylabel('score', fontsize=12)
    plt.title('Score vs. p', fontsize=14)
    
    plt.subplot(1, 2, 2)
    plt.plot(ps, a_fails, 'r-')
    plt.xlabel('p (probability of an edge between any 2 nodes)')
    plt.ylabel('Average failures')
    plt.title('Failures to cover all tasks vs. p', fontsize=14)
    
    plt.tight_layout()
    plt.show()


# -------------------------- MAIN EXECUTION ----------------------------------
def main():
    print("=== Erdos-Renyi Network Evaluation Tool ===")
    print("Running trials...")
    
    # Run full trials
    pp, a_mins, a_maxs, a_aves, a_fails = run_trials()
    
    # Plot results
    plot_results(pp, a_mins, a_maxs, a_aves, a_fails)
    
    print("\n=== Trial Complete ===")
    print(f"Total networks evaluated: 300")


if __name__ == '__main__':
    main()
