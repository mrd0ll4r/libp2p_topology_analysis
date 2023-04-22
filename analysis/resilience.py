#!/usr/bin/env python3

import random
import igraph as ig
import pandas as pd
import numpy as np


# Removes nodes, one by one, and records the percentage of remaining nodes in
# the largest connected component.
# Uses a function of the graph to determine which node to remove next.
def targeted_removal(graph: ig.Graph, removal_func, removal_ratio=0.9):
    num_nodes_before = graph.vcount()
    percentage_in_conn_comp = []
    ratio_removed = np.arange(0.0, removal_ratio, 1 / num_nodes_before)

    for _x in ratio_removed:
        target_vertex = removal_func(graph)
        graph.delete_vertices(target_vertex)

        # components.sizes() gives a descending list of the vcount of connected components.
        # components.size(<index>) seems to give the size of the specified index. So 0 => max?
        # Vertices are strongly connected if there's a path in *both* directions, i.e.,
        # u, v \in V have a path u -> v and v -> u.
        # I think for our purposes weak connectedness is more useful, but this should be discussed (<- ToDo)
        # We calculate the percentage of nodes contained in the biggest connected component.
        percentage_in_conn_comp.append(
            graph.components(mode="weak").size(0) * 100 / (graph.vcount()))

    return pd.DataFrame({
        "ratio_removed": ratio_removed,
        "percentage_in_conn_comp": percentage_in_conn_comp
    })


def maxdeg_removal(graph: ig.Graph, removal_ratio=0.9):
    # Function to select the node with the maximum combined degree.
    def maxdegree_selection(graph: ig.Graph):
        return graph.vs.select(_degree_eq=graph.maxdegree(mode="all"))[0]

    return targeted_removal(graph, maxdegree_selection, removal_ratio)


# Removes nodes randomly, one by one, and records the percentage of remaining
# nodes in the largest connected component.
def random_removal(graph: ig.Graph, removal_ratio=0.9):
    def random_selection(graph: ig.Graph):
        return random.randrange(0, graph.vcount())

    return targeted_removal(graph, random_selection, removal_ratio)


# Performs num_iterations iterations of random_removal.
def repeated_random_removal(graph: ig.Graph, removal_ratio=0.9,
                            num_iterations=10):
    df_list = []
    for i in range(0, num_iterations):
        g_copy = graph.copy()
        tmp_res = random_removal(g_copy, removal_ratio)
        tmp_res["iteration"] = [i for _ in range(0, len(tmp_res))]
        df_list.append(tmp_res.copy())

    return df_list
