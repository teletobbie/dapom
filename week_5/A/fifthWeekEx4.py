"""
6.6 More to do
The code in this file will read the 
third csv file you saved previously and compute the answers to the two (actually three) questions for 
the intended data analysis:

1. What is the average age of when a PhD candidate defended its thesis?
2. What is the average age of female candidates, and also what is the average age of male 
candidates?

"""

import pandas as pd
import os
import sys
from encoding import get_encoding_from_file

file = os.path.join(sys.path[0], "phdThesesFranceThirteesToNineties_2.csv")
encoding = get_encoding_from_file(file)

df = pd.read_csv(file, sep=",", encoding=encoding)
df["gender"] = df["gender"].apply(lambda gender: str.title("female") if gender.lower().startswith("f") else (str.title("male") if gender.lower().startswith("m") else "?"))

avg_year_of_defense = round(df["year_of_defense"].mean())
avg_age_year = round(df["year_of_birth"].mean())
print("Average age of PhD candidate defense based on year", avg_age_year, "is:", avg_year_of_defense - avg_age_year, "years old")

df_female_candidates = df[["gender", "year_of_birth"]].loc[df["gender"].str.startswith("F")]
max_age_female = df_female_candidates["year_of_birth"].max()
avg_age_female = round(df_female_candidates["year_of_birth"].mean())
print("Average age of PhD female candidate based on year", max_age_female, "is:", max_age_female - avg_age_female, "years old")

df_male_candidates = df[["gender", "year_of_birth"]].loc[df["gender"].str.startswith("M")]
max_age_male = df_male_candidates["year_of_birth"].max()
avg_age_male = round(df_male_candidates["year_of_birth"].mean())
print("Average age of PhD male candidate based on year", max_age_male, "is:", max_age_male - avg_age_male, "years old")