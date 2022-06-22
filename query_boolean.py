from collections import defaultdict
import pickle
import os
import numpy as np

from string_processing import *


def intersect_query(doc_list1, doc_list2):
    # TODO: you might like to use a function like this 
    # in your run_boolean_query implementation
    # for full marks this should be the O(n + m) intersection algorithm for sorted lists
    # using data structures such as sets or dictionaries in this function will not score full marks
    res = []
    # if one is empty, renturn []
    if len(doc_list1) == 0 or len(doc_list2) == 0:
        return []

    i = 0
    j = 0
    while i < len(doc_list1) and j < len(doc_list2):
        if doc_list1[i] == doc_list2[j]:
            res.append(doc_list1[i])
            i += 1
            j += 1
        elif doc_list1[i] < doc_list2[j]:
            i += 1
        else:
            j += 1
    return res


def union_query(doc_list1, doc_list2):
    # TODO: you might like to use a function like this 
    # in your run_boolean_query implementation
    # for full marks this should be the O(n + m) union algorithm for sorted lists
    # using data structures such as sets or dictionaries in this function will not score full marks

    # if one is empty, renturn the other
    if len(doc_list1) == 0:
        return doc_list2
    elif len(doc_list2) == 0:
        return doc_list1

    res = []
    i = 0
    j = 0
    while i < len(doc_list1) and j < len(doc_list2):
        if doc_list1[i] == doc_list2[j]:
            res.append(doc_list1[i])
            i += 1
            j += 1
        elif doc_list1[i] < doc_list2[j]:
            res.append(doc_list1[i])
            i += 1
        else:
            res.append(doc_list2[j])
            j += 1

    if i == len(doc_list1):
        res.extend(doc_list2[j:])
    elif j == len(doc_list2):
        res.extend(doc_list1[i:])

    return res


def run_boolean_query(query, index):
    """Runs a boolean query using the index.

    Args:
        query (str): boolean query string
        index (dict(str : list(tuple(int, int)))): The index aka dictonary of posting lists

    Returns:
        list(int): a list of doc_ids which are relevant to the query
    """
    # TODO: implement this function
    relevant_docs=[]

    # if the query is empty
    if query == None or len(query)==0:
        return []

    queList = query.split(" ")
    # if only one term in query
    if len(queList)==1:
        # if the term is not in the index
        if queList[0] not in index.keys():
            return []
        # otherwise
        for tup in index[queList[0]]:
            relevant_docs.append(tup[0])
        return relevant_docs

    # it has many query terms.
    # Operator only appears under the odd index of the query term.
    # Let the demo initially be the docList for the queList[0] term.
    demo=[]
    if queList[0] not in index.keys():
        pass
    else:
        for tup in index[queList[0]]:
            demo.append(tup[0])

    i = 1
    while i < len(queList):
        termb=queList[i+1]
        docb=[]
        # get doc list for termb
        if termb not in index.keys():
            pass
        else:
            for tup in index[termb]:
                docb.append(tup[0])
        # union/intersect(demo,docb)
        if queList[i] == "AND":
            demo=intersect_query(demo,docb)
        else:
            demo=union_query(demo,docb)
        i+=2

    relevant_docs=demo

    return relevant_docs


# load the stored index
(index, doc_freq, doc_ids, num_docs) = pickle.load(open("stored_index.pik", "rb"))

print("Index length:", len(index))
if len(index) != 906290:
    print("Warning: the length of the index looks wrong.")
    print("Make sure you are using `process_tokens_original` when you build the index.")
    raise Exception()

# the list of queries asked for in the assignment text
queries = [
    "Welcoming",
    "unwelcome OR sam",
    "ducks AND water",
    "plan AND water AND wage",
    "plan OR record AND water AND wage",
    "space AND engine OR football AND placement"
]

# run each of the queries and print the result
ids_to_doc = {v: k for k, v in doc_ids.items()}
for q in queries:
    res = run_boolean_query(q, index)
    res.sort(key=lambda x: ids_to_doc[x])
    print(q)
    for r in res:
        print(ids_to_doc[r])
