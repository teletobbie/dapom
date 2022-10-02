import pandas as pd
import os
import sys
from encoding import get_encoding_from_file 

file = os.path.join(sys.path[0], "new_phdThesesFranceThirteesToNineties.csv")
encoding = get_encoding_from_file(file)

df = pd.read_csv(file, sep=",", encoding=encoding)

df["gender"] = df["gender"].apply(lambda gender: str.title("female") if gender.lower().startswith("f") else (str.title("male") if gender.lower().startswith("m") else "?"))
print(df["gender"])