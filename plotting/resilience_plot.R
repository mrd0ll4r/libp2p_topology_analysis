source("util.R")

library(readr)
library(xtable)
library(dplyr)
library(tidyr)
library(ggplot2)
library(tikzDevice)
library(pracma)

dir.create("fig", showWarnings = TRUE, recursive = TRUE, mode = "0777")

theme_set(theme_bw(10))
theme_update(
  legend.position = "bottom",
)

# Input files
networks <- list(
  c("ipfs_full",
    "../csv/full/ipfs/random_resilience_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv",
    "../csv/full/ipfs/targeted_resilience_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv"),
  c("filecoin_full",
    "../csv/full/filecoin-mainnet/random_resilience_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv",
    "../csv/full/filecoin-mainnet/targeted_resilience_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv")#,
  #c("ipfs_online",
  #  "../csv/online_only/ipfs/random_resilience_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv",
  #  "../csv/online_only/ipfs/targeted_resilience_2023-04-20_02-17-15_UTC_to_2023-04-20_02-17-15_UTC.csv"),
  #c("filecoin_online",
  #  "../csv/online_only/filecoin-mainnet/random_resilience_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv",
  #  "../csv/online_only/filecoin-mainnet/targeted_resilience_2023-04-20_02-22-38_UTC_to_2023-04-20_02-22-38_UTC.csv")
)

# Plotting helper
print_plot <- function(plot, name, width=3.5, height=2.5){
  tex_name <- sprintf("fig/%s.tex",name)
  png_name <- sprintf("fig/%s.png",name)
  tex_width <- width
  tex_height <- height
  png_width <- tex_width*4
  png_height <- tex_height*4
  
  tikz(file=tex_name, width=tex_width, height=tex_height,sanitize = TRUE)
  print(plot)
  dev.off()
  
  png(file=png_name, width=png_width, height=png_height, units="cm", res=150)
  print(plot)
  dev.off()
}

## Random removals
plot_random_prepare_data <- function(input_file) {
  print(sprintf("loading results from %s", input_file))
  
  d <- read_csv(input_file, col_types = "ddicc")
  
  # Could contain multiple crawls, I guess?
  min_id = min(d$id)
  d <- d %>% filter(id == min_id)
  
  d_agg <- d %>% 
    group_by(graph_type, ratio_removed) %>%
    summarise(mean=mean(percentage_in_conn_comp),
              ci_lower = CI(percentage_in_conn_comp)[1],
              ci_upper = CI(percentage_in_conn_comp)[2]) %>%
    # From ratio to percentage for plotting
    mutate(ratio_removed = ratio_removed*100)
  
  return(d_agg)
}

plot_random_plot <- function(d) {
  p <- ggplot(d, aes(x = ratio_removed, y = mean)) +
    geom_line() +
    geom_ribbon(aes(ymin=ci_lower, ymax=ci_upper), alpha=0.15) +
    geom_line(aes(y = ci_lower), alpha = 0.5, linewidth=theme_get()$line$linewidth*0.5) +
    geom_line(aes(y = ci_upper), alpha = 0.5, linewidth=theme_get()$line$linewidth*0.5) +
    xlab("Percentage removed") +
    ylab("Perc. in conn. comp.") +
    scale_x_continuous(breaks = seq(0, 100, 10)) +
    facet_wrap(c("graph_type"),dir="v")
  
  return(p)
}
plot_random_single <- function(input_file) {
  print("calculating plot for random resilience...")
  
  d <- plot_random_prepare_data(input_file)
  p <- plot_random_plot(d)
  
  return(p)
}
plot_random_multi <- function(input_files) {
  d_full <- tibble()
  for (f in input_files) {
    d <- plot_random_prepare_data(f)
    
    if (isempty(d_full)) {
      d_full <- d
    } else {
      d_full <- rows_append(d_full,d)
    }
    
    rm(d)
  }
  
  p <- plot_random_plot(d_full)
  
  return(p)
}

## Targeted removals
plot_targeted_prepare_data <- function(input_file) {
  print(sprintf("loading results for from %s", input_file))
  
  d <- read_csv(input_file, col_types = "ddcc")
  
  # Could contain multiple crawls, I guess?
  min_id = min(d$id)
  d <- d %>% filter(id == min_id)
  
  # From ratio to percentage for plotting
  d <- d %>%
    mutate(ratio_removed = ratio_removed*100)
  
  return(d)
}
plot_targeted_plot <- function(d) {
  p <- ggplot(d, aes(x = ratio_removed, y = percentage_in_conn_comp)) +
    geom_line() +
    xlab("Percentage removed") +
    ylab("Perc. in conn. comp") +
    scale_x_continuous(breaks = seq(0, 100, 10)) +
    facet_wrap(c("graph_type"),dir="v")
  
  return(p)
}
plot_targeted_single <- function(input_file) {
  d <- plot_targeted_prepare_data(input_file)
  p <- plot_targeted_plot(d)
  
  return(p)
}
plot_targeted_multi <- function(input_files) {
  d_full <- tibble()
  for (f in input_files) {
    d <- plot_targeted_prepare_data(f)
    
    if (isempty(d_full)) {
      d_full <- d
    } else {
      d_full <- rows_append(d_full,d)
    }
    
    rm(d)
  }
  
  p <- plot_targeted_plot(d_full)
  
  return(p)
}

random_files = list()
targeted_files = list()

for (n in networks) {
  n_name = n[1]
  n_randfile = n[2]
  n_targetfile = n[3]
  
  random_files <- append(random_files, n_randfile)
  targeted_files <- append(targeted_files, n_targetfile)
  
  #### Random removal
  p <- plot_random_single(n_randfile)
  
  print_plot(p,sprintf("random_removals_%s", n_name))
  
  #### Targeted removal
  p <- plot_targeted_single(n_targetfile)
  
  print_plot(p,sprintf("targeted_removals_%s", n_name))
}


#### Random removal, combined
p <- plot_random_multi(random_files)

print_plot(p,"random_removals_faceted",height = 4)

#### Targeted removal, combined
p <- plot_targeted_multi(targeted_files)

print_plot(p,"targeted_removals_faceted",height=4)



