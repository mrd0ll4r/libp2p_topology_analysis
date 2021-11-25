source("util.R")

library(data.table)
library(ggplot2)
#library(tikzdevice)

theme_set(theme_bw(18))

###### Actual plotting

rand_dt = fread("../plot_data/random_resilience.csv")
target_dt = fread("../plot_data/targeted_resilience.csv")


## Random removals
aggr_rand = rand_dt[, .(mean=mean(percentage_in_conn_comp),
                        ci_lower=CI(percentage_in_conn_comp)[1],
                        ci_upper=CI(percentage_in_conn_comp)[2]),
                    .(ratio_removed)]
## From ratio to percentage for plotting
aggr_rand$ratio_removed = aggr_rand$ratio_removed*100


qRand = ggplot(aggr_rand, aes(x=ratio_removed, y=mean)) +
  geom_line(size=1) +
  geom_line(data=aggr_rand[,c("ratio_removed", "ci_lower")], aes(x=ratio_removed, y=ci_lower), alpha=0.5) +
  geom_line(data=aggr_rand[,c("ratio_removed", "ci_upper")], aes(x=ratio_removed, y=ci_upper), alpha=0.5) +
  xlab("Percentage removed") + ylab("Perc. in conn. comp.") +
  scale_x_continuous(breaks = seq(0, 100, 10))

# tikz(file="random_removals.tex", width=3.5, height=2.5)
# qRand
# dev.off()

png("random_removals.png", width=800, height=600)
qRand
dev.off()


##### Targeted
target_dt$ratio_removed = target_dt$ratio_removed * 100

qTarget = ggplot(target_dt, aes(x=ratio_removed, y=percentage_in_conn_comp)) +
  geom_line() +
  xlab("Percentage removed") + ylab("Perc. in conn. comp") +
  scale_x_continuous(breaks = seq(0, 100, 10))


# tikz(file="targeted_removals.tex", width=3.5, height=2.5)
# qTarget
# dev.off()

png("targeted_removals.png", width=800, height=600)
qTarget
dev.off()
