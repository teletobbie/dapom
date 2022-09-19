import gpxpy
import gpxpy.gpx
from geopy import distance

# Parsing an existing file:
# -------------------------
# source: https://github.com/tkrajina/gpxpy

gpx_file = open('D:\RUG\dapom\week_3\B\course_sempachersee.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation}')
            points.append([point.latitude, point.longitude, point.time])

print("Starting point", points[0]) 
print("End point", points[-1])
duration = points[-1][2] - points[0][2] #substract the timedelta from the endpoint with the startingpoint
print("Total duration of the track", duration)
print("Total duration of the track in seconds", duration.seconds)

# compute the distance between the first two points using https://github.com/geopy/geopy
p1, p2 = points[:2]
print(
    "distance between first two points in meters: ",
    distance.distance((p1[0], p1[1]), (p2[0], p2[1])).meters
)

# compute the total distance between all the points
total_distance = 0
for index, point in enumerate(points): # source: https://stackoverflow.com/questions/522563/accessing-the-index-in-for-loops
    if index == len(points) - 1: 
        break
    next_point = points[index + 1]
    total_distance += distance.distance((point[0], point[1]), (next_point[0], next_point[1])).meters
print("Total distance between all point", total_distance, "meters")

# compute the average speed is distance traveled divided by time taken
average_speed = total_distance / (duration.seconds // 3600) # // is used instead of / to get an integer, not an float, because you cannot have 1.2564454121 hours :).
print("Average speed of the track is", average_speed, "meters per hour")

