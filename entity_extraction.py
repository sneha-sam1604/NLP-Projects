'''
Created on Nov 25, 2019
Sample structure of run file run.py

@author: cxchu
@editor: ghoshs
'''
import sys
import csv

import re
import spacy

from spacy.matcher import Matcher
from dateutil.parser import parse

nlp = spacy.load('en_core_web_sm')

def your_extracting_function(input_file, result_file):
    
    '''
    This function reads the input file (e.g. input.csv)
    and extracts the required information of all given entity mentions.
    The results is saved in the result file (e.g. results.csv)
    '''
    with open(result_file, 'w', encoding='utf8', newline="") as fout:
        headers = ['entity','dateOfBirth','nationality','almaMater','awards','workPlaces']
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        
        with open(input_file, 'r', encoding='utf8') as fin:
            reader = csv.reader(fin)

            # skipping header row
            next(reader)
            
            for row in reader:
                entity = row[0]
                abstract = row[1]
                dateOfBirth, nationality, almaMater, awards, workPlace = [], [], [], [], []
                
                '''
                baseline: adding a random value 
                comment this out or remove this baseline 
                '''
                # dateOfBirth.append('1961-1-1')
                # nationality.append('United States')
                # almaMater.append('Johns Hopkins University')
                # awards.append('Nobel Prize in Physics')
                # workPlace.append('Johns Hopkins University')
                
                '''
                extracting information 
                '''

                dateOfBirth += extract_dob(entity, abstract)
                nationality += extract_nationality(entity, abstract)
                almaMater += extract_almamater(entity, abstract)
                awards += extract_awards(entity, abstract)
                workPlace += extract_workpace(entity, abstract)
                
                writer.writerow([entity, str(dateOfBirth), str(nationality), str(almaMater), str(awards), str(workPlace)])
        
    
'''
date of birth extraction funtion
'''    

def extract_dob(entity, abstract, **kwargs):
    dob = []
    '''
    === your code goes here ===
    '''

    doc = nlp(abstract)

    # for token in doc:
    #     print(token.text, token.pos_)

    #possible patterns to find the date of birth from given abstract obtained after pos tagging
    patterns = [
        [ 
            {'LOWER':'born'},
            {'POS':'NUM'},
            {'POS':'PROPN'},
            {'POS':'NUM'}
        ],
        [
            {'LOWER':'born'},
            {'POS':'PROPN'},
            {'POS':'NUM'},
            {'POS':'PUNCT', 'OP':'*'},
            {'POS':'NUM'}
        ]
    ]
    
    matcher = Matcher(nlp.vocab) 
    matcher.add("matching", patterns) 
    matches = matcher(doc)

    if len(matches) != 0:
        for ind in range(0,len(matches)):
            token = doc[matches[ind][1]:matches[ind][2]]
            date = parse(str(token[1:]))
            dob.append(date.strftime('%Y-%m-%d')) #to convert date to format as in groundtruth.csv

    return dob


'''
nationality extraction function
'''
def extract_nationality(entity, abstract, **kwargs):
    nationality = []
    '''
    === your code goes here ===
    '''

    #list of countries and their adjectives (Example: American -> United States) stored in a dictionary
    with open('demonyms.txt', encoding='utf8') as f:
        country_dict = dict(filter(None, csv.reader(f)))
    
    doc = nlp(abstract)

    # for token in doc:
    #     print(token.text, token.pos_)

    #possible patterns to find the nationality from given abstract obtained after pos tagging
    patterns = [
        [
            {'LEMMA':'be'},
            {'ORTH': {'IN': ['a', 'an']}},
            {'POS':'ADJ'},
            {'ORTH':'/', 'OP':'*'},
            {'POS':'ADJ', 'OP':'*'},
            {'POS':'NOUN'}
        ],
        [
            {'LOWER':'born'},
            {'LOWER':'in'},
            {'POS':'PROPN'},
            {'POS':'ADP', 'OP':'*'}
        ]
    ]

    matcher = Matcher(nlp.vocab) 
    matcher.add("matching", patterns) 
    matches = matcher(doc)

    if len(matches) != 0:
        for ind in range(0,len(matches)):
            token = doc[matches[ind][1]:matches[ind][2]]
            words = re.split(" ", str(token))
            for word in words:
                if word[0].isupper() and word!='Born':
                    if word in country_dict:
                        nationality.append(country_dict[word].strip())
                    else:
                        nationality.append(word.strip())

    return list(set(nationality))
 

'''
alma mater extraction function
'''
def extract_almamater(entity, abstract, **kwargs):
    almaMater = []
    '''
    === your code goes here ===
    '''
    sentences = abstract.split(".")

    verbs = ['graduated', 'educated', 'study', 'studied', 'degree', 'degrees', 'doctorate', 'scholarship', 'PhD','B.A.', 'former fellow', 'doctorates', 'honorary', 'B.S.']

    for sent in sentences:
        doc = nlp(sent)
        res = [ele for ele in verbs if(ele in sent)] #finding only those sentences with the above verbs in them
        if res:
            for token in doc.ents:
                if token.label_ == "ORG": #using NER to find organizations
                    almaMater.append(token.text.replace("the","").strip())

    return list(set(almaMater))


'''
awards extracttion function
'''
def extract_awards(entity, abstract, **kwargs):
    awards = []
    '''
    === your code goes here ===
    '''
    doc = nlp(abstract)

    words = ['Award','Prize','award','prize','Medal','doctorate', 'Fellowship', 'Emeritus','Preis']

    for noun_chunk in doc.noun_chunks:
        res = [ele for ele in words if(ele in noun_chunk.text)] #finding only those noun chunks which have the above words in them
        if res:
            awards.append(noun_chunk.text.replace("the","").strip())

    return list(set(awards))


'''
workplace extraction function
'''
def extract_workpace(entity, abstract, **kwargs):
    workPlace = []
    '''
    === your code goes here ===
    '''

    doc = nlp(abstract)

    words = ['work', 'worked', 'working', 'inducted', 'position','working','Professor', 'Lecturer', 'Founder', 'University', 'College', 'Laboratory', 'Institute']
    
    for token in doc.ents:
        res = [ele for ele in words if(ele in token.text)] #finding only those sentences which have above words
        if res:
            if token.label_ == "ORG": #using NER to find organizations
                place = token.text.replace("the","").strip()
                workPlace.append(place)

    return list(set(workPlace))


'''
main function
'''
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError('Expected exactly 2 argument: input file and result file')
    your_extracting_function(sys.argv[1], sys.argv[2])


#References:
#https://spacy.io/usage/rule-based-matching
#https://www.analyticsvidhya.com/blog/2020/06/nlp-project-information-extraction/
#https://github.com/knowitall/chunkedextractor/blob/master/src/main/resources/edu/knowitall/chunkedextractor/demonyms.csv
#https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
#https://stackoverflow.com/questions/2265357/parse-date-string-and-change-format
