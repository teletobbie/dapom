import pandas as pd
import numpy as np
from encoding import get_encoding_from_file

file = "D:\RUG\dapom\week_4\\restaurantRanking.csv"
encoding = get_encoding_from_file(file)

restaurants = pd.read_csv(file, encoding=encoding, sep=",", usecols=[0, 1])
# print("shape", restaurants.shape)
# print("columns", restaurants.columns)
# print("dtypes", restaurants.dtypes)

# generate a list full of zeroes as long as the table’s length in rows
# zeroes = [0] * restaurants.shape[0]  
# restaurants["nrGoodReviews"] = zeroes
# restaurants["nrBadReviews"] = zeroes
# restaurants["nrUndecided"] = zeroes

for newCol in ["nrGoodReviews", "nrBadReviews", "nrUndecided"]:
    restaurants[newCol] = np.nan
    # restaurants[newCol] = np.random.randint(0,50, size=len(restaurants))

restaurants.to_csv("week_4/restaurants_nan.csv", sep=";", index=False)

