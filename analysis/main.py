#!/usr/bin/env python3

import argparse
import os
import random
import glob
import igraph as ig
import igraph_metrics
import resilience
import pandas as pd


# Creates an unweighted directed graph from a dataframe containing source and
# target columns.
def make_simple_graph(df):
    g = ig.Graph.TupleList(df[["source", "target"]].itertuples(index=False),
                           weights=False, directed=True)
    g.simplify()
    return g


# Parses the edgelist CSV file produced by the crawler into an igraph.Graph.
def parse_edgelist_csv(input_path) -> ig.Graph:
    csv_data = pd.read_csv(input_path, engine="pyarrow")
    return make_simple_graph(csv_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze overlay graph topologies.")

    parser.add_argument("path",
                        type=str,
                        metavar="GLOB",
                        default="edge_lists/ipfs/*",
                        help="Glob of peer graph paths to load")
    parser.add_argument("--num_rand_graphs",
                        metavar="N",
                        type=int,
                        default=5,
                        help="Number of random graphs that should be generated.")
    parser.add_argument("--num_rand_removal_reps",
                        metavar="N",
                        type=int,
                        default=10,
                        help="Number of repetitions for random node removals.")
    parser.add_argument("--graph_metrics",
                        action="store_true",
                        default=True,
                        help="Should we compute graph metrics on the given topologies?")
    parser.add_argument("--resilience",
                        action="store_true",
                        default=True,
                        help="Should we do a resilience analysis?")
    parser.add_argument("--output_path",
                        type=str,
                        default="csv/",
                        help="Path to output CSVs to. A subdirectory per graph name will be created automatically.")
    parser.add_argument("--graph_name",
                        type=str,
                        default="ipfs",
                        help="Name of the graph. Will be used to create subdirectories, and appears in the CSV files.")
    parser.add_argument("--ignore_uncrawlable_nodes",
                        action="store_true",
                        default=False,
                        help="Ignores uncrawlable leaf nodes (out-degree=0)")

    args = parser.parse_args()

    # Make sure the output directory exists.
    output_dir = os.path.join(args.output_path, args.graph_name)
    output_dir_crawls = os.path.join(output_dir, "crawls")
    os.makedirs(output_dir_crawls, exist_ok=True)
    print(f"writing per-crawl output to {output_dir_crawls}")
    print(f"writing aggregated output to {output_dir}")

    # DFs for metrics etc. over multiple crawls
    aggregated_metrics = pd.DataFrame()
    aggregated_targeted_res = pd.DataFrame()
    aggregated_random_res = pd.DataFrame()

    # Compute input files.
    input_files = sorted(glob.glob(args.path))
    print(f"loading peer graphs {input_files}")

    # Keep track of first and last crawl timestamp to name the collection CSV.
    first_crawl_ts = None
    last_crawl_ts = None

    # Process each crawl.
    for f in input_files:
        crawl_ts = os.path.basename(f)
        crawl_ts = crawl_ts.split(".csv")[0]
        crawl_ts = crawl_ts.split("peerGraph_")[1]

        if first_crawl_ts is None:
            first_crawl_ts = crawl_ts
        last_crawl_ts = crawl_ts

        print(f"loading peer graph timestamped {crawl_ts}...")
        g = parse_edgelist_csv(f)
        print(f"{crawl_ts}: Nodes: {g.vcount()}, Edges: {g.ecount()}.")

        if (args.ignore_uncrawlable_nodes):
            print("removing leaf nodes")
            g.delete_vertices(g.vs.select(_outdegree_eq=0))
            print(f"{g.vcount()} nodes, {g.ecount()} edges remaining.")

        if args.graph_metrics:
            print("calculating graph metrics...")

            crawl_df = igraph_metrics.metrics_for_graphs([g],
                                                         f"{args.graph_name}",
                                                         crawl_ts)

            print("calculating graph metrics for comparable random graphs...")

            # Set random seed for graph generation and node/edge removals.
            # We need to reset this for each crawl.
            rnd_seed = 0
            random.seed(rnd_seed)

            # Edge and node counts, to generate random graphs
            num_nodes_crawl = g.vcount()
            num_edges_crawl = g.ecount()

            # Generate erdös-renyi and barabasi-albert random graphs
            # with the same size to compare against
            erg_list = igraph_metrics.generate_n_erg(num_nodes_crawl,
                                                     num_edges_crawl,
                                                     args.num_rand_graphs)
            bag_list = igraph_metrics.generate_n_bag(num_nodes_crawl,
                                                     num_edges_crawl,
                                                     args.num_rand_graphs)

            # Get graph metrics for these as well
            erg_df = igraph_metrics.metrics_for_graphs(erg_list, "erdos-renyi",
                                                       crawl_ts)
            bag_df = igraph_metrics.metrics_for_graphs(bag_list,
                                                       "barabasi-albert",
                                                       crawl_ts)

            # Gather all in a result DF and store that
            res_df = pd.concat([crawl_df, erg_df, bag_df])
            res_df.to_csv(
                os.path.join(output_dir_crawls,
                             f"graph_metrics_{crawl_ts}.csv"),
                index=False, header=True)

            # Append to collection over all crawls
            aggregated_metrics = pd.concat([aggregated_metrics, res_df],
                                           ignore_index=True)

        if args.resilience:
            # Set random seed for reproducible node/edge removals
            # Reset for every crawl.
            rnd_seed = 0
            random.seed(rnd_seed)

            print("calculating targeted resilience metrics...")
            g_copy = g.copy()
            targeted_res = resilience.maxdeg_removal(g_copy, 0.9)

            print("calculating random resilience metrics...")
            g_copy = g.copy()
            random_res = pd.concat(
                resilience.repeated_random_removal(g_copy, 0.9,
                                                   args.num_rand_removal_reps))

            targeted_res['graph_type'] = pd.Series(
                [args.graph_name for i in range(0, len(targeted_res))], )
            targeted_res['id'] = pd.Series(
                [crawl_ts for i in range(0, len(targeted_res))])
            random_res['graph_type'] = pd.Series(
                [args.graph_name for i in range(0, len(random_res))], )
            random_res['id'] = pd.Series(
                [crawl_ts for i in range(0, len(random_res))])

            # Append to collection over all crawls
            aggregated_targeted_res = pd.concat(
                [aggregated_targeted_res, targeted_res], ignore_index=True)
            aggregated_random_res = pd.concat(
                [aggregated_random_res, random_res], ignore_index=True)

            # Write to CSV
            targeted_res.to_csv(
                os.path.join(output_dir_crawls,
                             f"targeted_resilience_{crawl_ts}.csv"),
                header=True)
            random_res.to_csv(
                os.path.join(output_dir_crawls,
                             f"random_resilience_{crawl_ts}.csv"),
                header=True)

    print("saving results...")
    aggregated_metrics.to_csv(
        os.path.join(output_dir,
                     f"graph_metrics_{first_crawl_ts}_to_{last_crawl_ts}.csv"),
        index=False,
        header=True)
    aggregated_targeted_res.to_csv(
        os.path.join(output_dir,
                     f"targeted_resilience_{first_crawl_ts}_to_{last_crawl_ts}.csv"),
        index=False, header=True)
    aggregated_random_res.to_csv(
        os.path.join(output_dir,
                     f"random_resilience_{first_crawl_ts}_to_{last_crawl_ts}.csv"),
        index=False, header=True)
