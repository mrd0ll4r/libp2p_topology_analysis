source("util.R")

library(readr)
library(xtable)
library(dplyr)
library(tidyr)

dir.create("tab", showWarnings = TRUE, recursive = TRUE, mode = "0777")

options(xtable.floating=FALSE)
options(xtable.booktabs=TRUE)
options(xtable.auto=TRUE)
options(xtable.include.rownames = FALSE)

# Input files
networks <- list(
  c("ipfs_full",
    "../csv/full/ipfs/graph_metrics_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv"),
  c("filecoin_full",
    "../csv/full/filecoin-mainnet/graph_metrics_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv"),
  c("ipfs_online",
    "../csv/online_only/ipfs/graph_metrics_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv"),
  c("filecoin_online",
    "../csv/online_only/filecoin-mainnet/graph_metrics_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv")
)

for (n in networks) {
  n_name <- n[1]
  n_path <- n[2]
  
  d <- read_csv(n_path,col_types = "iIiddddddddddddcc")
  graph_type_name = d %>% filter(graph_type != "erdos-renyi" & graph_type != "barabasi-albert") %>% select(graph_type)
  graph_type_name = graph_type_name$graph_type
  
  d_long <- d %>%
    mutate(node_count=as.double(node_count),edge_count=as.double(edge_count),diameter=as.double(diameter)) %>%
    pivot_longer(!c("graph_type","id"), names_to="metric")
  
  d_agg <- d_long %>%
    group_by(graph_type,metric) %>%
    summarize(n=n(),avg=mean(value),ci_lower=CI(value)[1],ci_upper=CI(value)[2])
  
  write_csv(d_agg,fil=sprintf("tab/graph_metrics_%s_raw.csv",n_name))
  
  t <- d_agg %>%
    pivot_wider(id_cols=metric,names_from=graph_type,values_from=c("avg","ci_lower","ci_upper"),names_glue="{graph_type}_{.value}", names_vary="slowest")%>%
    select(metric,
           starts_with(graph_type_name),
           starts_with("erd"),
           starts_with("bar"))
  
  addtorow <- list()
  addtorow$pos = list(0)
  addtorow$command = sprintf('& \\multicolumn{3}{c}{%s} & \\multicolumn{3}{c}{Erdös-Renyi} & \\multicolumn{3}{c}{Barabasi-Albert} \\\\
  \\cmidrule(lr){2-4} \\cmidrule(lr){5-7} \\cmidrule(lr){8-10}
  Metric & $\\mu$ & +CI & -CI & $\\mu$ & +CI & -CI & $\\mu$ & +CI & -CI \\\\', graph_type_name)
  
  # Alternative format which is very wide:
  # t <- d_agg %>% 
  #  pivot_wider(id_cols=c(graph_type,n),names_from=metric,values_from=c("avg","ci_lower","ci_upper"),names_glue = "{metric}_{.value}",names_vary="slowest") %>%
  #  arrange(desc(graph_type)) %>%
  #  select(graph_type,n,
  #         node_count_avg,
  #         edge_count_avg,
  #         average_path_length_avg,
  #         starts_with("betweenness_max"),
  #         starts_with("betweenness_mean"),
  #         closeness_all_max_avg,
  #         closeness_all_mean_avg,
  #         starts_with("diameter"),
  #         #starts_with("pagerank"),
  #         starts_with("transitivity")
  #         ) %>%
  #  mutate(node_count_avg = as.integer(node_count_avg))
  #
  #addtorow <- list()
  #addtorow$pos <- list(0)
  #addtorow$command <- '&&& \\multicolumn{1}{c}{Edges} & \\multicolumn{1}{c}{apl} & \\multicolumn{3}{c}{betw. max} & \\multicolumn{3}{c}{betw. mean} & \\multicolumn{1}{c}{close. max} & \\multicolumn{1}{c}{close. mean} & \\multicolumn{3}{c}{diam} & \\multicolumn{3}{c}{trans.} \\\\
  #\\cmidrule(lr){6-18}
  #Graph & N & Nodes & $\\mu$ & $\\mu$ & $\\mu$ & +CI & -CI & $\\mu$ & +CI & -CI & $\\mu$ & $\\mu$ & $\\mu$ & +CI & -CI & $\\mu$ & +CI & -CI & $\\mu$ & +CI & -CI  \\\\'
  
  
  print(xtable(t,digits=-2), file=sprintf("tab/graph_metrics_%s.tex",n_name), add.to.row=addtorow,include.colnames=F)
}
