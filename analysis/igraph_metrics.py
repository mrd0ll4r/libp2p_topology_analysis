#!/usr/bin/env python3
import statistics

import pandas as pd
import igraph as ig


# Generates num_graphs Erdos-Renyi random graphs for the given number of nodes
# and edges.
def generate_n_erg(num_nodes, num_edges, num_graphs=5):
    erg_list = [
        ig.GraphBase.Erdos_Renyi(n=num_nodes, m=num_edges, directed=True)
        for _ in range(0, num_graphs)]
    return erg_list


# Generates num_graph Barabasi-Albert random graphs for the given number of
# nodes and edges.
def generate_n_bag(num_nodes, num_edges_total, num_graphs=5):
    # Barabasi-Albert expects the number of nodes and the number of edges each
    # new node should attach to its neighbors in the process of preferential
    # attachment.
    bag_list = [
        ig.GraphBase.Barabasi(
            num_nodes,
            int(round(num_edges_total / num_nodes, 0)),
            directed=True, power=2)
        for _ in range(0, num_graphs)]
    return bag_list


## TODO: normalize betweenness
## Expects: (1) a list of igraph objects, (2) the type of the graphs as string.
## Outputs: A pandas DF with many interesting metrics for all graphs
def metrics_for_graphs(glist: [ig.Graph], gtype: str, identifier: str):
    betweenness = [g.betweenness(directed=True) for g in glist]
    closeness_all = [g.closeness(mode="all", normalized=True) for g in glist]
    closeness_in = [g.closeness(mode="in", normalized=True) for g in glist]
    closeness_out = [g.closeness(mode="out", normalized=True) for g in glist]
    personalized_pagerank = [g.personalized_pagerank(directed=True) for g in
                             glist]

    metric_df = pd.DataFrame({
        'node_count': [g.vcount() for g in glist],
        'edge_count': [g.ecount() for g in glist],
        'diameter': [g.diameter(directed=True) for g in glist],
        'average_path_length': [g.average_path_length(directed=True) for g in
                                glist],
        'transitivity': [g.transitivity_undirected() for g in glist],
        'betweenness_max': [max(b) for b in betweenness],
        'betweenness_mean': [statistics.mean(b) for b in betweenness],
        'closeness_all_max': [max(b) for b in closeness_all],
        'closeness_all_mean': [statistics.mean(b) for b in closeness_all],
        'closeness_in_max': [max(b) for b in closeness_in],
        'closeness_in_mean': [statistics.mean(b) for b in closeness_in],
        'closeness_out_max': [max(b) for b in closeness_out],
        'closeness_out_mean': [statistics.mean(b) for b in closeness_out],
        'pagerank_max': [max(b) for b in personalized_pagerank],
        'pagerank_mean': [statistics.mean(b) for b in personalized_pagerank],
        'graph_type': [gtype for _ in range(0, len(glist))],
        'id': [identifier for _ in range(0, len(glist))]
    })
    return metric_df
