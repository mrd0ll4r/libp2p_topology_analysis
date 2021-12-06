## Graph metrics on libp2p-based overlay networks

This repo contains python scripts to (1) compute graph metrics and (2) perform resilience/robustness calculations, given a measured overlay graph.

You can issue `poetry install` to install the necessary dependencies via [poetry](https://python-poetry.org).

`analysis/igraph_metrics.py` contains code to compute basic graph metrics:
* diameter
* average path length
* transitivity (=clustering coefficient)
* max. betweenness
* max. closeness
* max. pagerank

These metrics are computed for the provided overlay graph *and* for equally sized Erdős–Rényi and Barabási-Albert random graphs.
The script will write a `graph_metrics.csv` with the respective metrics.

`analysis/resilience.py` has scripts to compute the resilience of the specified graphs to random failures and targeted node removals.