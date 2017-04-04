# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 12:07:27 2015

@author: mrinmoymaity
"""

import networkx as nx 
import numpy as np
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
import math
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
    
def user_network_visualizations(path, input_gml):

    G = nx.read_gml(input_gml)
    
    weights = []
    for source,dest,attr in G.edges(data=True):
        weights.append(attr['weight'])
    visualize_histogram(path,weights,input_gml)
#    visualize_user_network_custom_layout(path, G)
#    visualize_user_network_networkx_layout(path, G)

def visualize_histogram(path,weights,file):
    op_path = path_extraction(path, 2)+"\Histograms\\"+filename_extraction(path)+".png"
#    print op_path
    x = np.array(weights)
    if (max(x)-min(x))>0:
        plt.hist(x, facecolor='green', bins = max(x)-min(x))
    else:
        plt.hist(x, facecolor='green')
    plt.xlabel('# Agreement among Users')
    plt.ylabel('Frequencies')
    plt.title("User Agreements")
    plt.savefig(op_path)
    plt.show()


def visualize_user_network_networkx_layout(path,G):
    options = ['spring','circular','spectral','shell','random']
    pos_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 0]
    neg_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] < 0]
    neutral_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] == 0]
    
    #print(pos_edges,neg_edges, neutral_edges)
    for option in options:
        node_pos = networkx_layout_options(G, option)
        nx.draw_networkx_nodes(G, node_pos, node_size=10)
        nx.draw_networkx_edges(G,node_pos,edgelist=pos_edges,width=1,alpha=0.5,edge_color='b')
        nx.draw_networkx_edges(G,node_pos,edgelist=neg_edges,width=1,alpha=0.5,edge_color='g')
        nx.draw_networkx_edges(G,node_pos,edgelist=neutral_edges,width=1,edge_color='y')
        op_file = path_extraction(path, 2)+"\Networkx Graph Visualizations\\"+filename_extraction(path)+"_"+option+".png"
        plt.axis('off')
        plt.savefig(op_file) # save as png
        plt.show() # display
        

def networkx_layout_options(G, option):
	
	if option == 'spring':
		return nx.spring_layout(G)
	elif option == 'circular':
		return nx.circular_layout(G)
	elif option == 'spectral':
		return nx.spectral_layout(G)
	elif option == 'shell':
		return nx.shell_layout(G)
	else:
		return nx.random_layout(G)
    
def log_scaling_of_edge_weights(n):
    return math.log10(1+n)+1
    


def visualize_user_network_custom_layout(path, G):
    
    op_path = path_extraction(path, 2)+"\Custom Graph Visualizations\\"+filename_extraction(path)+".pdf"

    X_CENTRE = 500
    Y_CENTRE = 300
    X_UNIT = 700
    Y_UNIT = 1000    
    ZERO = 100
    
    nodes_dict = {}
    
    #Initializing colors for nodes
    colors_file = open("colors.txt",'r')
    colors = colors_file.readlines()
    random.seed()
    random.shuffle(colors)
#    print(colors)
    
    if (len(G.nodes()) > 0):
        
        # Below algorithm is for layout structure of the graph. 
        # Taken from "Network Analysis of 
        # Collaboration Structure in Wikipedia" by Brades et. all
        
        # Calculate λ and  λ'
        adj_matrix = nx.to_numpy_matrix(G)
        
#        for i in range(len(adj_matrix)):
#            adj_matrix[i] = map(log_scaling_of_edge_weights, adj_matrix[i])

#        for x_idx in range(len(adj_matrix)):
#            for y_idx in range(len(adj_matrix[x_idx])):
##                mod_weight = math.log10(1 + adj_matrix[x_idx][y_idx]) + 1
##                adj_matrix[x_idx][y_idx] = mod_weight
##                adj_matrix[y_idx][x_idx] = mod_weight
#                print x_idx, y_idx, adj_matrix[x_idx][y_idx]
        
        eigenvalues, eigenvectors = np.linalg.eig(adj_matrix)
        copy_eigenvalues = eigenvalues.copy()
        lambda_min = min(eigenvalues)
        copy_eigenvalues[np.argmin(eigenvalues)] = float("inf")
        lambda_min_prime = min(copy_eigenvalues)
        #Compute eigen vectors associated with  λ and  λ'
        x = eigenvectors[:,np.argmin(eigenvalues)]
        y = eigenvectors[:,np.argmin(copy_eigenvalues)]
#        x = x.flatten()
#        y = y.flatten()
#        print x, y

        if ((lambda_min<0) and (lambda_min_prime<0)):
            y = y*(lambda_min_prime/lambda_min)


       
        # Calculate the node positions
        i = 0        
        node_pos = {} #Collect the node positions
        node_colors = []
        for node in G.nodes():
            
            # Get the co-ordinates from eigen vectors
            x_i = x[i].real
            y_i = y[i].real
            
            # Transpolate the coordinates.
            x_i = min(X_CENTRE + (x_i * X_UNIT), X_CENTRE * 2)
            y_i = min(Y_CENTRE + (y_i * Y_UNIT), Y_CENTRE * 2)
            
            # Avoid nodes going out of the screen.
            x_i = max(x_i, ZERO)
            y_i = max(y_i, ZERO)
            
            # Assign a color to the node.
            if node not in nodes_dict.keys():
                nodes_dict.update({node : len(nodes_dict) +1 })  
            node_color = colors[nodes_dict[node] % len(colors)].rstrip()
            
            node_pos[node] = [np.array(x_i).reshape(-1,).tolist()[0], np.array(y_i).reshape(-1,).tolist()[0]]
            node_colors.append(node_color)
            i = i+1
        

        # Calculate the node sizes based on neighbour counts/total neighbour weights
        node_sizes_neighbour_count = []
        node_sizes_neighbouring_weights = []
        for node in G.nodes():
            out_neighbours = 0
            neighbouring_wt = 0
            for neighbour in nx.all_neighbors(G, node):
                out_neighbours += 1
#                neighbouring_wt += G[node][neighbour]#['weight']
            node_sizes_neighbouring_weights.append(neighbouring_wt*50)
            node_sizes_neighbour_count.append(out_neighbours*100)
        # Normalize the nodes
        range_node_sizes_neighbour_count = max(node_sizes_neighbour_count)-min(node_sizes_neighbour_count)
        for idx in range(len(node_sizes_neighbour_count)):
            node_sizes_neighbour_count[idx] = node_sizes_neighbour_count[idx]*100//range_node_sizes_neighbour_count
        print node_sizes_neighbour_count
#        print node_sizes_neighbouring_weights
        

#        for i in range(len(adj_matrix)):
#            for j in range(i, len(adj_matrix)):
#                weight = adj_matrix[i,j]
        
        
        # Partitioning the edges
        pos_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 0]
        neg_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] < 0]
        neutral_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] == 0]
        
        plt.figure(figsize=(6,6))
        nx.draw_networkx_nodes(G, pos=node_pos, node_size=node_sizes_neighbour_count)
#        nx.draw_networkx_labels(G, pos=node_pos, font_size=10)
        nx.draw_networkx_edges(G,node_pos, edgelist=pos_edges,width=1,alpha=0.5,edge_color='b')
        nx.draw_networkx_edges(G,node_pos,edgelist=neg_edges,width=1,alpha=0.5,edge_color='g')
        nx.draw_networkx_edges(G,node_pos,edgelist=neutral_edges,width=1,alpha=0.5,edge_color='y')
        plt.axis('off')
        plt.savefig(op_path) # save as png
        plt.show() # display        
    
    colors_file.close()


def main():
    controversial_articles = ["Anarchism","Christianity","Circumcision","George_W._Bush","Global_warming","Jesus","World_Wrestling_Entertainment_roster","Muhammad","United_States"]
    primary_ip_dir = "C:\WikiProject\\"
    internal_ip_dir_anonymous_inclusion_without_details = "Controversial Single Pages Simple Wiki\Anonymous Inclusion Without Details\User Graphs With Anonymous\\"
    internal_ip_dir_anonymous_inclusion_with_IP = "Controversial Single Pages Simple Wiki\Anonymous Inclusion With IP Address\User Graphs With Anonymous\\"
    internal_ip_dir_only_anonymous = "Controversial Single Pages Simple Wiki\Only Anonymous\User Graphs With Anonymous\\"
    internal_ip_dir_anonymous_inclusion_without_details_wiki = "Controversial Single Pages Wikipedia\Anonymous Inclusion With IP Address\User Graphs With Anonymous gml\\"
    internal_ip_dir_reverter_reverted_network = "Controversial Single Pages Wikipedia\Anonymous Inclusion With IP Address\Reverter Reverted Networks gml\\" 
    working_ip_dir = internal_ip_dir_reverter_reverted_network
    
    for idx in range(len(controversial_articles)):
        print controversial_articles[idx]
        print "---------------"
        inputpath = primary_ip_dir+working_ip_dir+controversial_articles[idx]+".gml"
        inputFile = open(inputpath,"r")
        user_network_visualizations(inputpath,inputFile)
        inputFile.close()
        
        
main()


#main()
#user_network_visualizations('C:\WikiProject\Controversial Pages Single\User Graphs With Anonymous\Anarchism.gml')
#user_network_visualizations('user_graph.gml')
#user_network_visualizations('test_user_graph.gml')