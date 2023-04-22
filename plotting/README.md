# Libp2p Kademlia Topology Analysis

You'll need `R>=4.2` installed, everything else should (hopefully) be taken care of by `renv`.
After running the [analysis scripts](../analysis), you'll probably need to adjust the paths to the files specified at the top of the two R scripts.

After you've done that, execute:

```bash
Rscript graph_metrics.R
Rscript resilience_plot.R
```

This will write figures to [fig/](fig) and tables to [tab/](tab).