import statistics

a = [-16, 9, -4, 5, 66, 34, 28, 22, -90]
av = statistics.mean(a)
med = statistics.median(a)
mod = statistics.mode(a)
sigma = statistics.stdev(a)
var = statistics.variance(a)
print("vector", a)
print("\nhas average", av)
print("\nhas median", med)
print("\nhas mode", mod) # If there are no repeating numbers in a given list then python will take the first one (-16)
print("\nhas an variance", var)


