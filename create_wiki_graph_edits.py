    # -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 17:30:35 2015

@author: mrinmoymaity
"""

import networkx as nx
import os
import csv
import sys
import time

csv.field_size_limit(sys.maxsize)

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
        return
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
    op_path = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/reverts_network.gml"

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

def calculate_number_of_revs(dict):
    num_revisions = []
    for key, val in dict.items():
        if val is not None:
            num_revisions.append(len(val))
    return num_revisions

def filter_page_ids_by_num_authors(dict):
    threshold = 10
    num_pages_above_threshold = 0
    mod_dict = {}
    for key, val in dict.items():
        if val is not None and len(val) > threshold:
            mod_dict[key] = val
            num_pages_above_threshold += 1
    print("Number of pages above threshold: ", num_pages_above_threshold)
    print("After Filtering, number of keys", len(mod_dict))
    return mod_dict

def read_dict_from_file(filename):
    dict = {}
    for key, val in csv.reader(open(filename)):
        dict[key] = preprocess_dict_values(val)
    print("Original number of Keys", len(dict))
    return dict

def write_dict_to_file(dict, filename):
    writer = csv.writer(open(filename, "w"))
    for key, val in dict.items():
        writer.writerow([key, val])
    return


def create_dict_by_pageid():
    
    page_level_dict = {}
    inputFile = open("/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/edits_.log", "r")
    outputFileName = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/page_edit_list_dict.csv"
    
    prev_pageID = 10 # First Page ID
    user_list = []
    
    for line in inputFile:
        words = line.split(",")
        pageID = int(words[0])
        if pageID == prev_pageID:
            userID = words[1]
            if is_anonymous(userID):
                continue
            else:
                if userID not in user_list:
                    user_list.append(int(userID))
        else:
            page_level_dict[pageID] = user_list
            prev_pageID = pageID
            user_list = []

    write_dict_to_file(page_level_dict, outputFileName)
    inputFile.close()
    return page_level_dict


def calculate_overlaps_of_authors_between_pages(index):
    
    inputFileName_global="/N/dc2/scratch/mmaity/Wikidicts/page_edit_list_dict.csv"
    inputFileName_local="/N/dc2/scratch/mmaity/Wikidicts/dict_"+str(index)
    #inputFileName_global = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/page_edit_list_dict.csv"
    #inputFileName_local = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/dict_"+str(index)
    outputFileName = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/page_overlaps_"+str(index)+".graphml"
    print("Accessing : ", str(index))
    dict = read_dict_from_file(inputFileName_global)
    local_dict = read_dict_from_file(inputFileName_local)
    #num_revisions = calculate_number_of_revs(dict)
    #distribution_of_pageid_revisions(num_revisions)
    #dict = filter_page_ids_by_num_authors(dict)
    G = initialize_undirected_wiki_graph()

    end = time.time()
    for pageID1, user_list1 in dict.items():
        print("<", pageID1, ">")
        start = end
        for pageID2, user_list2 in local_dict.items():
            #print("<", pageID1, pageID2, ">")
            pageID1 = int(pageID1)
            pageID2 = int(pageID2)
            overlapping_J_coef = find_overlaps_between_two_pageIDs(user_list1, user_list2)
            if overlapping_J_coef != 0:
                update_users(G, pageID1)
                update_users(G, pageID2)
                update_user_links(G, pageID1, pageID2, overlapping_J_coef)
        end = time.time()
        print("Elapsed Time: ",(end-start))

    nx.write_graphml(G, outputFileName)
    return
    
    
def calculate_partial_overlaps_of_authors_between_pages(index1):
    
    
    inputFileName="/N/dc2/scratch/mmaity/Wikidicts/dict_"+str(index1)
    outputFileName = "/N/dc2/scratch/mmaity/Wikidicts/page_overlaps_"+str(index1)+".csv"
    
    dictOriginal = read_dict_from_file(inputFileName)


    with open(outputFileName, 'w', newline='') as csvfile:
        for index2 in range(1,29):
            end = time.time()
            fp = csv.writer(csvfile, delimiter=',')
            inputFileNamePaired="/N/dc2/scratch/mmaity/Wikidicts/dict_"+str(index2)
            dictPaired = read_dict_from_file(inputFileNamePaired)
            start = end
            #print("SubFile: ", index2)
            
            for pageID1, user_list1 in dictOriginal.items():
                #print("<", pageID1, ">")
                
                for pageID2, user_list2 in dictPaired.items():
                    #print("<", pageID1, pageID2, ">")
                    pageID1 = int(pageID1)
                    pageID2 = int(pageID2)
                    overlapping_J_coef = find_overlaps_between_two_pageIDs(user_list1, user_list2)
                    if overlapping_J_coef != 0:
                        fp.writerow([pageID1, pageID2, overlapping_J_coef])
            end = time.time()
            print(index2, ", Elapsed Time: ",(end-start))
    return

def preprocess_dict_values(value):

    if len(value) <= 2:
        return None
            #print(value, len(value))
    value = value[1:len(value)-1]
    values = [int(i) for i in value.split(',')]
    return values


def find_overlaps_between_two_pageIDs(list1, list2):
    
    if list1 is None or list2 is None:
        return 0
    
    #list1 = preprocess_dict_values(list1)
    #list2 = preprocess_dict_values(list2)
    
    if len(list1) > len(list2):
        tmp = list1
        list1 = list2
        list2 = tmp

    common_elm = 0

    for index in range(len(list1)):
        if list1[index] in list2:
            common_elm += 1

    total_elm = len(list1) + len(list2) - common_elm
    return common_elm/total_elm * 1.0




def main():
    print(sys.argv[1])
    #page_level_dict = create_dict_by_pageid()
    #calculate_overlaps_of_authors_between_pages(sys.argv[1])
    calculate_partial_overlaps_of_authors_between_pages(sys.argv[1])



main()
