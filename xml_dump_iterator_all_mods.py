# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 18:05:08 2015

@author: mrinmoymaity: Written in Python-3.4
"""

from mw.xml_dump import Iterator
from mw.xml_dump import Page
from mw.xml_dump import Revision
from mw.lib import reverts
import time
import sys

def read_relevant_pagelinks(ipFile):
    page_ids = []
    with open(ipFile, "r") as f:
        for line in f:
            page_ids.append(int(line))
    return page_ids

# An inefficient version of find_user
# More efficient version implemented below.
#def find_user(edit_list, rev_id):
#    key = None
#    for i in range(len(edit_list)):
#        if edit_list[i][0] == rev_id:
#            key = edit_list[i][1]
#    if key != None:
#        return key
#    else:
#        return -1

# An efficient version of find_user function implemented above
# It uses the assumption that the revisions will be extracted fast if counted 
# down from current revision.
# Also difference from earlier is that for anonymous it returns IP address 
# instead of -1. edit list can contain tuples <revision_id,user_id> or
# <revision_id, anonymous IP>. -1 returned for error cases.
def find_user(edit_list, rev_id):
    for i in range(len(edit_list)-1,0,-1):
        if edit_list[i][0] == rev_id:
            return edit_list[i][1]
    return -1
## Test find_user
#def test_find_user():
#    a = [[10,1],[11,3],[16,4],[19,6]]
#    result = find_user(a,16)
#    print(result)
#test_find_user()

def create_set_of_page_ids(inputFileName):

    ip_dir = "/N/u/mmaity/Karst/WikiAnalysis/Wikidumps/Output_Logs/"
    fp = open(ip_dir+inputFileName, "r")
    page_ids = []
    for lines in fp:
        page_ids.append(int(lines))
    fp.close()
    page_ids = set(page_ids)
    return page_ids


# Parse all pages and create revert history
def parse_all_wiki_articles_for_rev_history(xml_stub_history, xml_file_no):

    #primary_op_dir = "C:\WikiProject\\"
    #internal_op_dir = "Controversial Single Pages Wikipedia\Wikidumps\Revisions\All Revisions\\"
    primary_op_dir = "/N/u/mmaity/Karst/"
    internal_op_dir = "WikiAnalysis/Wikidumps/Output_Logs/"
    dump_iter = Iterator.from_file(open(xml_stub_history,encoding='latin-1'))
    tot_file_ct = 0
    
    start = time.time()
    
    
    output_file_reverts = open(primary_op_dir+internal_op_dir+"reverts_"+str(xml_file_no)+".log", mode='w', encoding='utf-8')
    output_file_edits = open(primary_op_dir+internal_op_dir+"edits_"+str(xml_file_no)+".log", mode='w', encoding='utf-8')
    page_ids = create_set_of_page_ids("page_ids")
    
    for page_iter in dump_iter:
        if page_iter.id in page_ids:
            print(page_iter.id)
            page = Page(page_iter.id, page_iter.title, page_iter.namespace,  page_iter.redirect, page_iter.restrictions, page_iter.__iter__())
            detector = reverts.Detector()
        
            output_file_reverts.write("#"+str(page_iter.id)+"\n")
            edit_list = []
            for rev_iter in page:
                if rev_iter.contributor.id != None:
                    edit_list.append([rev_iter.id, rev_iter.contributor.id])
                else:
                    edit_list.append([rev_iter.id, rev_iter.contributor.user_text])
            
            
                # Detect reverts and save info in reverts_ file
                revert_info = detector.process(rev_iter.sha1, rev_iter.id)
                if revert_info != None:
                    reverter = find_user(edit_list, revert_info.reverting)
                    revertedTo = find_user(edit_list, revert_info.reverted_to)
                    for i in range(len(revert_info.reverteds)):
                        reverted = find_user(edit_list, revert_info.reverteds[i])
                        output_file_reverts.write(str(reverter)+","+str(revertedTo)+","+str(reverted)+"\n")
        
            # <page_id, user_id, num_of_revs>
            user_list = {}
            for edit_list_iter in edit_list:
                contributor = edit_list_iter[1]
                if contributor in user_list.keys():
                    user_list[contributor] += 1
                else:
                    user_list[contributor] = 1
                
                   
            for item in user_list.items():
                output_file_edits.write(str(page_iter.id)+","+str(item[0])+","+str(item[1])+"\n")
        else:
            print(page_iter.id, "Not Found")
                        
 
    output_file_reverts.close()
    output_file_edits.close()
    end = time.time()
    
    print(xml_stub_history)
    print("Total File Count:", tot_file_ct) 
    print("Elapsed Time:", (end-start))   


def main(argv):
    xml_file_no = sys.argv[1]
    xml_stub_history_simple_wiki = "/N/dc2/scratch/mmaity/Wikidumps/enwiki-20150602-stub-meta-history"+str(xml_file_no)+".xml"
#"""
#xml1 : 1
#xml2 : 10K - 25K
#xml3 : 25K - 55K
#xml4 : 55K - 105K
#xml10 : 925000
#xml12:  1825000
#xml13 : 2420000
#xml14 : 3120000
#xml15 : 3920000
#xml18 : 7500000
#xml19 : 9220000
#xml20 : 11000000
#"""
#    xml_stub_history_wikipedia = "C:\WikiProject\Wikipedia Dumps\enwiki-20150304-stub-meta-history10.xml"
#    parse_simple_wiki_controversial_articles(xml_stub_history_simple_wiki)
#    parse_wikipedia_controversial_articles(xml_stub_history_wikipedia)    
    parse_all_wiki_articles_for_rev_history(xml_stub_history_simple_wiki, xml_file_no)



if __name__=='__main__':
    main(sys.argv)

#parse_revisions()
