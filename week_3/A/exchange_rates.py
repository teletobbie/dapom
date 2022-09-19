from pathlib import Path
import chardet
import pandas as pd
import numpy as np

file = "D:\RUG\dapom\week_3\A\euro-exchange-rates.csv"
detected = chardet.detect(Path(file).read_bytes())
encoding = detected.get("encoding")

eu_exchange_rates = pd.read_csv(file, encoding=encoding, sep=";")

print("\nthe size of the table is (rows * columns):")
print(eu_exchange_rates.shape)
print("the rows are organized as:")
print(eu_exchange_rates.columns)
print("the Python type of the values on the columns are:")
print(eu_exchange_rates.dtypes)
print(eu_exchange_rates)

print("EU exchange rate between",eu_exchange_rates.Period.head(1).values[0], "-", eu_exchange_rates.Period.tail(1).values[0])
currencies = eu_exchange_rates.Currency.unique()
exchange_rate_per_currency = eu_exchange_rates.groupby('Currency', dropna=True)['Rate'].apply(lambda x: list(np.unique(x))) # https://stackoverflow.com/questions/36106490/how-to-get-unique-values-from-multiple-columns-in-a-pandas-groupby
print(exchange_rate_per_currency)




