import csv

with open("D:\RUG\dapom\week_2\A\groningenRestaurants.csv") as handler:
    content = csv.reader(handler)
    table = list(content)

def add_restaurant():
    name = input("restaurant name is: ")
    address = input("restaurant address is: ")
    lonlat = input("coordinates are: ")
    new_row = list((name, address, lonlat))
    table.append(new_row)
    print(name, "succesfully added")

def write_file():
    with open("D:\RUG\dapom\week_2\A\groningenRestaurants.csv", mode="w") as handler:
        content_writer = csv.writer(handler)
        for row in table:
            content_writer.writerow(row)

add_next_restaurant = True

while(add_next_restaurant):
    add_restaurant()
    next = input("do you want to input one more restaurant? (y/n)")
    if next == "y":
        print("Let's add a new restaurant")
        continue
    elif next == "n":
        print("Saving file")
        write_file()
        print("File saved bye bye")
        add_next_restaurant = False
        
        



