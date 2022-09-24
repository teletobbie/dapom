# Exercise based on 5.4 & 5.5 
import pandas as pd
import matplotlib.pyplot as plt

file = "week_4\A\\finalRestaurants.csv"

restaurants = pd.read_csv(file, sep=";")

# count
print(restaurants["score"].count())
print(restaurants.count())

# min max
print(restaurants['score'].min())
print(restaurants['score'].max())
print(restaurants.min())
print(restaurants.max())

# mean
print(restaurants['score'].mean())
print(restaurants.mean())

# Total sum of the column values, Median of the column values & Number of unique entries
print(restaurants['score'].sum()) 
print(restaurants['score'].median()) 
print(restaurants['score'].nunique()) 

# central tendency, dispersion, and shape of a dataset’s distribution, excluding NaN values.
print(restaurants.describe()) 
# returns the 25th, 50th, and 75th percentiles
print(restaurants.describe(percentiles = [0.15, 0.3, 0.45, 0.6, 0.85 ]))

# ---------------------------------------------------------------------------------------------------

# 5.5 Graphic visualization methods
restaurants['score'].hist()
restaurants.hist()
plt.show()
