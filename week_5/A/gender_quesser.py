"""
6.7 For the curious student
Automatic gender recognition is possible to some extent. You may study this further, for example 
one current project in the ever growing Python modules development ecosystems is:
https://pypi.org/project/gender-guesser/ 

Third homework question of useing the Detector() class developed by Jorg Michael (described for use on the webpage linked above) 
and automatically complete the gender field for the those rows where we can rely only on the name of the thesis author
"""

import pandas as pd
import os
import sys
import gender_guesser.detector as gender
from encoding import get_encoding_from_file

file = os.path.join(sys.path[0], "phdThesesFranceThirteesToNineties.csv")
encoding = get_encoding_from_file(file)
d = gender.Detector()

df = pd.read_csv(file, usecols=["author_name","year_of_birth","thesis_title","year_of_defense"], sep=",", encoding=encoding)
df["gender"] = df["author_name"].apply(lambda gender: d.get_gender(gender.split(" ")[0])) # identify the gender based on the first name of the author
df=df.reindex(columns=["author_name","year_of_birth","gender","thesis_title","year_of_defense"])
print(df)