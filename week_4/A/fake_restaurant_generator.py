from faker import Faker
import numpy as np

# generates fake restaurant names and addresses
output_file = "week_4/A/fake_restaurants.csv"
fake = Faker('nl_NL')
with open(output_file, mode='w') as output:
    output.write("restaurant,address,scores\n")
    for _ in range(20):
        profile = fake.profile()
        restaurant = profile["company"]
        address = profile["address"].replace("\n", ", ")
        line = "%s,%s,%f\n"%(restaurant, address, np.nan)
        output.write(line)