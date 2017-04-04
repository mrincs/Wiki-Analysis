# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 18:05:08 2015

@author: mrinmoymaity: Written in Python-3.4
"""

from mw.xml_dump import Iterator
from mw.xml_dump import Page
from mw.xml_dump import Revision
from mw.lib import reverts
import wikipedia




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


# Construct dump file iterator

def parse_revisions(xml_dump, output_file):
    dump_iter = Iterator.from_file(open(xml_dump,encoding='latin-1'))
    #print("------------Site Metadata----------------", file=output_file)
    #print("\nSiteName: ",dump_iter.site_name,"\nBase: ",dump_iter.base,"\nGenerator:        ",dump_iter.generator,"\nCase: ",dump_iter.case, file=output_file)
      
      #page_iter_idx = 0 # Number of pages
      #cumulative_rev_iter_idx = 0 # Total number of revisions of all pages
      ## Iterate through pages
      #for page_iter in dump_iter:
      #    page_iter_idx = page_iter_idx+1
      #    rev_iter_idx = 0
      #    # Iterate through a page's revisions
      #    for revision_iter in page_iter:
      #        rev_iter_idx = rev_iter_idx+1
      #        cumulative_rev_iter_idx = cumulative_rev_iter_idx+1
      #        #print(revision_iter.id)
      #        
      #print(page_iter_idx, cumulative_rev_iter_idx)

    page_iter_idx = 0 # Number of pages
    for page_iter in dump_iter:
        if page_iter_idx < 1000:
            page_iter_idx = page_iter_idx+1
            page = Page(page_iter.id, page_iter.title, page_iter.namespace,  page_iter.redirect, page_iter.restrictions, page_iter.__iter__()) 
            #print("\n",page_iter_idx,". PageID: ",page.id, file=output_file)
            output_file.write("#\n")
            rev_iter_idx = 0
            detector = reverts.Detector()
            edit_list = []
            for rev_iter in page:
                rev_iter_idx = rev_iter_idx+1
#                revision = Revision(rev_iter.id, rev_iter.timestamp)
                edit_list.append([rev_iter.id, rev_iter.contributor.id])
                #print(edit_list, file=output_file)
                #print("\n\t",rev_iter_idx,".",rev_iter,"\n", file=output_file)
                revert_info = detector.process(rev_iter.sha1, rev_iter.id)
                if revert_info != None:
                    reverter = find_user_including_anonymous(edit_list, revert_info.reverting) 
                    revertedTo = find_user_including_anonymous(edit_list, revert_info.reverted_to)
                    for i in range(len(revert_info.reverteds)):
                        reverted = find_user_including_anonymous(edit_list, revert_info.reverteds[i])
                        output_file.write(reverter,",",revertedTo,",",reverted,"\n")


# Output is saved in <page_title>.log file.
# Format of Output <reverter, revertedTo, reverted>.
# For anonymous cases, -1 is saved
def parse_specific_pages_given_pageID(xml_dump, page_id, output_file):
    dump_iter = Iterator.from_file(open(xml_dump,encoding='latin-1'))
    for page_iter in dump_iter:
        print(page_iter.id, page_id)
        if page_iter.id == page_id:
            page = Page(page_iter.id, page_iter.title, page_iter.namespace,  page_iter.redirect, page_iter.restrictions, page_iter.__iter__()) 
            rev_iter_idx = 0
            detector = reverts.Detector()
            # edit_list contains tuples <revision_id, user_id> to track previous revisions
            edit_list = []
            for rev_iter in page:
                rev_iter_idx = rev_iter_idx+1
                edit_list.append([rev_iter.id, rev_iter.contributor.id])
                revert_info = detector.process(rev_iter.sha1, rev_iter.id)
                if revert_info != None:
                    reverter = find_user(edit_list, revert_info.reverting) 
                    revertedTo = find_user(edit_list, revert_info.reverted_to)
                    for i in range(len(revert_info.reverteds)):
                        reverted = find_user(edit_list, revert_info.reverteds[i])
                        output_file.write(reverter,",",revertedTo,",",reverted,"\n")
            break


# Output is saved in <page_title>.log file.
# Format of Output <reverter, revertedTo, reverted>.
# For anonymous cases, IP is saved
def parse_specific_pages_given_pageID_anonymous(xml_dump, page_id, output_file):
    dump_iter = Iterator.from_file(open(xml_dump,encoding='latin-1'))
    for page_iter in dump_iter:
        if page_iter.id == page_id:
            page = Page(page_iter.id, page_iter.title, page_iter.namespace,  page_iter.redirect, page_iter.restrictions, page_iter.__iter__()) 
            rev_iter_idx = 0
            detector = reverts.Detector()
            # edit_list contains tuples <revision_id, user_id> to track previous revisions. For anonymous, saved in form -1,<IP address>
            edit_list = []
            for rev_iter in page:
                rev_iter_idx = rev_iter_idx+1
                if rev_iter.contributor.id != None:
                    edit_list.append([rev_iter.id, rev_iter.contributor.id])
                else:
                    edit_list.append([rev_iter.id, rev_iter.contributor.user_text])
                revert_info = detector.process(rev_iter.sha1, rev_iter.id)
                if revert_info != None:
                    reverter = find_user(edit_list, revert_info.reverting) 
                    revertedTo = find_user(edit_list, revert_info.reverted_to)
                    for i in range(len(revert_info.reverteds)):
                        reverted = find_user(edit_list, revert_info.reverteds[i])
                        output_file.write(reverter,",",revertedTo,",",reverted,"\n")
            break


# Entry Function for parsing simple wiki controversial article. Takes a lists of
# <page_title, page_id>. Parses the xml dump to find all the reverts given page_id.
# Output is saved in <page_title>.log file in specified directory
def parse_simple_wiki_controversial_articles(xml_stub_history):
    # Used for Single Pages of Controversial articles of Simple Wiki
    primary_ip_dir = "C:\WikiProject\\"
    internal_ip_dir = "Controversial Single Pages Simple Wiki\\"
    input_filename = "simple_wiki_page_ids.txt"
    primary_op_dir = "C:\WikiProject\\"
    internal_op_dir = "Controversial Single Pages Simple Wiki\Revision Logs\\"
    
    #Parse Input file and create dictionary
    input_file = open(primary_ip_dir+internal_ip_dir+input_filename,'r')
    for line in input_file:
        parts = line.split() # Line Format <page_title, page_id>
        page_title = parts[0]
        page_id = int(parts[1])
        print("Parsing for ",page_title,"...")
        #output_file = open('revision_1000.log', mode='w', encoding='utf-8')
        output_file = open(primary_op_dir+internal_op_dir+page_title+".log", mode='w', encoding='utf-8')
        #parse_revisions(xml_stub_history, output_file)
        #parse_specific_pages_given_pageID(xml_stub_history,page_id,output_file)
        parse_specific_pages_given_pageID_anonymous(xml_stub_history,page_id,output_file)
        output_file.close()
        print("Created ",page_title,".log in: ", primary_op_dir,internal_op_dir)



def find_page_id_given_page_title(title):
    try:
        page = wikipedia.page(title.strip())
        if page is not None:
            return page.pageid.strip()
        return -1
    except wikipedia.exceptions.PageError:
        return -1

## Test find_page_id_given_page_title
#def test_find_page_id_given_page_title():
#    print(find_page_id_given_page_title("George_W._Bush "))
#    
#test_find_page_id_given_page_title()

def parse_wikipedia_controversial_articles(xml_stub_history):
    primary_ip_dir = "C:\WikiProject\\"
    internal_ip_dir = "Controversial Single Pages Wikipedia\\"
    controversial_page_titles_fileName = "controversial_page_titles.txt"
    controversial_page_ids_fileName = "controversial_wikipedia_page_ids.txt"
    
    # Create page_ids file corresponding to page_titles
    inputFile = open(primary_ip_dir+internal_ip_dir+controversial_page_titles_fileName,'r')
    outputFile = open(primary_ip_dir+internal_ip_dir+controversial_page_ids_fileName,'w')
    
    for title in inputFile:
        outputFile.write(title.strip()+" "+find_page_id_given_page_title(title))
        outputFile.write("\n")
    
    inputFile.close()
    outputFile.close()
    
    # Parse xml_dump to retrieve the reverts of controversial pages
    inputFile = open(primary_ip_dir+internal_ip_dir+controversial_page_ids_fileName, 'r')

    titles = []
    pageID = []
    for line in inputFile:
        parts = line.split()
        titles.append(parts[0].strip())
        pageID.append(int(parts[1]))
    
    inputFile.close()
    
    inputFile = open(xml_stub_history,'r',encoding='utf-8')
    article_count = 0    
    dump_iter = Iterator.from_file(inputFile)
    for page_iter in dump_iter:
        print(page_iter.id)
        if page_iter.id in pageID:
            article_count += 1
            try:
                item_idx = pageID.index(page_iter.id)
            except ValueError:
                continue
            outputFile = open(primary_ip_dir+internal_ip_dir+"Anonymous Inclusion With IP Address\Revision Logs\\"+titles[item_idx]+".log", mode='w', encoding='utf-8')
            page = Page(page_iter.id, page_iter.title, page_iter.namespace,  page_iter.redirect, page_iter.restrictions, page_iter.__iter__()) 
            rev_iter_idx = 0
            detector = reverts.Detector()
            # edit_list contains tuples <revision_id, user_id> to track previous revisions. For anonymous, saved user_id in form <IP address>
            edit_list = []
            for rev_iter in page:
                rev_iter_idx = rev_iter_idx+1
                if rev_iter.contributor.id != None:
                    edit_list.append([rev_iter.id, rev_iter.contributor.id])
                else:
                    edit_list.append([rev_iter.id, rev_iter.contributor.user_text])
                revert_info = detector.process(rev_iter.sha1, rev_iter.id)
                if revert_info != None:
                    reverter = find_user(edit_list, revert_info.reverting) 
                    revertedTo = find_user(edit_list, revert_info.reverted_to)
                    for i in range(len(revert_info.reverteds)):
                        reverted = find_user(edit_list, revert_info.reverteds[i])
                        outputFile.write(str(reverter)+","+str(revertedTo)+","+str(reverted))
                        outputFile.write("\n")
        
        outputFile.close()
        # All articles found
        if (article_count == len(pageID)):
            break
    inputFile.close()
        
        

# Page Links in level1 from Anarchism -simple wiki

def main():
    xml_stub_history_simple_wiki = "C:\WikiProject\Simple Wiki dumps\simplewiki-20141222-stub-meta-history.xml"
#"""
#xml1 : 1
#xml2 : 10000
#xml3 : 25000
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
    parse_simple_wiki_controversial_articles(xml_stub_history_simple_wiki)
#    parse_wikipedia_controversial_articles(xml_stub_history_wikipedia)    



if __name__=='__main__':
    main()