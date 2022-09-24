import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({'mass' : [0.330, 4.87 , 5.972], 'radius' : [2439.7, 6051.8, 6378.1]}, index = ['Mercury', 'Venus', 'Earth'])
# we can select only one key/row if we want
df.plot.pie(y='mass', figsize=(5, 5))
df.plot.pie(y='radius', figsize=(5, 5))
# but we can also plot all in one shot
df.plot.pie(subplots = True, figsize = (6,3))
plt.show()
