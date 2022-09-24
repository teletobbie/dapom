import pandas as pd
import numpy as np
from nps_formula import calculate_nps
from encoding import get_encoding_from_file

file = "D:\RUG\dapom\week_4\A\\restaurantRanking.csv"
encoding = get_encoding_from_file(file)

restaurants = pd.read_csv(file, encoding=encoding, sep=",", usecols=[0, 1])

for newCol in ["nrGoodReviews", "nrBadReviews", "nrUndecided"]:
    # restaurants[newCol] = np.nan
    restaurants[newCol] = np.random.randint(0,50, size=len(restaurants))

restaurants["score"] = calculate_nps(restaurants.nrGoodReviews, restaurants.nrBadReviews, restaurants.nrUndecided)

restaurants.sort_values(by="score", inplace=True, ascending=False)
restaurants.to_csv("week_4/A/finalRestaurants.csv", sep=";", index=False)
