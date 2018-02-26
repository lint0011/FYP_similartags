
# coding: utf-8


import re
import csv


#each rows is in the format of :[45901655,'<spring-security><oauth-2.0>']
#read from csv file, first column is post_id, second column is tags
tagsrows = [] 
with open('Id_Tags.csv') as csvfile:
    rows = csv.reader(csvfile, delimiter = ',')
    for row in rows:
        tagsrows.append(row)


TagNames = [] #import all the tags on StackOverflow
with open('Tags.csv') as csvfile:
    rows = csv.reader(csvfile,delimiter = ',')
    for row in rows:
        TagNames.append(row[0])

#special terms that need to be filtered out when performing cleaning
#A list of list, in the format of ['original term', 'designated term']


special_terms = [['amazon-ec2','amazon-ec2'], ['amazon-s3','amazon-s3'],
                 ['c++1z','c++'],['x11','x11'],['t4','t4'],
                 ['x86','x86'],['x86-64','x86'],['base64','base64'],
                 ['mp3','mp3'],['mp4','mp4'],['v8','v8'],
                 ['flex3','flex'],['h2','h2'],['python-2.x','python'],
                 ['8086','8086'], ['h.264', 'h.264'],['flex4','flex'],
                 ['x509','x509'],['flex4.5','flex'],['z3','z3'],
                 ['opencv3.0','opencv'],['python-3.x','python'],
                 ['opencv3.2','opencv'],['tr2','tr']
                 ]

updated_rows = [] #arrays to host rows that needs to be updated
no_change = [] #arrays with rows of no change


#each rows is in the format of :[45901655,'<spring-security><oauth-2.0>']
for row in tagsrows:
    
    #firstly, check tags is not None
    if row[1] is not None:
        
        #proceed to do cleaning
        id = row[0]
        original_tags = row[1]
        
        #track whether tags are cleaned and changed
        changed = False
        
        #updated row
        new_row = []
        
        #split tags into seperate tag
        subbed_tags = re.sub('<|>',' ', original_tags)
        split_tags = subbed_tags.split()
        
        #for each tag, perform the cleaning:
        for i, tag in enumerate(split_tags):
            
            original_tag = tag
            temp_tag = tag
            cleaned_tag = None
            
            #firstly, check whether it is one of the special terms
            for term in special_terms:
                if original_tag == term[0]:
                    cleaned_tag = term[1]
                    break #tag is cleaned
                    
            if cleaned_tag is None: #tag is not cleaned yet
                #check whether it ends with 'N(.Nxrv)'
                #need to check multiple times because there can be tags with format of 'python-3.6-v2'
                while bool(re.search('[xvr]*[0-9.]+$',temp_tag)):
                    if bool(re.search('-[xvr]*[0-9.]+$',temp_tag)):
                        temp_tag = re.sub('-[xvr]*[0-9.]+$','',temp_tag)
                    else:
                        temp_tag = re.sub('[xvr]*[0-9.]+$','',temp_tag)
                        
                #at the end of the while loop, the temp_tag doesn't contain any uncleaned format
                cleaned_tag = temp_tag
            
            #if cleaned tag is not the same as the original tag, need to update
            if cleaned_tag != original_tag:
                
                #check if the cleaned tag exists in the tags on stackoverflow, if not,
                #the cleaned tag is not valid as a tag name, continue to use original tag
                if cleaned_tag in TagNames:
                    split_tags[i] = cleaned_tag
                    changed = True
                else:
                    print(cleaned_tag + 'doesn\'t exist on StackOverflow')
        
        if changed: 
            #now that tags are all cleaned, put them back into the format of '<python><java><c>'
            #note that this will change the order of the tags(rank in alphabetical order)
            split_tag_set = set(split_tags)
            #join them by <>
            cleaned_tags = '<'+"><".join(split_tag_set)+'>'
            #append id to new_row
            new_row.append(id)
            #append cleaned tags
            new_row.append(cleaned_tags)
            #append new row to updated row
            updated_rows.append(new_row)
            
        else:
            #only delete repetitive tags
            split_tag_set = set(split_tags)
            #join them by <>
            cleaned_tags = '<'+"><".join(split_tag_set)+'>'
            #append id to new_row
            new_row.append(id)
            #append cleaned tags
            new_row.append(cleaned_tags)
            #append new row to updated row
            no_change.append(new_row)


csvfile = 'Id_CleanedTags.csv'
with open(csvfile,'w') as output:
    writer = csv.writer(output,lineterminator = '\n')
    writer.writerow(['Id','Tags'])
    if no_change is not None:
        writer.writerows(no_change)
    if updated_rows is not None:
        writer.writerows(updated_rows)

