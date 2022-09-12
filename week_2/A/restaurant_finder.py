import csv

with open("D:\RUG\dapom\week_2\A\groningenRestaurants.csv") as handler:
    content = csv.reader(handler)
    table = list(content)


for row in table[1:]:
    restaurant_name = row[0]

    if restaurant_name[0:4] == "Pizz" or restaurant_name[0:4] == "pizz":
        print("Restaurants starting with the substring Pizz or pizz", row)
        
    if restaurant_name.find("Eet") != -1 or restaurant_name.find("eet") != -1:
        print("Restaurants starting with the substring Eet or eet", row)

    restaurant_lowercase = restaurant_name.lower()
    if restaurant_lowercase.find("zuid") != -1 or restaurant_lowercase.find("noord")  != -1 or restaurant_lowercase.find("west") != -1 or restaurant_lowercase.find("oost") != -1: 
        print("Restaurants starting with the substring Zuid, Noord, West or Oost", row)


    

    
