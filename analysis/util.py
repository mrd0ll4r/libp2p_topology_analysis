#!/usr/bin/env python3

import pandas as pd
import igraph as ig

## Wrapper for loading graphs from DB/file/multiple files.
## It expects two columns in a DataFrame: "peer_id" and "neighbor_id".
## For now this just reads the
## extracted data from the first crawl (ToDo).
def load_graph_data():
    ## Read the crawl data
    fcrawl = pd.read_csv("first_crawl.csv")
    g = ig.Graph.TupleList(fcrawl[["peer_id", "neighbor_id"]].itertuples(index=False), weights=False, directed=True)
    g.simplify()
    return g

