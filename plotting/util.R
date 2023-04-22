#### Helper function(s)

## Confidence Interval calculation using a student t-test => We assume normally distributed values.
CI = function(data,tolerance=1e-7, conf.level = 0.95) {
  # Returns (lower, upper)
  # Check for NA
  if(any(is.na(data))) {
    return(NA)
  }
  
  # Check if all data entries are equal -> No confidence interval
  if(all(abs(data-data[1]) <=tolerance)) {
    return(c(data[1], data[1]))
  }
  
  t = t.test(data, conf.level = conf.level)$conf.int
  return(c(t[1], t[2]))
}
