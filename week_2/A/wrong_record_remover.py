# EXERCISE: 
# For you to figure out (difficulty: medium, you can leave it for the homework): 
# Based on the bad_record list, eliminate the bad records from table. To solve this, you have to discover
# which method for the Python list data type is adequate to remove elements from a list.

import csv

with open("D:\RUG\dapom\week_2\A\groningenRestaurants_test.csv") as handler:
    content = csv.reader(handler)
    table = list(content)

expected_record_length = len(table[0])
incorrect_records = []
for record in table[1:]:

    if not (len(record) == expected_record_length):
        incorrect_records.append(record)
        print(record, "has", len(record), "data points")
    else:
        continue

print("Now loop over all the incorrect_records records and delete the records from the table \n")

# now loop over all the incorrect_records records and delete the records from the table
for incorrect_record in incorrect_records:
    table.remove(incorrect_record)
    print(incorrect_record, "has been deleted from the table")

print("Now test if the incorrect_records are deleted")

for record in table[1:]:
    if record in incorrect_records:
        print("Not all incorrect records are deleted:", record)
        break 

