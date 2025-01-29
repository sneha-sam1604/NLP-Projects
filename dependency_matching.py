'''
Created on Nov 8, 2019
Sample structure of run file run.py

@author: cxchu
'''

import sys

import spacy 
import nltk

from spacy.matcher import DependencyMatcher 
#from spacy import displacy 
from nltk.corpus import wordnet as wn

def your_typing_function(input_file, result_file):
    
    '''
    This function reads the input file (e.g. test.tsv)
    and does typing all given entity mentions.
    The results is saved in the result file (e.g. results.tsv)
    '''
    fout = open(result_file, 'w', encoding='utf8')
    fin = open(input_file, 'r', encoding='utf8')
    for line in fin.readlines():
        comps = line.rstrip().split("\t")
        id = int(comps[0])
        entity = comps[1]
        sentence = comps[2]

        nlp = spacy.load("en_core_web_sm")
        matcher = DependencyMatcher(nlp.vocab)

        types=[]
        synsets_list = []
        
        doc = nlp(str(sentence))

        # for token in doc: 
        #     print(token.text, "-->",token.dep_,"-->", token.pos_)
        # displacy.serve(doc, style="dep")

        pattern = [
        [  #for "IS", "WAS", "ARE", "WERE" with attribute and no amods or compounds
            {
                "RIGHT_ID": "anchor_root",       
                "RIGHT_ATTRS": {"LEMMA": "be"}
            },
            {
                "LEFT_ID": "anchor_root",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr",
                "RIGHT_ATTRS": {"DEP": "attr"},
            }
        ],

        [   #for "IS", "WAS", "ARE", "WERE" with attribute and no amods or compounds
            {
                "RIGHT_ID": "anchor_root",       
                "RIGHT_ATTRS": {"LEMMA": "be"}
            },
            {
                "LEFT_ID": "anchor_root",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr",
                "RIGHT_ATTRS": {"DEP": "attr"},
            },
            {
                "LEFT_ID": "root_attr",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr_modifier",
                "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound", "conj", "pobj"]}},
            }
        ],

        [   #for "IS", "WAS", "ARE", "WERE" with attribute and no amods or compounds
            {
                "RIGHT_ID": "anchor_root",       
                "RIGHT_ATTRS": {"LEMMA": "be"}
            },
            {
                "LEFT_ID": "anchor_root",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr",
                "RIGHT_ATTRS": {"DEP": "attr"},
            },
            {
                "LEFT_ID": "root_attr",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr_prep",
                "RIGHT_ATTRS": {"DEP": "prep"}
            },
            {
                "LEFT_ID": "root_attr_prep",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr_prep_pobj",
                "RIGHT_ATTRS": {"DEP": "pobj"}
            },
            {
                "LEFT_ID": "root_attr_prep_pobj",
                "REL_OP": ">",
                "RIGHT_ID": "root_attr_pobj_more",
                "RIGHT_ATTRS": {"DEP": {"IN": ["compound", "amod"]}}
            }
        ],

        [   #for "includes" with attribute and dobj and no conj
        {
            "RIGHT_ID": "root_include",
            "RIGHT_ATTRS": {"ORTH": {"IN": ["include", "includes"]}}  
        },
        {
            "LEFT_ID": "root_include",
            "REL_OP": ">",
            "RIGHT_ID": "include_dobj",
            "RIGHT_ATTRS": {"DEP": {"IN": ["dobj", "nsubj"]}}
        }
        ],

        [   #for "includes" with attribute and dobj and conj
            {
                "RIGHT_ID": "root_include",      
                "RIGHT_ATTRS": {"ORTH": {"IN": ["include", "includes"]}}  
            },
            {
                "LEFT_ID": "root_include",
                "REL_OP": ">",
                "RIGHT_ID": "include_dobj",
                "RIGHT_ATTRS": {"DEP": {"IN": ["dobj", "nsubj"]}}
            },
            {
                "LEFT_ID": "include_dobj",
                "REL_OP": ">",
                "RIGHT_ID": "dobj_conj",
                "RIGHT_ATTRS": {"DEP": "conj"}
            }
        ]
        ]

        matcher.add("is_or_was", pattern)
        matches = matcher(doc)
        
        if len(matches) != 0:
            match_id, tokens = matches[0]
            for ind in range(1, len(tokens)):
                types.append(doc[tokens[ind]].text)
            #     synsets = wn.synsets(doc[tokens[ind]].text) #getting the synonym sets
            #     for syn in synsets:
            #         hypernyms = syn.hypernyms() #getting the hypernyms of the synonyms
            #         for hyp in hypernyms:
            #             synsets_list += hyp.lemma_names()
            #         synsets_list = list(set(synsets_list)) #final list of hypernyms

            # types = (list(set(types + synsets_list)))

        fout.write(str(id) + "\t" + str(types) + "\n")
        
    fout.close()
    
    
'''
*** other code if needed
'''    
    
    
'''
main function
'''
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError('Expected exactly 2 argument: input file and result file')
    your_typing_function(sys.argv[1], sys.argv[2])

#References:
#https://spacy.io/usage/rule-based-matching
#https://www.youtube.com/watch?v=gUbMI52bIMY
#https://github.com/explosion/spaCy/discussions/10396
#https://sp1819.github.io/wordnet_spacy.pdf
