import pandas as pd
import os
import sys
from encoding import get_encoding_from_file

file = os.path.join(sys.path[0], "phdThesesFranceThirteesToNineties.csv")
encoding = get_encoding_from_file(file)

df = pd.read_csv(file, sep=",", encoding=encoding)

print(df.shape)
print(df.columns)
print(df.dtypes)

print("Year range:", df["year_of_defense"].min(), "-", df["year_of_defense"].max())

odf = df.sort_values(by=["gender"])

print("gender field appears:", df["gender"].nunique(), "kinds\n", 
    "each occurs:\n kind     occurences\n", df["gender"].value_counts())

print("year of birth field appears:", df["year_of_birth"].nunique(), "kinds\n", 
    "each occurs:\n kind     occurences\n", df["year_of_birth"].value_counts())

odf.to_csv(os.path.join(sys.path[0], "new_phdThesesFranceThirteesToNineties.csv"), sep=",", index=False)