source("util.R")

library(data.table)
library(tidyr)

metrics_dt = fread("plot_data/graph_metrics.csv")

metrics_dt = pivot_longer(metrics_dt, !graph_type, names_to="metric")
setDT(metrics_dt)
metrics_dt[, .(avg_val = mean(value), ci_lower= CI(value)[1], 
               ci_upper = CI(value)[2]), .(graph_type, metric)]
