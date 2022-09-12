# - What is the average latitude and longitude of all these restaurants (the geographical “center of gravity point”)

#TODO
# - How many restaurants are north of a user-inputted parallel? 
# - Take a lon-lat coordinate from the user (or for example, just use the newly found “center of gravity” point) and make four separate files, each containing the restaurants in a quadrant (NW, NE, SE, SW) defined by the given coordinate.

import csv

with open("D:\RUG\dapom\week_2\A\groningenRestaurants.csv") as handler:
    content = csv.reader(handler)
    table = list(content)

lat_list = []
long_list = []

for row in table[1:]:
    lat_long = row[2]
    lat, long = lat_long.split(",")
    lat_list.append(float(lat))
    long_list.append(float(long))

print("Average lat long of all restaurants:", sum(lat_list) / len(lat_list),",",sum(long_list) / len(long_list))
