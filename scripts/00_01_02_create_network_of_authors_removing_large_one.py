import pandas as pd
import networkx as nx
import json
import datetime
from collections import defaultdict
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt
import pickle
# %%
output_code = "00_01_02"
# %%
node_id_to_node_name = {}
node_id_to_first_publish_date = {}
cord19_paper_id_to_coauthors = defaultdict(set)
with open("../inputs/untracked/article-authors_04-27.csv", "r") as f:
    print(f.readline())
    for line in f:
        splitted_line = line.strip().split("|")
        cord19_paper_id = splitted_line[0]
        unique_author_name = splitted_line[2]
        unique_author_id = splitted_line[3]
        if splitted_line[5]:
            publish_date = datetime.datetime.strptime(splitted_line[5],"%Y-%m-%d")
        else:
            continue
        #print(line)
        node_id_to_node_name[unique_author_id] = unique_author_name
        if unique_author_id in node_id_to_first_publish_date:
            if publish_date < node_id_to_first_publish_date[unique_author_id]:
                ## We are trying to get the earliest publish date of the author
                node_id_to_first_publish_date[unique_author_id] = publish_date
            else:
                pass
        else:
            ## We have never encountered this node before so we add this into
            ## the dictionary
            node_id_to_first_publish_date[unique_author_id] = publish_date
        ## Now adding the unique node id to the set to create co-author network
        cord19_paper_id_to_coauthors[cord19_paper_id].add(unique_author_id)
# %%
del cord19_paper_id_to_coauthors["1vimqhdp"]
# %%
edgelist_with_weight = defaultdict(int)
## First for each of the coauthors sets, we will create a sorted list
## create combination of nodes that will go as an edge of the one-mode projection
for coauthor_set in cord19_paper_id_to_coauthors.values():
    for edge_tuple in combinations(sorted(coauthor_set),2):
        edgelist_with_weight[edge_tuple] += 1
# %%
all_edges_with_weight = [(n1,n2,w) for (n1,n2),w in edgelist_with_weight.items()]
g = nx.Graph()
g.add_weighted_edges_from(all_edges_with_weight)
# %%
with open("../outputs/untracked/%s_node_id_to_node_name.json" %output_code, "w") as f:
    json.dump(node_id_to_node_name,f)
# %%
## saving the dates as pickle because json can not serialize the dates
with open("../outputs/untracked/%s_node_id_to_first_publish_date.pickle" %output_code, "wb") as f:
    pickle.dump(node_id_to_first_publish_date, f)
# %%
## Writing the edgelist
with open("../outputs/untracked/%s_coauthorship_network.edgelist" %output_code, "wb") as f:
    nx.write_weighted_edgelist(g, f)