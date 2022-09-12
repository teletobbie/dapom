import csv

with open("D:\RUG\dapom\week_2\A\groningenRestaurants.csv") as handler:
    content = csv.reader(handler)
    table = list(content)

# print("data records =", len(table)) #how many records 
# print("table header =", table[0]) #first row
# print("last record in the table = ", table[-1][0]) 
# print("data points in a record =", len(table[0]))

# for record in table:
#     print(len(record))

# for record in table[1:]:
#     address = record[1]
#     geolocation = record[2]
#     name=record[0]
#     print("\nAt:", address, "\ncoord.:", geolocation, "\nis:", name)

# expected_record_length = len(table[0])
# wrong_length_record_counter = 0
# for record in table[1:]:

#     if not (len(record) == expected_record_length):
#         wrong_length_record_counter += 1
#         print(record, "has", len(record), "data points")
#         break
#     else:
#         continue

#Selecting records
for row in table[1:]:
    name = row[0]
    address = row[1]
    if name[0] == "D" and address[0] == "R":
        print(row)