import webbrowser
import gpxpy
import gpxpy.gpx
import folium
from geopy import distance
import branca.colormap

# Parsing an existing file:
# -------------------------
# source: https://github.com/tkrajina/gpxpy

gpx_file = open('D:\RUG\dapom\week_3\B\\02-Sep-2019-1316.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = []
times = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation}')
            points.append([point.latitude, point.longitude])
            times.append(point.time)

max_point = max(points)
speed = []

for index, point in enumerate(points):
    if index == len(points) - 1:
        break
    next_point = points[index + 1]
    duration_between_points = times[index + 1] - times[index]
    distance_between_points = distance.distance((point[0], point[1]), (next_point[0], next_point[1])).meters
    speed_between_points = (distance_between_points / duration_between_points.seconds) * 3.6 # https://www.inchcalculator.com/convert/meter-per-second-to-kilometer-per-hour/ 
    speed.append(speed_between_points)

# https://stackoverflow.com/questions/66546901/how-to-add-a-tooltip-to-folium-colorline-for-further-data-information
colormap = branca.colormap.linear.YlOrRd_09.scale(min(speed), max(speed)).to_step(len(speed))


m = folium.Map(location=max_point,
              zoom_start=14)

folium.ColorLine(positions=points, colormap=colormap, weight=10, colors=speed).add_to(m)

m.save("map.html")
webbrowser.open("map.html")

