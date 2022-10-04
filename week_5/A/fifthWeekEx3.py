import pandas as pd
import os
import sys
from encoding import get_encoding_from_file

def repairYearOfBirth(yearOfBirth : str):
    chars_to_replace =  ["c", "C", ".", "(", ")"] 
    repairedYearOfBirth = yearOfBirth
    for char in chars_to_replace:
        repairedYearOfBirth = repairedYearOfBirth.replace(char, "") 
    if "-" in repairedYearOfBirth:
        year_range = list(map(int, repairedYearOfBirth.split("-"))) 
        repairedYearOfBirth = str(round(sum(year_range) / len(year_range)))
    return repairedYearOfBirth



file = os.path.join(sys.path[0], "new_phdThesesFranceThirteesToNineties.csv")
encoding = get_encoding_from_file(file)

df = pd.read_csv(file, sep=",", encoding=encoding)

df["year_of_birth"] = df["year_of_birth"].apply(repairYearOfBirth)

df.to_csv(os.path.join(sys.path[0], "phdThesesFranceThirteesToNineties_2.csv"), sep=",", index=False)

