#### Helper function(s)

## Confidence Interval calculation using a student t-test => We assume normally distributed values.
CI = function(data, conf.level = 0.95) {
  # Returns (lower, upper)
  # Check if all data entries are equal -> No confidence interval
  if(all(data == data[1])) {
    return(c(data[1], data[1]))
  }
  
  t = t.test(data, conf.level = conf.level)$conf.int
  return(c(t[1], t[2]))
}