import argparse
import util
import igraph_metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze given topologies.")

    parser.add_argument("path", help="Path to crawl dump")
    parser.add_argument("--chunksize", metavar="k", type=int, default=10**4, help="Size of chunks (in number of lines) when reading the crawl dump.")
    parser.add_argument("--num_rand_graphs", metavar="N", type=int, default=5, help="Number of random graphs that should be generated.")
    parser.add_argument("--graph_metrics", action="store_true", default=False, help="Should we compute graph metrics on the given topologies?")
    parser.add_argument("--resilience", action="store_true", help="Should we do a resilience analysis?")
    parser.add_argument("--output_path", default="./", help="Path to output CSVs to.")

    args = parser.parse_args()

    for crawl_id, g in util.parse_db_dump(args.path, chunksize=args.chunksize):
        print(f"Crawl_id {crawl_id}. Nodes: {g.vcount()}, Edges: {g.ecount()}.")
        if args.graph_metrics:
            metric_df = igraph_metrics.metrics_for_graphs([g], "ipfs", crawl_id)
            metric_df.to_csv(f"{args.output_path}gmetrics_{crawl_id}.csv")
