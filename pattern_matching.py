"""
Barebone code created by: Tuan-Phong Nguyen
Date: 2022-06-03
"""

import logging
from typing import Dict, List, Tuple

from collections import Counter

import spacy
from spacy.matcher import Matcher

logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")

def your_solution(animal: str, doc_list: List[Dict[str, str]]) -> List[Tuple[str, int]]:
    """
    Task: Extract things that the given animal eats. These things should be mentioned in the given list of documents.
    Each document in ``doc_list`` is a dictionary with keys ``animal``, ``url``, ``title`` and ``text``, whereas
    ``text`` points to the content of the document.

    :param animal: The animal to extract diets for.
    :param doc_list: A list of retrived documents.
    :return: A list of things that the animal eats along with their frequencies.
    """

    print(f"Animal: \"{animal}\". Number of documents: {len(doc_list)}.")

    # You can directly use the following list of documents, which is a list of str, if you don't need other information (i.e., url, title).
    documents = [doc["text"] for doc in doc_list]

    # TODO Implement your own method here
    # You must extract things that are explicitly mentioned in the documents.
    # You cannot use any external CSK resources (e.g., ConceptNet, Quasimodo, Ascent, etc.).

    # Output example:
    # return [("grass", 10), ("fish", 3)]

    matcher = Matcher(nlp.vocab)
    pattern = [
        [
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}, "OP":"?"},
            {"LEMMA": "eat"},
            {"POS": "NOUN"},
        ],
        [
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}, "OP":"?"},
            {"LEMMA": "eat"},
            {"POS": "ADV", "OP":"*"},
            {"POS": "NOUN"},
        ],
        [
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}},
            {"POS": "ADV", "OP":"*"},
            {"LEMMA": "eat"},
            {"POS": "ADJ", "OP":"*"},
            {"POS": "ADV", "OP":"*"},
            {"POS": "NOUN"},
            {"POS": "CCONJ", "OP": "*"},
            {"POS": "NOUN", "OP": "*"}
        ],
        [   
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}},
            {"LEMMA": "feed"},
            {"POS": "SCONJ"},
            {"POS": "PRON", "OP":"*"},
            {"POS": "ADJ", "OP":"*"},
            {"POS": "NOUN", "OP":"*"},
            {"POS": "CCONJ", "OP":"*"},
            {"POS": "NOUN", "OP":"*"},
        ],
        [
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}},
            {"LEMMA": "munch"},
            {"POS": "ADP", "OP": "*"},
            {"POS": "VERB", "OP": "*"},
            {"POS": "ADJ", "OP":"*"},
            {"POS": "NOUN", "OP":"*"},
            {"POS": "CCONJ", "OP":"*"},
            {"POS": "ADJ", "OP":"*"},
            {"POS": "NOUN", "OP":"*"},
            {"POS": "NOUN"}
        ],
        [
            {"LOWER": {"IN": [f"{animal}", f"{animal}s"]}},
            {"LEMMA": "eat"},
            {"POS": "DET"},
            {"POS": "NOUN"},
            {"POS": "ADP", "OP": "*"},
            {"POS": "NOUN"},
            {"POS": "CCONJ", "OP":"*"},
            {"POS": "NOUN", "OP":"*"},
        ]
    ]
    matcher.add("eatPattern", pattern)

    logger.info(
        f"Animal: \"{animal}\". Number of documents: {len(doc_list)}. Running SpaCy...")
    for doc in doc_list:
        doc["spacy_doc"] = nlp(doc["text"])
        
    matches = []
    for doc in doc_list:
        matches.append(matcher(doc["spacy_doc"]))

    diets = []
    for a, ms in zip(doc_list, matches):
        for m in ms:
            _, _, end = m
            diets.append(a["spacy_doc"][end-1].text.lower())
    
    return Counter(diets).most_common()
