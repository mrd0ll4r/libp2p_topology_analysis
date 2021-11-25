#!/usr/bin/env python3
import numpy as np
import pandas as pd

import util
import random

def randomRemoval(graph, removal_ratio=0.9):
    num_removals = int(round(graph.vcount()*removal_ratio, 0))
    num_nodes_before = graph.vcount()
    percentage_in_conn_comp = []
    ratio_removed = np.arange(0.0, removal_ratio, 1/num_nodes_before)
    for i in range(0, num_removals):
        ## Very basic progress indicator
        if i % 100 == 0:
            print(i*100/num_removals)

        rand_vid = random.randrange(0, num_nodes_before - i)
        graph.delete_vertices(rand_vid)
        ## components.sizes() gives a descending list of the vcount of connected components.
        ## components.size(<index>) seems to give the size of the specified index. So 0 => max?
        ## Vertices are strongly connected if there's a path in *both* directions, i.e.,
        ## u, v \in V have a path u -> v and v -> u.
        ## I think for our purposes weak connectedness is more useful, but this should be discussed (<- ToDo)
        ## We calculate the percentage of nodes contained in the biggest connected component.
        ## To avoid recalculating graph.vcount() everytime we use our loop index for that.
        percentage_in_conn_comp.append(graph.components(mode="weak").size(0)*100/(num_nodes_before - i - 1))

    return pd.DataFrame({
        "ratio_removed": ratio_removed,
        "percentage_in_conn_comp": percentage_in_conn_comp
    })

## Same considerations apply as for randomRemoval.
## This expects a removal_metric function which sorts the vertices in each iteration
## and removes the highest-ranked on.
def targetedRemoval(graph, removal_func, removal_ratio=0.9):
    num_removals = int(round(graph.vcount()*removal_ratio, 0))
    num_nodes_before = graph.vcount()
    percentage_in_conn_comp = []
    ratio_removed = np.arange(0.0, removal_ratio, 1/num_nodes_before)

    for i in range(0, num_removals):
        ## Very basic progress indicator
        if i % 100 == 0:
            print(i*100/num_removals)

        target_vertex = removal_func(graph)
        graph.delete_vertices(target_vertex)
        percentage_in_conn_comp.append(graph.components(mode="weak").size(0)*100/(num_nodes_before - i - 1))

    return pd.DataFrame({
        "ratio_removed": ratio_removed,
        "percentage_in_conn_comp": percentage_in_conn_comp
    })


def repeated_random_resilience(graph, removal_ratio, num_iterations):
    df_list = []
    for i in range(0, num_iterations):
        g_copy = graph.copy()
        tmp_res = randomRemoval(g_copy, removal_ratio)
        tmp_res["iteration"] = [i for j in range(0, len(tmp_res))]
        df_list.append(tmp_res.copy())

    return df_list


if __name__ == "__main__":
    ## Set random seed for reproducible node/edge removals
    rnd_seed = 0
    random.seed(rnd_seed)
    ## How many iterations of removals should we do?
    n = 10

    ## The targetedRemoval function takes a node ranking metric.
    ## We use the maximum degree as a start
    maxdeg_func = lambda g: g.vs.select(_degree=g.maxdegree())[0]

    ## Load the graph
    g = util.load_graph_data()

    ## Copy the original graph before removing things on it
    g_copy = g.copy()
    targeted_res = targetedRemoval(g_copy, maxdeg_func, 0.9)
    g_copy = g.copy()
    random_res = repeated_random_resilience(g_copy, 0.9, n)

    targeted_res.to_csv("targeted_resilience.csv", index=False, header=True)
    pd.concat(random_res).to_csv("random_resilience.csv", index=False, header=True)