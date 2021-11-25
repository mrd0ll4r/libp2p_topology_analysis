#!/usr/bin/env python3
import random
import util

def generate_n_erg(num_nodes, num_edges, N):
    erg_list = [ig.GraphBase.Erdos_Renyi(n=num_nodes, m=num_edges, directed=True) for i in range(0, N)]
    return erg_list

def generate_n_bag(num_nodes, num_edges_total, N):
    ## Barabasi-Albert expects the number of nodes and the number of edges each new node should attach to its neighbors
    ## in the process of preferential attachment.
    bag_list = [ig.GraphBase.Barabasi(num_nodes, int(round(num_edges_total/num_nodes, 0)), directed=True, power=2) for i in range(0, N)]
    return bag_list

## TODO: normalize betweenness
## Expects: (1) a list of igraph objects, (2) the type of the graphs as string.
## Outputs: A pandas DF with many interesting metrics for all graphs
def metrics_for_graphs(glist, gtype):
    metric_df = pd.DataFrame({
        'node_count': [g.vcount() for g in glist],
        'edge_count': [g.ecount() for g in glist],
        'diameter': [g.diameter() for g in glist],
        'average_path_length': [g.average_path_length() for g in glist],
        'transitivity': [g.transitivity_undirected() for g in glist],
        'betweenness': [max(g.betweenness()) for g in glist],
        'closeness': [max(g.closeness()) for g in glist],
        'pagerank': [max(g.personalized_pagerank()) for g in glist],
        'graph_type': [gtype for i in range(0, len(glist))]
    })
    return metric_df



if __name__ == "__main__":
    ## Set random seed for graph generation and node/edge removals
    rnd_seed = 0
    random.seed(rnd_seed)

    ## How many graphs should we generate?
    n = 10


    ## Load the graph from the data frame and remove multi-edges
    g = util.load_graph_data()
    num_nodes_ipfs = g.vcount()
    num_edges_ipfs = g.ecount()

    ## Compute graph metrics for the crawl-graph
    ## ToDo: distinguish between all nodes and the reachable ones
    ipfs_df = metrics_for_graphs([g], "ipfs")

    ## Generate erdös-renyi and barabasi-albert random graphs
    ## with the same size to compare against
    erg_list = generate_n_erg(num_nodes_ipfs, num_edges_ipfs, n)
    bag_list = generate_n_bag(num_nodes_ipfs, num_edges_ipfs, n)

    ## Get graph metrics for these as well
    erg_df = metrics_for_graphs(erg_list, "erdos-renyi")
    bag_df = metrics_for_graphs(bag_list, "barabasi-albert")

    ## Gather all in a result DF and store that
    res_df = pd.concat([erg_df, bag_df])
    res_df.to_csv("graph_metrics.csv", index=False, header=True)

