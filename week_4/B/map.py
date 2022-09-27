import folium
import numpy as np

price_marker_colors = ['orange', 'lightred', 'red', 'darkred']

def create_color_map(colors: list, items: list):
    items = np.array_split(np.sort(items), len(colors))

    color_map = {}
    for i, item in enumerate(items):
        for inner_item in item:
            color_map[inner_item] = colors[i]  
    return color_map

def create_map_with_markers(points: list, total_amounts: list):
    max_point = max(points)
    min_point = min(points)

    center_latitude = (min_point[1] + max_point[1])/2
    center_longitude = (min_point[0] + max_point[0])/2 
    center_location = [center_latitude, center_longitude]

    m = folium.Map(location=center_location, zoom_start=12)
    colormap = create_color_map(price_marker_colors, total_amounts)

    for point, total_amount in zip(points, total_amounts):
        latitude = point[1]
        longitude = point[0]
        marker_location = [latitude, longitude]
        folium.Marker(
            location=marker_location, 
            popup="Price of taxi $" + str(total_amount) + ",-", 
            icon=folium.Icon(color=colormap[total_amount], icon="taxi", prefix="fa")).add_to(m)
    return m
    


