import os
import folium
import random
import os
import sys

possible_marker_colors = ['orange', 'black', 'lightgray', 'lightred', 'darkred', 'blue', 'beige', 'lightblue', 'cadetblue', 'darkgreen', 'purple', 'gray', 'green', 'darkpurple', 'pink', 'red', 'lightgreen', 'darkblue']

def create_map_with_markers(points: list):
    max_point = max(points)
    min_point = min(points)
    points_length = len(points)

    center_latitude = (min_point[1] + max_point[1])/2
    center_longitude = (min_point[0] + max_point[0])/2 
    center_location = [center_latitude, center_longitude]

    m = folium.Map(location=center_location, zoom_start=12)

    #TODO: create branca color scale
    get_colors = lambda n: list(map(lambda i: random.choice(possible_marker_colors),range(n)))
    colors = get_colors(points_length)

    for i in range(points_length):
        latitude = points[i][1]
        longitude = points[i][0]
        marker_location = [latitude, longitude]
        folium.Marker(
            location=marker_location, 
            popup=str(marker_location), 
            icon=folium.Icon(color=colors[i], icon="taxi", prefix="fa")).add_to(m)
    return m
    


