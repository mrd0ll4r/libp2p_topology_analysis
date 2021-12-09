#!/usr/bin/env python3

import pandas as pd
import igraph as ig

def make_simple_graph(df):
    g = ig.Graph.TupleList(df[["peer_id", "neighbor_id"]].itertuples(index=False), weights=False,
                       directed=True)
    g.simplify()
    return g

## Opens a crawl db dump and yields each graph.
def parse_db_dump(crawl_file, chunksize):
    csv_reader = pd.read_csv(crawl_file, iterator=True, chunksize=chunksize)
    crawl = pd.DataFrame()

    ## The idea is simple: consume the raw dump in chunks, extract chunks until we have a complete edgelist,
    ## use that edgelist to build an igraph-graph and yield that graph. Repeat.

    first_chunk = csv_reader.get_chunk()
    target_crawl_id = min(first_chunk["crawl_id"])


    crawl = crawl.append(first_chunk)

    ## For every further chunk: put it either into our DF or yield the graph object
    for chunk in csv_reader:
        #print("Processing chunk...")
        cids = chunk["crawl_id"].unique()
        ## There are several cases:
        ## (1) We read an entire chunk of data with the same target_id => easy. Just append and be happy
        ## (2) We read a chunk with 2 or even more IDs => yield every ID until the last one
        ## (3) We read a chunk with 1 ID but it's different from our target_id => yield and use the new id as target.
        if target_crawl_id in cids:
            if len(cids) == 1:
                ## Case (1): Only our target_id
                crawl = crawl.append(chunk)
                #print(f"Easy, appending to {target_crawl_id}...")
            else:
                ## Case (2): Multiple IDs
                ## Yield our graph in progress
                crawl = crawl.append(chunk[chunk.crawl_id == target_crawl_id])
                #print("Multiple IDs, yielding the first graph")
                yield target_crawl_id, make_simple_graph(crawl)
                ## This case is probably very rare. Yield every graph until the last ID which will become
                ## our new target.
                for uniq_cid in cids[1:-1]:
                    #print(f"Yielding graph with ID {uniq_cid}")
                    crawl = chunk[chunk.crawl_id == uniq_cid]
                    yield uniq_cid, make_simple_graph(crawl)
                #print(f"Setting new target to {cids[-1]}")
                target_crawl_id = cids[-1]
                crawl = chunk[chunk.crawl_id == target_crawl_id]
        else:
            #print(f"Last ID not in chunk, yielding {target_crawl_id}")
            ## Condition (3): Our ID is not in the chunk. Yield our graph
            yield target_crawl_id, make_simple_graph(crawl)
            if len(cids) == 1:
                #print(f"Only one cid, making {cids[-1]} the new target.")
                ## Easy: make this the new target_crawl_id and use the data
                target_crawl_id = cids[-1]
                crawl = chunk
            if len(cids) >= 2:
                #print(f"Multiple IDs, yielding {target_crawl_id}")
                ## Again: yield every graph until the last one, use the new graph as target
                for uniq_cid in cids[0:-1]:
                    #print(f"Yielding graph with ID {uniq_cid}")
                    yield uniq_cid, make_simple_graph(chunk[chunk.crawl_id == uniq_cid, ["peer_id", "neighbor_id"]])
                #print(f"Setting new target to {cids[-1]}")
                target_crawl_id = cids[-1]
                crawl = chunk[chunk.crawl_id == target_crawl_id]
