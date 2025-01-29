import spacy
import re
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter

#spacy.cli.download("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")

filename_ip = "./wikipedia_dump/1.txt"

file_text = open(filename_ip, "r", encoding="utf8")
title = file_text.readline().replace("\n","")
#print(title)

#Cleaning text

file_text = BeautifulSoup(file_text, "lxml").text #remove html tags
file_text = file_text.replace("\n\n","") #remove line breaks
file_text = file_text.replace("[","").replace("]","") #remove square brackets
file_text = re.sub(r"http\S+", "", file_text) #remove urls
file_text = re.sub(r"==.*?==+", "", file_text) #remove headings
file_text = re.sub(r"\{.*\}", "", file_text) #remove unnecessary information
file_text = re.sub(r"[\,\'\"\*\=:\(\)|]", "", file_text) #remove punctuation
file_text = file_text.replace("File:", "") #remove file:

#print(file_text)

file_doc = nlp(file_text)

#Problem 1

#named entity recognition
entities = []
for ent in file_doc.ents:
    entities.append(ent.text)
#print(entities)

#counting entities
freq = Counter(entities)
print(freq)

entities_set = set(entities)
print(len(entities_set)) #total number of unique named entities

title_list = [title] * len(freq)
named_entity = freq.keys()
frequency = freq.values()

entity_list = list(zip(title_list, named_entity, frequency))

print(entity_list)

#convert to dataframe
entity_frame = pd.DataFrame(entity_list, columns=['Title', 'Named-entity', 'Frequency'])

print(entity_frame)

filename_op = "./"+title.strip()+".csv"
entity_frame.to_csv(filename_op, index=False)

#Problem2.1

postype = []
postext = []
for token in file_doc:
    postext.append(token.lemma_)
    postype.append(token.pos_)

verb_adj = [token.text
         for token in file_doc
         if (not token.is_stop and
             not token.is_punct and
             token.pos_ == "ADJ" or
             token.pos_ == "VERB")]

#print(verb_adj)

verb_adj_freq = Counter(verb_adj)
#print(verb_adj_freq)

common_adj_verb = verb_adj_freq.most_common(1)
#print(common_adj_verb)

pos_list = list(zip(title_list, postype, common_adj_verb, verb_adj_freq.values()))

pos_frame = pd.DataFrame(pos_list, columns=['Title', 'POS Type', 'POS', 'Frequency'])

#print(pos_frame)

pos_frame.to_csv("./Problem2_1.csv", index=False, mode='a', header=False)

#References used to solve the problems:
#https://realpython.com/natural-language-processing-spacy-python/
#https://monkeylearn.com/blog/text-cleaning/
#https://stackoverflow.com/questions/36850550/split-the-result-of-counter
#https://www.javatpoint.com/how-to-create-a-dataframes-in-python
#https://stackoverflow.com/questions/37253326/how-to-find-the-most-common-words-using-spacy
