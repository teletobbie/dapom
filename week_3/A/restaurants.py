from pathlib import Path
import chardet
import pandas as pd

file = "D:\RUG\dapom\week_3\A\groningenRestaurants.csv"
detected = chardet.detect(Path(file).read_bytes())
encoding = detected.get("encoding")

restaurants = pd.read_csv(file, encoding=encoding)
# shorter and easier than the with, open, read, list() construct
random_selection = restaurants.sample(12)
# print(random_selection[["restaurant","lonlat"]])

print("\n", random_selection)
print("\nthe size of the table is (rows * columns):")
print(random_selection.shape)
print("the rows are organized as:")
print(random_selection.columns)
print("the Python type of the values on the columns are:")
print(random_selection.dtypes)

#change settings for showing the different columns
# pd.set_option('display.max_rows', restaurants.shape[0])
# pd.set_option('display.max_columns', restaurants.shape[1])
# pd.set_option('display.width', 1000) #characters in one line width
# print(restaurants)

print("\n1. Looking in restaurants in with the names start with Pizz or pizz")
# df4[df4['col'].str.contains(r'foo|baz')] https://stackoverflow.com/questions/11350770/filter-pandas-dataframe-by-substring-criteria
restaurants_starting_with_Pizz_pizz = restaurants[restaurants["restaurant"].str.contains(r'Pizz|pizz')]
print(restaurants_starting_with_Pizz_pizz)
print("\n2. Looking in restaurants in with the names start with Eet or eet")
restaurants_starting_with_Eet_eet = restaurants[restaurants["restaurant"].str.contains(r'Eet|eet')]
print(restaurants_starting_with_Eet_eet)
print("\n2. Looking in restaurants in with the address includes noord, zuid, west and oost")
restaurant_address_starting_with_NOZW = restaurants[restaurants["address"].str.contains(r'Zuid|zuid|Oost|oost|West|west|Noord|noord')]
print(restaurant_address_starting_with_NOZW)