# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 17:30:35 2015

@author: mrinmoymaity
"""

import networkx as nx
import os

def path_extraction(file, level):
    dir_level_1 = os.path.dirname(file)
    dir_level_2 = os.path.dirname(dir_level_1)
    dir_level_3 = os.path.dirname(dir_level_2)
    if (level == 1):
        return dir_level_1
    elif level == 2:
        return dir_level_2
    elif dir_level_3:
        return dir_level_3
## Test path_extraction
#def test_path_extraction():
#    file = "C:\WikiProject\Controversial Single Pages Simple Wiki\Anonymous Inclusion Without Details\User Graphs With Anonymous"
#    result = path_extraction(file,3)
#    print file
#    print result
#    
#test_path_extraction()

def filename_extraction(file):
    filename = os.path.basename(file)
    parts = filename.split(".")
    return parts[0]
## Test filename extractor    
#def test_filename_extraction():
#    file = "C:\WikiProject\Controversial Single Pages Simple Wiki\Anonymous Inclusion Without Details\User Graphs With Anonymous\\abc.txt"
#    result = filename_extraction(file)
#    print file
#    print result
#test_filename_extraction()


def initialize_undirected_wiki_graph():
    G = nx.Graph()
    return G
    
def initialize_directed_wiki_graph():
    G = nx.DiGraph()
    return G

#Add Nodes/Users if not already present
def update_users(G,user):
    if G.has_node(user) != None:
        G.add_node(user)
    return

#Update weights of the edges or add one if not already present 
def update_user_links(G,user1,user2,weight):
    if G.has_edge(user1,user2):
        G[user1][user2]['weight']+=weight
    else:
        G.add_edge(user1,user2,weight=weight)       
    return

#Only add edges at least one of whose end is anonymous
def update_user_links_only_anonymous(G,user1,user2,weight):
    if G.has_edge(user1,user2):
        G[user1][user2]['weight']+=weight
    else:
        if is_anonymous(user1) or is_anonymous(user2):
            update_users(G, user1)
            update_users(G, user2)
            G.add_edge(user1,user2,weight=weight)       
    return

#Update user network
def include_in_network(G,reverter,revertedTo,reverted):
    update_users(G,reverter)
    update_users(G,reverted)
    update_users(G,revertedTo)
    update_user_links(G,reverter,reverted,-1)
    update_user_links(G,reverter,revertedTo,1)
#    update_user_links(G,reverted,revertedTo,-1)
    return
    
    
#Update user network only anonymous
def include_in_network_only_anonymous(G,reverter,revertedTo,reverted):
    update_user_links_only_anonymous(G,reverter,reverted,-1)
    update_user_links_only_anonymous(G,reverter,revertedTo,1)
    return
    
def graph_properties(G):
    print("No. of triangles:", nx.triangles(G))
    print("Clustering: ", nx.clustering(G))
    structural_balance(G)
    print("Radius:", nx.radius(G))
    print("Diameter:", nx.diameter(G))
    print("Density:", nx.density(G))
    print("Periphery:", nx.periphery(G))


def structural_balance(G):

    node_list = []
    errors = 0
    balanced_triplets = 0
    unbalanced_triplets = 0
    unbalanced_triplets_all_negatives = 0
    unbalanced_triplets_one_negative = 0
    
    for node in G.nodes():
        node_list.append(node)
    for i in range(len(node_list)):
        for j in range(len(node_list)):
            for k in range(len(node_list)):
                node_A = node_list[i]
                node_B = node_list[j]
                node_C = node_list[k]
                if (i!=j) and (j!=k) and (i!=k):
                    if G.has_edge(node_A,node_B) and G.has_edge(node_B, node_C) and G.has_edge(node_C, node_A):
                            edge_AB = (G[node_A][node_B]['weight']>=0)
                            edge_BC = (G[node_B][node_C]['weight']>=0)
                            edge_CA = (G[node_C][node_A]['weight']>=0)
                            if (edge_AB and edge_BC and edge_CA) or (edge_AB + edge_BC + edge_CA == 1):
                                balanced_triplets += 1
                            elif (edge_AB + edge_BC + edge_CA == 0):
                                unbalanced_triplets += 1
                                unbalanced_triplets_all_negatives += 1
                            elif (edge_AB + edge_BC + edge_CA == 2):
                                unbalanced_triplets += 1
                                unbalanced_triplets_one_negative += 1
                            else:
                                errors += 1
   
    print("Total number of Nodes:", len(node_list))
    print("Total number of Edges:", G.number_of_edges())
    print("Maximum possible Edges:", ((len(node_list))*(len(node_list)-1)*(len(node_list)-2)/6))
    print("Edge Density:", (G.number_of_edges()*6.0/((len(node_list))*(len(node_list)-1)*(len(node_list)-2))))
    print("balanced_triplets:",balanced_triplets)
    print("unbalanced_triplets:",unbalanced_triplets)
    print("unbalanced_triplets_all_negatives:",unbalanced_triplets_all_negatives)
    print("unbalanced_triplets_one_negative:",unbalanced_triplets_one_negative)
    print("errors:",errors)


# Test if the input is a real user_id or anonymous
def is_anonymous(num):
    try:
        int(num)
        return False
    except ValueError:
        return True
        
## Test is_anonymous
#def test_is_anonymous():
#    result = is_anonymous(45)
#    print result
#test_is_anonymous()



    

# Create a new graph where there will be a edge only between reverter and reverted (thereby omitting revertedTo)
def create_undirected_reverter_reverted_network(inputFile):
    op_path = "~/WikiAnalysis/Wikidumps/Output_Logs/reverts_network.gml"

    G = initialize_undirected_wiki_graph()
    
    
    for lines in inputFile:
        if lines[0] != '#':
            words = lines.split(",")
            reverter = words[0].strip()
            reverted = words[2].strip()
            include_in_network_only_reverter_reverted(G,reverter,reverted)
        else:
            #New pageID
            print(lines)
            continue
    nx.write_gml(G,op_path)
    graph_properties(G)


# Called from create_Directed_reverter_reverted_network()    
def include_in_network_only_reverter_reverted(G,reverter,reverted):
    update_users(G,reverter)
    update_users(G,reverted)
    update_user_links(G,reverter,reverted,1)
    return    


def main():
    primary_ip_dir = "~/WikiAnalysis/Wikidumps/Output_Logs/"
    inputpath = primary_ip_dir+"reverts_.log"
    inputFile = open(inputpath, "rb")
    create_undirected_reverter_reverted_network(inputFile)
    inputFile.close()


main()
