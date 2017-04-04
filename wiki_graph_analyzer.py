# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 14:37:59 2015

@author: mrinmoymaity
"""
import networkx as nx
import numpy as np
from scipy.stats import spearmanr,pearsonr
import os
#from create_wiki_graph import *

# Input two graphs G1 and G2 
# Output G1 intersection G2
def find_overlapping_nodes(G1,G2):
    common_users = []
    if G1.number_of_nodes() > G2.number_of_nodes():
        G1, G2 = G2, G1
    for user in G1.nodes():
        if G2.has_node(user):
            common_users.append(user)
    return common_users
    
## test find_overlapping_nodes
#def test_find_overlapping_nodes():
#    G1 = nx.path_graph(10)
#    G2 = nx.tetrahedral_graph()
#    print G1.nodes()
#    print G2.nodes()
#    find_overlapping_nodes(G1, G2)
#    
#test_find_overlapping_nodes()


# Input two graphs G1 and G2 
# Output G1 s edges intersection G2 s edges   
def find_overlapping_edges(G1, G2):
    common_links = []
    if G1.number_of_edges() > G2.number_of_edges():
        G1, G2 = G2, G1
    for link in G1.edges():
        user1, user2 = link
        if G2.has_edge(user1, user2):
            common_links.append([link, G1[user1][user2]['weight']+G2[user1][user2]['weight']])
    return common_links
    
## test find_overlapping_nodes
#def test_find_overlapping_edges():
#    G1 = nx.path_graph(10)
#    G2 = nx.tetrahedral_graph()
#    print G1.edges()
#    print G2.edges()
#    find_overlapping_edges(G1, G2)
#    
#test_find_overlapping_edges()
    
# Accept multiple graphs and return their union    
def graph_union_combine_edge_weights(f_arg, *argv):
    print "Graph Union combine edge weights"
    G = nx.Graph()
    
#    node_dict_farg = nx.get_node_attributes(f_arg, 'label')
    for user in f_arg.nodes():
        if G.has_node(user) != None:
            G.add_node(user)
    for graph in argv:
        for user in graph.nodes():
            if G.has_node(user) != None:
                G.add_node(user)
    
    for link in f_arg.edges():
        user1, user2 = link
        if G.has_edge(user1, user2) != None:
            G.add_edge(user1, user2)
            G[user1][user2]['weight'] = f_arg[user1][user2]['weight']
        else:
            G[user1][user2]['weight'] += f_arg[user1][user2]['weight']
    for graph in argv:
        for link in graph.edges():
            user1, user2 = link
            if G.has_edge(user1, user2) != None:
                G.add_edge(user1, user2)
                G[user1][user2]['weight'] = graph[user1][user2]['weight']
            else:
                G[user1][user2]['weight'] += graph[user1][user2]['weight']
    return G
    
#def test_graph_union_combine_edge_weights():
#    G1 = nx.Graph()
#    G1.add_weighted_edges_from([(1,5,0.125),(1,3,0.75),(2,4,1.8),(3,5,0.1)])
#    G2 = nx.Graph()
#    G2.add_weighted_edges_from([(1,2,0.125),(1,3,0.75),(2,4,1.2),(3,4,0.375)])
#    print G1.edges()
#    print G2.edges()
#    print graph_union_combine_edge_weights(G1, G2)
#    
#test_graph_union_combine_edge_weights()
    
def graph_union_ignore_edge_weights(f_arg, *argv):
    G = nx.Graph()
    
    for user in f_arg.nodes():
        if G.has_node(user) != None:
            G.add_node(user)
    for graph in argv:
        for user in graph.nodes():
            if G.has_node(user) != None:
                G.add_node(user)
    
    for link in f_arg.edges():
        user1, user2 = link
        if G.has_edge(user1, user2) != None:
            G.add_edge(user1, user2)
    for graph in argv:
        for link in graph.edges():
            user1, user2 = link
            if G.has_edge(user1, user2) != None:
                G.add_edge(user1, user2)
    return G
    
# Combine all the graph nodes and edges
# Edge weights of overlapping graph is sum of previous ones
def graph_intersection_combine_edge_weights(G1, G2):
    print "Graph intersection combine edge weights"
    G = nx.Graph()
    if G1.number_of_nodes() > G2.number_of_nodes():
        G1, G2 = G2, G1
    for user in G1.nodes():
        if G2.has_node(user) and G.has_node(user) != None:
            G.add_node(user)
    if G1.number_of_edges() > G2.number_of_edges():
        G1, G2 = G2, G1
    for link in G1.edges():
        user1, user2 = link
        if G2.has_edge(user1, user2) and G.has_edge(user1, user2) != None:
            G.add_edge(user1, user2, weight=G1[user1][user2]['weight']+G2[user1][user2]['weight'])
    #print G.edges()
    return G

# Used to find out how much part of a graph contributes to overlaps
def part_in_overlapping_graph(subpart_G, overlapped_G):
    edge_set = []
    for overlapping_edge in overlapped_G.edges():
        user1, user2 = overlapping_edge
        if subpart_G.has_edge(user1, user2):            
            edge_set.append([user1, user2, subpart_G[user1][user2]['weight']])
    return edge_set


def union_of_intersections_of_all_linked_graph_with_primary_graph(f_arg, *argv):
    constructed_graph = nx.Graph()    
    for graph in argv:
        G = graph_intersection_combine_edge_weights(f_arg, graph)
        constructed_graph = graph_union_combine_edge_weights(constructed_graph, G)
    return constructed_graph
    
# Accept an array in form <node1, node2, weight> and return set of weights
def set_of_weights(edge_set):
    set_of_weights = []
    for idx in range(len(edge_set)):
        set_of_weights.append(edge_set[idx][2])
    return set_of_weights


# Accept arrays and return Pearson's correlation coefficient
def calculate_correlation_coeff(w1, w2):
    set1 = np.array(w1)
    set2 = np.array(w2)
    print set1, set2
    return np.corrcoef(set1, set2)[1][0]
    
def convert_nodeid_to_labels(iGraph):
    oGraph = nx.Graph()
    node_dict = nx.get_node_attributes(iGraph, 'label')
#    print "node_dict:" , node_dict
    for link in iGraph.edges():
        user1, user2 = link
        mod_user1 = node_dict.get(user1)
        mod_user2 = node_dict.get(user2)
#        print mod_user1, mod_user2, iGraph[user1][user2]['weight']
        oGraph.add_edge(mod_user1, mod_user2, weight=iGraph[user1][user2]['weight'])
#    print "oGraph: ", oGraph.edges()
    return oGraph
 
     
    
def level_1_graph_link_analyzer(Primary_graph, Graphs):
    print "Inside level_1_graph_link_analyzer"
    extent_of_overlaps = np.zeros(len(Graphs))
    correlation_of_overlaps = np.zeros(len(Graphs))
    for idx in range(len(Graphs)):
        print "Index :", idx
        G_union = graph_union_combine_edge_weights(Primary_graph, Graphs[idx])
        G_common = graph_intersection_combine_edge_weights(Primary_graph, Graphs[idx])
        # Measure the extent of overlapping
        extent_of_overlaps[idx] = 1.0*G_common.number_of_edges()/G_union.number_of_edges()
        E_G_common_primary = part_in_overlapping_graph(Primary_graph, G_common)
        E_G_common_linked = part_in_overlapping_graph(Graphs[idx], G_common)
        weight_of_primary_graph = set_of_weights(E_G_common_primary)
        weight_of_linked_graph = set_of_weights(E_G_common_linked)
        # Measure the similarity in user behavior in overlapping network
        correlation_of_overlaps[idx] = calculate_correlation_coeff(weight_of_primary_graph, weight_of_linked_graph)\
        
    print "Measure of extent of overlaps:\n", extent_of_overlaps
    print "Edge Correlation:\n", correlation_of_overlaps
    print "-----------------------------------"
    

# Primary graph represents the controversial pages. Graphs represent all links
# directly connected to primary. We will find all users that has same set of edges with primary
def level_1_all_graph_link_analyzer(Primary_graph, Graphs):
    G_union = Primary_graph
    for idx in range(len(Graphs)):
        G_union = graph_union_combine_edge_weights(G_union, Graphs[idx])
    G_common_all_inclusive = nx.Graph()
    for idx in range(len(Graphs)):
        G_common = graph_intersection_combine_edge_weights(Primary_graph, Graphs[idx])
        G_common_all_inclusive = graph_union_combine_edge_weights(G_common_all_inclusive, G_common)
    # Measure the extent of overlapping
    Jac_coef = G_common.number_of_edges()/float(G_union.number_of_edges()) 
    E_G_common_primary = part_in_overlapping_graph(Primary_graph, G_common_all_inclusive)
    E_G_common_l1 = [0 for idx in len(Graphs)]    
    for idx in range(len(Graphs)):
        E_G_common_l1[idx] = part_in_overlapping_graph(Graphs[idx], G_common_all_inclusive)
    weight_of_primary_graph = set_of_weights(E_G_common_primary)
    for idx in range(len(Graphs)):
        weight_of_linked_graph = set_of_weights(E_G_common_l1[idx])
    # Measure the similarity in user behavior in overlapping network
    edge_correlation = calculate_correlation_coeff(weight_of_primary_graph, weight_of_linked_graph)   
        
    for idx in range(len(Graphs)):
        G_union = graph_union_combine_edge_weights(Primary_graph, Graphs[idx])
        G_common = graph_intersection_combine_edge_weights(Primary_graph, Graphs[idx])
        E_G_common_primary = part_in_overlapping_graph(Primary_graph, G_common)
        E_G_common_linked = part_in_overlapping_graph(Graphs[idx], G_common)
        weight_of_primary_graph = set_of_weights(E_G_common_primary)
        weight_of_linked_graph = set_of_weights(E_G_common_linked)
        # Measure the extent of overlapping
        Jac_coef = G_common.number_of_edges()/float(G_union.number_of_edges())
        # Measure the similarity in user behavior in overlapping network
        edge_correlation = calculate_correlation_coeff(weight_of_primary_graph, weight_of_linked_graph)
        print "Graph ", idx+1
        print "Measure of extent of overlaps:\n", Jac_coef
        print "Edge Correlation:\n", edge_correlation
        print "-----------------------------------"
    
    

def graph_union(G1, G2):
    print "Inside Graph Union"
    G =nx.Graph()
    G.add_nodes_from(G1.nodes(data=True))
    G.add_edges_from(G1.edges(data=True))
    G.add_nodes_from(G2.nodes(data=True))
    G.add_edges_from(G2.edges(data=True))
    print "G1:", G1.edges()
    print "G2:", G2.edges()
    print "G:", G.edges()
    return G    



def level_1_graph_link_analyzer_using_gexf(Primary_graph, Graphs):
    print "Inside level_1_graph_link_analyzer_using_gexf"
    print "Number of secondary graphs", len(Graphs)
    extent_of_overlaps = np.zeros(len(Graphs))
    correlation_of_overlaps = np.zeros(len(Graphs))
    for idx in range(len(Graphs)):
        G_union = graph_union_combine_edge_weights(Primary_graph, Graphs[idx])
        #print "G_union:", G_union.edges()
        G_common = graph_intersection_combine_edge_weights(Primary_graph, Graphs[idx])
        #print "G_common:", G_common.edges()
        # Measure the extent of overlapping
        extent_of_overlaps[idx] = 1.0*G_common.number_of_edges()/G_union.number_of_edges()
        E_G_common_primary = part_in_overlapping_graph(Primary_graph, G_common)
        print "E_G_common_primary:", E_G_common_primary
        E_G_common_linked = part_in_overlapping_graph(Graphs[idx], G_common)
        print "E_G_common_linked:", E_G_common_linked
        weight_of_primary_graph = set_of_weights(E_G_common_primary)
        print "weight_of_primary_graph:", weight_of_primary_graph
        weight_of_linked_graph = set_of_weights(E_G_common_linked)
        print "weight_of_linked_graph:", weight_of_linked_graph
        # Measure the similarity in user behavior in overlapping network
        correlation_of_overlaps[idx] = calculate_correlation_coeff(weight_of_primary_graph, weight_of_linked_graph)\
        
    print "Measure of extent of overlaps:\n", extent_of_overlaps
    print "Edge Correlation:\n", correlation_of_overlaps
    print "-----------------------------------"

def main():
    input_dir = "C:\WikiProject\Controversial Single Pages Simple Wiki\Simple Wiki Page Links\\"
    primary_files = os.listdir(input_dir)
    for primary_file in primary_files:
        if primary_file.endswith(".gexf"):
            idx = 0
            print "Accessing :", primary_file
            Primary_graph = nx.read_gexf(str(input_dir+"\\"+primary_file), relabel=True)
#            Primary_graph = convert_nodeid_to_labels(Primary_graph)
            print Primary_graph.edges()
            input_dir = "C:\WikiProject\Controversial Single Pages Simple Wiki\Simple Wiki Page Links\\"
            primary_file = primary_file.split(".")[0].lower()
            sub_dir = "Revision History In Page Links\\"+ primary_file
            files = os.listdir(input_dir+sub_dir)
            file_index = 0 
            for file in files:
                if file.endswith(".gexf"):
                    file_index += 1
            Graphs = [0 for i in range(file_index)]
            for file in files:
                if file.endswith(".gexf"):
                    print "----Accessing Index:", idx, file
                    
                    ipPath = input_dir+sub_dir+"\\"+file
                    ipFile = open(ipPath,"r")
                    Graphs[idx] = nx.read_gexf(ipFile, relabel=True)
#                    Graphs[idx] = convert_nodeid_to_labels(Secondary_graph)
                    print Graphs[idx].edges()
                    idx += 1
                    ipFile.close()
            level_1_graph_link_analyzer_using_gexf(Primary_graph, Graphs)
            
def test_main():
    # Create two separate graphs
    num_graphs = 2
    Primary_graph = nx.Graph()
    Graphs = [0 for idx in range(num_graphs)]
    for idx in range(num_graphs):
        Graphs[idx] = nx.Graph()
    Primary_graph.add_weighted_edges_from([(1,5,0.125),(1,3,0.75),(2,4,1.8),(1,2,0.125)])
    Graphs[0].add_weighted_edges_from([(1,3,1.75),(2,4,0.8),(3,5,0.1),(1,5,0.25)])
    Graphs[1].add_weighted_edges_from([(1,2,0.125),(1,4,0.3),(3,5,0.375)])
    
    level_1_graph_link_analyzer_using_gexf(Primary_graph, Graphs)

main()    
#test_main()
    
#Primary_graph = nx.read_gml("C:\WikiProject\Controversial Single Pages Simple Wiki\Simple Wiki Page Links\\Anarchism.gml")
#Secondary_graph = nx.read_gml("C:\WikiProject\Controversial Single Pages Simple Wiki\Simple Wiki Page Links\Revision History In Page Links\\Anarchism\\312.gml")
#Primary_graph = convert_nodeid_to_labels(Primary_graph)
#Secondary_graph = convert_nodeid_to_labels(Secondary_graph)
#Graphs = []
#Graphs.append(Secondary_graph)
#level_1_graph_link_analyzer(Primary_graph, Graphs)
#Graph = nx.disjoint_union(Primary_graph, Secondary_graph)
#print "Union:",Graph.edges()
