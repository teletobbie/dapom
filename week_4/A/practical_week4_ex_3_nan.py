import pandas as pd
from nps_formula import calculate_nps

file = "D:\RUG\dapom\week_4\A\\restaurants_nan.csv"
restaurants = pd.read_csv(file, sep=";")

restaurants_without_reviews= restaurants[restaurants[["nrGoodReviews", "nrBadReviews", "nrUndecided"]].isnull().all(1)]
restaurants_with_reviews = restaurants.dropna()
restaurants_with_reviews["score"] = calculate_nps(restaurants.nrGoodReviews, restaurants.nrBadReviews, restaurants.nrUndecided)
print(restaurants_with_reviews)