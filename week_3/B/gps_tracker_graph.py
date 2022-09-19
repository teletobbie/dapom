import webbrowser
import gpxpy
import gpxpy.gpx
import folium

# Parsing an existing file:
# -------------------------
# source: https://github.com/tkrajina/gpxpy

gpx_file = open('D:\RUG\dapom\week_3\B\\02-Sep-2019-1316.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation}')
            points.append([point.latitude, point.longitude])

min_lat_long = min(points)
max_lat_long = max(points)

m = folium.Map(location=max_lat_long,
              zoom_start=14)

folium.PolyLine(points,
                color='red',
                weight=7,
                opacity=0.8).add_to(m)

m.save("map.html")
webbrowser.open("map.html")

