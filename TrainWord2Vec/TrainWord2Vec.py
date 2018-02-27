
# coding: utf-8

import pandas as pd
import re
import numpy as np
from gensim.models import word2vec
import logging

logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(message)s', level = logging.INFO)


#parsing '<python><java>' into a list of ['python','java']
def tag_to_taglist(tags):
    tag_cleaned = re.sub('[<>]',' ',tags)
    tags_list = tag_cleaned.split()
    return tags_list


def TrainWord2Vec(skipgram,features,windows,minfrequency,location):
    
    #dataframe that contains tags for each post
    df = pd.read_csv(location, names = ['Tags'])

    tags_groups = [] #a list of lists, [['python','java'],['c','web']]..
    for row in df['Tags'][1:]: #print(df['Tags'][0]) --> Tags, starts from index 1
        tags_groups.append(tag_to_taglist(row))

    #define word2vec parameters
    num_features = features
    min_word_count = minfrequency
    num_workers = 2
    context = windows
    downsampling = 1e-3
    skipgram = skipgram

    print('Training model...')
    model = word2vec.Word2Vec(tags_groups, workers = num_workers,\
                              size = num_features, min_count = min_word_count,\
                              window = context, sample = downsampling, sg = skipgram)
    model.init_sims(replace = True)
    model_name = str(num_features)+'features_'+str(min_word_count)+'minwords_'+str(context)+'windows_'+str(skipgram)+'skipgram'
    model.save(model_name)

def checksimilar(tag,similar_tag,tag_category):
    
    if tag in tag_category.keys() and similar_tag in tag_category.keys():
        tag_cate = tag_category[tag]
        simi_cate = tag_category[similar_tag]
        #make sure all of them exist in tag_category
    else:
        return False
    
    #import similar groups
    similarGroups = []
    f = open('categoryGroup.txt',encoding = 'utf8')
    lines = f.readlines()
    for line in lines:
        similargroup = line.strip().split()
        similarGroups.append(similargroup)
    
    #construct taboo list that contains tags that are too general to be compared
    tabooList1 =['database','file','class','function','server','algorithm',\
                 'performance','exception','events','video','image','networking',\
                 'browser','memory','graph','download','reference','path','transactions',\
                 'sdk','camera','datatables','framework','frameworks','operating-system',\
                 'ide','format','terminology','applet','controls','return','sql-update',\
                 'documentation','embedded','label','closures','iterations','client',\
                 'cloud','components','character','ms-office','text-files','prepared-statement',\
                 'android-manifest','version','overflow','screen','programming-languages', \
                 'keyboard-shortcuts','open-source','accessibility','instance','distinct',\
                 'clone', 'customization','overloading','limit','state','monitoring',\
                 'native', 'packages', 'transition','center','game-engine','device',\
                 'repeater', 'apply','web-api','microcontroller','declaration',\
                 'add-in', 'libraries','remote-access','resultset','patch','intervals',\
                 'hybrid-mobile-app','instruments', 'actor', 'version', 'multilingual',\
                 'point','delete-file', 'keyboard-events', 'analysis','static-analysis',\
                 'pseudocode', 'using', 'crash-reports', 'exists', 'absolute', 'multilanguage',\
                 'filesize', 'software-design','mobile-application','production', 'dimensions',\
                 '2d-games','custom-data-attribute', 'temporary-files', 'material',\
                 'agent','file-type','test-case','class-method', 'in-memory-database',\
                 'toolkit','jquery-tools', 'github-for-windows', 'collaboration','review']
    df = pd.read_csv('manualCategory.csv',names = ['Cate','CatePlural'])
    tabooList2 = []
    for key,value in df.iterrows():
        tabooList2.append(value['Cate'])
        tabooList2.append(value['CatePlural'])    
    tabooList = set(tabooList1 + tabooList2)
    
    similar = False
    #check if they are similar tags
    if tag_cate == 'null' or simi_cate == 'null' :
        similar = False
    #compare their categories
    elif tag_cate == simi_cate:
        similar = True
    else:
        for group in similarGroups:
            if tag_cate in group and simi_cate in group:
                similar = True
                break

    if similar:
        #if they are similar, check whether they are taboo words（too general to compare),or they have length of less than 3
        for k in [tag,similar_tag]:
            #check k, delete tag pair who have tags of length 1 or 2
            #delete tag pair who have key word  'database', 'file', 'class','server','function',...(these are too general to be compared)
            if len(k) < 3:
                similar = False
                break
            if k in tabooList:
                similar = False
                break
                
    if not similar:
        return False
    else:
        return True
        

def ExamineModel(model_name, most_similar_topn,min_similarity):

    model = word2vec.Word2Vec.load(model_name)

    #import tag_category list for checksimilar() function
    tag_category = {}
    #to be passed into pandas
    location_tag_cate = 'Tag_Category.csv'
    #dataframe that contains tags for each post
    df = pd.read_csv(location_tag_cate,names = ['Tag','Category'])
    for index,row in df.iterrows():
        tag_category[row['Tag']] = row['Category']

    tag_frequency_array = []

    #build an array according to tags' frequency
    for key,value in model.wv.vocab.items():
        count = value.count
        new_tuple = (key,count) #python, its_frequency
        tag_frequency_array.append(new_tuple)

    #sort the array according to tags' frequency
    dtype = [('tag','S50'),('frequency',int)]
    array_bf_sort = np.array(tag_frequency_array,dtype = dtype)
    tag_frequency_sorted = np.sort(array_bf_sort, order = 'frequency')[::-1]

    for tag_freq in tag_frequency_sorted[:5]:
        tag = str(tag_freq[0],'utf-8')
        most_similar_60 = model.wv.most_similar(tag,topn = most_similar_topn)
        tag_similar_list = []
        tag_similar_list.append(tag)
        for word in most_similar_60:
            if word[1]>min_similarity:
                if checksimilar(tag, word[0], tag_category):
                    tag_similar_list.append(word[0])
        print(tag_similar_list)

if __name__ == '__main__':
    
    model_name = '600features_10minwords_1windows_1skipgram'
    most_similar_topn = 60 #w2v parameters
    min_similarity = 0.6 #w2v parameters
    skipgram = 1 #w2v parameters
    features = 600 #w2v parameters
    windows = 1 #w2v parameters
    minfrequency = 10 #w2v parameters
    location = 'Id_CleanedTags.csv'#location of the csv file containing Id, Tags for each post, to be passed into pandas
    
    try:
        TrainWord2Vec(skipgram,features,windows,minfrequency,location)
        ExamineModel(model_name, most_similar_topn,min_similarity)
    except Exception as e:
        print('There are exceptions')
        print(e)
        raise
        
        
        