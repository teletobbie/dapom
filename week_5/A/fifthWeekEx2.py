import pandas as pd
import os
import sys
from encoding import get_encoding_from_file

def repairGender(gender : str):
    repairedGender = gender
    # if the string is not repaired after the code below, 
    # the same value that was sent is returned
    if gender == 'f' or gender == 'female' or gender == 'F' or gender == 'fem.':
        repairedGender = 'Female'
    if gender == 'm' or gender == 'male' or gender == 'M' or gender == 'man':
        repairedGender = 'Male'
    return repairedGender   

file = os.path.join(sys.path[0], "new_phdThesesFranceThirteesToNineties.csv")
encoding = get_encoding_from_file(file)

df = pd.read_csv(file, sep=",", encoding=encoding)

df["gender"] = df["gender"].apply(repairGender)
print(df["gender"])
