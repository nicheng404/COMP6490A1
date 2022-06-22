from collections import defaultdict
import pickle
import os
import numpy as np

from string_processing import *

def get_query_tokens(query_string):
    """Turns a query text string into a sequence of tokens.
    Applies the same set of lingusitic modules as during
    index construction.

    Args:
        query_string (str): the input query

    Returns:
        list(str): a list of processed tokens.
    """
    toks = tokenize_text(query_string)
    toks = process_tokens(toks)
    return toks

def count_query_tokens(query_tokens):
    """Given a list of query tokens will count them and return 
    a list containing (unique token, term frequency)

    Args:
        query_tokens (list(string)): a list of processed tokens.

    Returns:
        list(tuple(str, int)): a list of tokens and their term frequency counts.
    """
    counts = defaultdict(int)
    for tok in query_tokens:
        counts[tok] += 1
    return list(counts.items())

def get_doc_to_norm(index, doc_freq, num_docs):
    """Precompute the norms for each document vector in the corpus.

    Args:
        index (dict(str : list(tuple(int, int)))): The index aka dictonary of posting lists
        doc_freq (dict(str : int)): document frequency for each term
        num_docs (int): number of documents in the corpus

    Returns:
        dict(int: float): a dictionary mapping doc_ids to document norms
    """
    doc_norm = defaultdict(int)
    # calculate square of norm for all docs
    for term in index.keys():
        for doc_id, doc_tf in index[term]:
            doc_norm[doc_id] += doc_tf **2

    # take square root squared norms
    for doc_id in doc_norm.keys():
        doc_norm[doc_id] = np.sqrt(doc_norm[doc_id])

    return doc_norm

def run_query(query_token_counts, index, doc_freq, doc_norm, num_docs):
    """ Run a query on the index and return a sorted list of documents. 
    Sorted by most similar to least similar.
    Documents not returned in the sorted list are assumed to have 0 similarity.

    Args:
        query_token_counts (list(tuple(str, int)): a list of query tokens and their term frequency counts
        index (dict(str : list(tuple(int, int)))): The index aka dictonary of posting lists
        doc_freq (dict(str : int)): document frequency for each term
        doc_norm (dict(int : float)): a map from doc_ids to pre-computed document norms
        num_docs (int): number of documents in the corpus

    Returns:
        list(tuple(int, float)): a list of document ids and the similarity scores with the query
        sorted so that the most similar documents to the query are at the top.
    """

    # calculate the norm of the query vector
    query_norm = 0
    for query_term, query_tf in query_token_counts:
        query_norm += query_tf**2
    query_norm = np.sqrt(query_norm)

    # calculate cosine similarity for all relevant documents
    doc_to_score = defaultdict(float)
    for query_term, query_tf in query_token_counts:
        # ignore query terms not in the index
        if query_term not in index:
            continue
        # add to similarity for documents that contain current query word
        for doc_id, doc_tf in index[query_term]:
            doc_to_score[doc_id] += query_tf * doc_tf / (doc_norm[doc_id] * query_norm)

    sorted_docs = sorted(doc_to_score.items(), key=lambda x:-x[1])
    return sorted_docs

# load the index from disk
(index, doc_freq, doc_ids, num_docs) = pickle.load(open("stored_index.pik", "rb"))

# process some doc norms (in practice we would want to store this on disk, for
# simplicity in this assignment it is written here)
doc_norms = get_doc_to_norm(index, doc_freq, num_docs) 

# get a reverse mapping from doc_ids to document paths
ids_to_doc = {v:k for k, v in doc_ids.items()}


# run all the queries in the evaluation dataset and store the result for evaluation
fout = open("./runs/retrieved.txt", "w")
for lines in open("./gov/topics/gov.topics", "r"):

    # read the evaluation query
    lines = lines.split()
    id = lines[0]
    query = lines[1:]
    id = int(id)
    query = " ".join(query)

    # run the query
    qt = get_query_tokens(query)
    query_token_counts = count_query_tokens(qt)
    res = run_query(query_token_counts, index, doc_freq, doc_norms, num_docs)

    # write the results in the correct treceval format
    for rank, (doc, sim) in enumerate(res):
        strout = "%d Q0 %s %d %f MY_IR_SYSTEM\n" % (id, os.path.split(ids_to_doc[doc])[-1], rank, sim)
        fout.write(strout)

fout.close()




