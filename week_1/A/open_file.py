# first version
# file = open("week_1/A/storage.txt")
# print(file.read())
# file.close()

# second version
with open("week_1/A/storage.txt") as file:
    content = str(file.read())
    print(content)