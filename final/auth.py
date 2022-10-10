import csv

#make sure that elastic is running in the background!
def authorize_elastic():
    with open("week_4/B/secret.csv") as handler:
        content = csv.reader(handler)
        user = list(content)
    return user[-1]


