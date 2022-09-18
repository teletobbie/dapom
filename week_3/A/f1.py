import numpy as np
import pandas as pd

data_in_dict = { 
    "year" : [
        1950, 1951, 1952,
        1953, 1954, 1955,
        1956, 1957, 1958, 1959
    ],
    "champ" : [
        "Farina", "Fangio", "Ascari", "Ascari",
        "Fangio", "Fangio", "Fangio", "Fangio",
        "Hawthorne", "Brabham"
    ],
    "wins" : [
        3, 3, 6, 5,
        6, 4, 3, 4, 1, 2
    ],
    "points" : [
        30, 31, 36, 34,
        42, 40, 30, 40, 42, 43
    ]
}

data_in_dict["gender"] = ["m"] * 10
# print("printing first as a Python dictionary: \n", data_in_dict)

formula_one = pd.DataFrame(data_in_dict, columns = ["year", "champ", "wins", "points", "gender"])

team_wins = ["Alfa"] * 2 + ["Ferrari"] * 2 + ["Mercedes"
] * 2 + ["Ferrari", "Maserati", "Ferrari", "Cooper"]

formula_one["team"] = team_wins

print(formula_one)

# unfortunately, for long debated reasons, formula one remains still a male dominated sport). We can safely remove this monotone column gender
del(formula_one["gender"])

print("\n", formula_one)
print("\nthe size of the table is (rows * columns):")
print(formula_one.shape)
print("the rows are organized as:")
print(formula_one.columns)
print("the Python type of the values on the columns are:")
print(formula_one.dtypes)

path='week_3\\A\\'
formula_one.to_csv(path+'f1_fifties.csv')
print('\ndata frame written to csv file')