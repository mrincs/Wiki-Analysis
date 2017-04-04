
import csv
import sys

csv.field_size_limit(sys.maxsize)

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

def preprocess_dict_values(value):
    
    if len(value) == 2:#A length for string '[]'
        return None
    
    value = value[1:len(value)-1]
    values = [int(i) for i in value.split(',')]
    return values

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

def split_pageID_dict(dict):

    num_splits = 30
    new_dict = {}
    
    dict = filter_page_ids_by_num_authors(dict)
    print("Dict length before split:", len(dict))
    print("Expected Dict len:", len(dict)/num_splits)
    
    num_pageids_per_node = 0
    file_idx = 1
    
    for key, val in dict.items():
        new_dict[key] = val
        num_pageids_per_node += 1
        
        if num_pageids_per_node >= len(dict)/num_splits:
            
            print("Saving ", file_idx, " file", ", length: ", len(new_dict))
            outputFileName = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/dict_"+str(file_idx)
            write_dict_to_file(new_dict, outputFileName)
            new_dict = {}
            num_pageids_per_node = 0
            file_idx += 1


def main():
    print("Entering main")
    inputFileName = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/page_edit_list_dict.csv"
    dict = read_dict_from_file(inputFileName)
    split_pageID_dict(dict)

main()