import pandas as pd
import os
import sys
import folium
import webbrowser
import random

taxi = pd.read_json(os.path.join(sys.path[0],"taxiRuns.json"), orient = 'records')

# intially pickup location has longitude - latitude values, so swap the values first to latitude - longitude : https://stackoverflow.com/questions/73074981/swap-values-of-column-of-lists-that-has-nans
taxi["pickup_location"] = taxi["pickup_location"].apply(lambda x: [x[1], x[0]])
taxi["dropoff_location"] = taxi["dropoff_location"].apply(lambda x: [x[1], x[0]])

max_point = taxi[["pickup_location", "dropoff_location"]].max(axis=1).max(axis=0) 
min_point = taxi[["pickup_location", "dropoff_location"]].min(axis=1).min(axis=0)

center_latitude = (min_point[0] + max_point[0])/2
center_longitude = (min_point[1] + max_point[1])/2 
center_location = [center_latitude, center_longitude]

m = folium.Map(location=center_location, zoom_start=10)

# plot all the routes using different colors for every route
points = taxi[["pickup_location", "dropoff_location"]]

# get an list of random colors based on the length of the points dataframe (100 entries = 100 colors) 
# source: https://stackoverflow.com/questions/9057497/how-to-generate-a-list-of-50-random-colours-in-python 
get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
colors = get_colors(len(points))

for i in range(len(points)):
    route = points.iloc[[i]]
    folium.PolyLine(route, color=colors[i]).add_to(m)

m.save(os.path.join(sys.path[0],"taxiRuns.html"))
webbrowser.open("taxiRuns.html")