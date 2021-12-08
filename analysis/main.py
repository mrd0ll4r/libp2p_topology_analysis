import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze given topologies.")

    parser.add_argument("path", help="Path to crawl dump")
    parser.add_argument("--num_rand_graphs", metavar="N", type=int, default=5, help="Number of random graphs that should be generated.")
    parser.add_argument("--graph_metrics", action="store_true", default=False, help="Should we compute graph metrics on the given topologies?")
    parser.add_argument("--resilience", action="store_true", help="Should we do a resilience analysis?")

    args = parser.parse_args()
