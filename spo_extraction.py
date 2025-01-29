'''
Created on Nov 25, 2019
Sample structure of run file run.py

@author: cxchu
'''

import sys
import spacy

from spacy.matcher import Matcher
from spacy.util import filter_spans

nlp = spacy.load("en_core_web_sm")

def your_extracting_function(input_file, result_file):
    
    '''
    This function reads the input file (e.g. sentences.tsv)
    and extracts all SPO per line.
    The results are saved in the result file (e.g. results.txt)
    '''

    with open(result_file, 'w', encoding='utf8') as fout:
        with open(input_file, 'r', encoding='utf8') as fin:
            id = 1
            for line in fin:
                line = line.rstrip()
                
                '''
                baseline: running dependency, return head verb, nominal subject and directed object
                comment out or remove when running your code
                verbs = {key: {'subject': text, 'object': text}}
                '''
                #verbs = spo_baseline(line)
                '''
                end baseline
                '''

                '''
                Extracting SPO
                === your code goes here ===
                verbs = extract_spo(line)
                '''
                
                verbs = {}

                doc = nlp(line)

                predicates = get_predicates(doc)

                key = str(get_root(doc))
                if(key not in verbs.keys()):
                    verbs[key] = {"subject":"","object":""}
                
                non_predicates = doc.noun_chunks
                full_predicate = None

                if len(predicates) == 0:
                    continue
                elif len(predicates) > 1:
                    full_predicate = get_full_predicate(list(predicates))
                else:
                    full_predicate = predicates[0]

                subject = get_subject(full_predicate, non_predicates)
                object = get_object(full_predicate, non_predicates)
                
                verbs[key]["subject"] = str(subject)
                verbs[key]["object"] = str(object)
                
                '''
                formatting dict compatible with oie reader
                '''

                if len(verbs) > 0:
                    res = ''
                    for key, value in verbs.items():
                        if value['subject'] != '' and value['object'] != '':
                            res += str(id) + '\t"' + value["subject"] + '"\t"' + key + '"\t"' + value["object"] + '"\t0\n'
                    if res != '':
                        fout.write(line + "\n")
                        fout.write(res) 
                        id += 1

'''
baseline implementation
'''
def spo_baseline(line):
    verbs = {}
    doc = nlp(line)
    for token in doc:
        key=token.head.text;
        if(token.head.pos_ == "VERB" and key not in verbs.keys()):
            verbs[key] = {"subject":"","object":""};
        if(token.dep_ == "nsubj" and token.head.pos_ == "VERB"):
            verbs[key]["subject"] = token.text;
        elif(token.dep_ == "dobj" and token.head.pos_ == "VERB"):
            verbs[key]["object"] = token.text;
    return verbs

    
'''
*** other code if needed
'''    

def get_root(doc):
    #assuming that the verb is usually the root
    for token in doc:
        if (token.dep_ == "ROOT"):
            return token

def check_root(predicate, root):
    #check if the root word is present in the predicate
    start = predicate.start
    end = predicate.end
    if root.i >= start and root.i <= end:
        return True
    else:
        return False

def get_predicates(doc):
    #match phrases with given patterns to obtain predicates
    root = get_root(doc)

    patterns = [
        [
            {"POS":"AUX"},
            {"POS":"VERB"}, 
            {"POS":"ADP"}
        ], 
        [
            {"POS":"NOUN"},
            {"POS":"VERB"},
            {"POS":"PREP", "OP":"*"}
        ],
        [
            {"POS":"NOUN", "OP":"*"},
            {"POS":"SCONJ"},
            {"POS":"VERB"},
            {"POS":"ADP"},
            {"POS":"DET", "OP":"*"}
        ],
        [
            {"POS":"VERB"},
            {"POS":"NOUN", "OP":"*"},
            {"POS":"ADP", "OP":"*"},
            {"POS":"DET", "OP":"*"}
        ],
        [
            {"POS":"SCONJ"},
            {"POS":"VERB"},
            {"POS":"ADP"}
        ],
        [
            {"POS":"ADV"},
            {"POS":"VERB"},
            {"POS":"PRON", "OP":"*"}
        ],
        [
            {'POS': 'VERB', 'OP': '?'},
            {'POS': 'ADV', 'OP': '*'},
            {'POS': 'VERB', 'OP': '+'}
        ]
    ]

    
    phrases = []
    
    matcher = Matcher(nlp.vocab)
    matcher.add("Verb phrase", patterns)

    matches = matcher(doc)
    spans = [doc[start:end] for _, start, end in matches]

    for pred in filter_spans(spans):
        if (check_root(pred, root)):
            phrases.append(pred)

    return phrases

def get_full_predicate(predicates):
    #find the full predicate for a given verb
    length = 0
    full_predicate = None
    for predicate in predicates:
        if len(predicate) > length:
            full_predicate = predicate
            
    return full_predicate

def get_subject(predicate, non_predicate):
    #find subject if noun chunks are before the predicate
    for phrase in non_predicate:
        if phrase.start < predicate.start:
            return phrase

def get_object(predicate, non_predicate):
    #find object if noun chunks are after the predicate
    for phrase in non_predicate:
        if phrase.start > predicate.start:
            return phrase
      
'''
main function
'''
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError('Expected exactly 2 argument: input file and result file')
    your_extracting_function(sys.argv[1], sys.argv[2])


#References:
#https://spacy.io/
#https://spacy.io/api/token
#https://stackoverflow.com/questions/47856247/extract-verb-phrases-using-spacy
#https://stackoverflow.com/questions/58844962/match-the-last-noun-before-a-particular-word
#https://subscription.packtpub.com/book/data/9781838987312/2/ch02lvl1sec14/extracting-noun-chunks
#https://subscription.packtpub.com/book/data/9781838987312/2/ch02lvl1sec15/extracting-entities-and-relations
