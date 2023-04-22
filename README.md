## Graph metrics on libp2p-based overlay networks

Graph metrics and resilience of libp2p overlay graphs, using edgelists produced by our [libp2p crawler](https://github.com/trudi-group/ipfs-crawler).

This repo contains Python scripts, that, given an overlay graph:
1. generate comparable random graphs and compute graph metrics, and
2. perform resilience/robustness calculations on the overlay graph.

Additionally, there are R scripts to evaluate and plot the results.


## Usage

Use [analysis/main.py](analysis/main.py) to analyze a list of overlay graphs.

```bash
$ python3 analysis/main.py -h
usage: main.py [-h] [--num_rand_graphs N] [--num_rand_removal_reps N] [--graph_metrics] [--resilience] [--output_path OUTPUT_PATH] [--graph_name GRAPH_NAME] [--ignore_uncrawlable_nodes] GLOB

Analyze overlay graph topologies.

positional arguments:
  GLOB                  Glob of peer graph paths to load

options:
  -h, --help            show this help message and exit
  --num_rand_graphs N   Number of random graphs that should be generated.
  --num_rand_removal_reps N
                        Number of repetitions for random node removals.
  --graph_metrics       Should we compute graph metrics on the given topologies?
  --resilience          Should we do a resilience analysis?
  --output_path OUTPUT_PATH
                        Path to output CSVs to. A subdirectory per graph name will be created automatically.
  --graph_name GRAPH_NAME
                        Name of the graph. Will be used to create subdirectories, and appears in the CSV files.
  --ignore_uncrawlable_nodes
                        Ignores uncrawlable leaf nodes (out-degree=0)
```

Make sure to escape the path glob to avoid your shell from expanding it.
Results are written to CSV files.

Exapmle:
```bash
python3 analysis/main.py --num_rand_graphs 5 --num_rand_removal_reps 10 --graph_metrics --resilience --output_path csv --graph_name filecoin-mainnet 'edge_lists/filecoin/*'
```

Use the R scripts in [plotting/](plotting) to visualize the results.

## Installation

You can issue `poetry install` to install the necessary dependencies via [poetry](https://python-poetry.org).
Then use `poetry shell` to get a virtualenv with the installed dependencies.

## Metrics

`analysis/igraph_metrics.py` contains code to compute basic graph metrics:
* diameter
* average path length
* transitivity (=clustering coefficient)
* max. betweenness
* max. closeness
* max. pagerank

These metrics are computed for the provided overlay graph *and* for equally sized Erdős–Rényi and Barabási-Albert random graphs.

`analysis/resilience.py` has scripts to compute the resilience of the specified graphs to random failures and targeted node removals.