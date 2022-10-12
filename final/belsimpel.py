from elasticsearch import Elasticsearch
from auth import authorize_elastic
from encoding import get_encoding_from_file
from db import ingest_csv_file_into_elastic_index
import pandas as pd
import numpy as np
import json
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt

username, password = authorize_elastic()
index_name = "belsimpel"
buffer_size = 5000

template = {
    "number_of_shards": 1
}

prop = {
    "properties": {
        "day": {"type": "integer"},
        "product_id": {"type": "integer"}
    }
}

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))

if es.indices.exists(index=index_name) == False:
    print("haven't found an index document called", index_name)
    file = os.path.join(sys.path[0], "data_dapom.csv")
    ingest_csv_file_into_elastic_index(
        file, es, index_name, template=template, properties=prop, buffer_size=buffer_size)

file_sizes = os.path.join(sys.path[0], "data_dapom_sizes.csv")
file_margins = os.path.join(sys.path[0], "data_dapom_margins.csv")
encode_file_sizes = get_encoding_from_file(file_sizes)
encode_file_margins = get_encoding_from_file(file_margins)

df_sizes = pd.read_csv(file_sizes, sep=",", encoding=encode_file_sizes)
df_margins = pd.read_csv(file_margins, sep=",", encoding=encode_file_margins)

get_products_search = {
    "size":0,
    "aggs": {
        "products": {
            "terms": {
                "field": "product_id",
                "size": 100000,
                "order": {
                    "_key": "asc"
                }
            }
        }
    }
}

all_products = es.search(index=index_name, body=get_products_search)
df_products = pd.json_normalize(all_products["aggregations"]["products"]["buckets"])
print(df_products)
df_products["profit_margin"] = df_margins["margin"]
df_products["product_volume_cm3"] = df_sizes["length"] * df_sizes["width"] * df_sizes["height"]
df_products.drop(columns=["doc_count"], inplace=True)
df_products.rename(columns={"key": "product_id"}, inplace=True)

for index, row in df_products.iterrows():
    product_search_id = {
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "term": {
                        "product_id": row["product_id"]
                    }
                }
            }
        },
        "aggs": {
            "days": { #key == day, doc_count = how many products from row["product_id"] per day
                "terms": {
                    "field": "day",
                    "size": 100000,
                    # "min_doc_count": 0, # this is working to also get 0 buckets, but this is very slow 
                    "order": {
                        "_key": "asc"
                    }
                }
            }
        }
    }

    product_search_result = es.search(index=index_name, body=product_search_id)
    #TODO: dit klopt nog niet want de aggs neemt geen 0 waardes, dus bijv. wanneer een product op day 2 niet verkocht wordt dan moet er nul staan, dus de length van de lijst is niet hetzelfde als de oude lijst
    # maak een df en voeg daar 1 tm length(day) allemaal vol met nullen. 
    df_demand_per_product_per_day = pd.json_normalize(product_search_result["aggregations"]["days"]["buckets"])
    
    #TODO: this can be an function 
    #adding zeroes for the days that the product hasn't been sold 
    length_df_demand_per_product_per_day = len(df_demand_per_product_per_day)
    length_df_products = len(df_products)
    if length_df_demand_per_product_per_day != length_df_products:
        # create an array based on the ending point (len) of the demand per product per day until endpoint of df_products 
        zero_keys = np.arange(length_df_demand_per_product_per_day, length_df_products, 1)
        # create an array of zeros based on the difference in df length between df_products and df_demand_per_product_per_day
        zero_doc_count = np.zeros(length_df_products - length_df_demand_per_product_per_day)
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
        df_zeroes = pd.DataFrame(
            {
                "key": zero_keys,
                "doc_count": zero_doc_count
            },
            index=zero_keys
        )
        df_demand_per_product_per_day = pd.concat([df_demand_per_product_per_day, df_zeroes])

    # for key in range(len(df_demand_per_product_per_day), len(df_products)): # this is working to also fill the zero buckets, but this is very slow 
    #     df_demand_per_product_per_day.loc[key] = [key, 0]
    print("length of demand per product per day", len(df_demand_per_product_per_day))
    df_products.at[index, "total_demand"] = df_demand_per_product_per_day["doc_count"].sum()
    df_products.at[index, "average_demand_per_day"] = df_demand_per_product_per_day["doc_count"].mean()
    df_products.at[index, "std_demand_per_day"] = df_demand_per_product_per_day["doc_count"].std()

print(df_products)

df_error_bar = df_products[["product_id","average_demand_per_day","std_demand_per_day"]].sort_values(by="average_demand_per_day", ascending=False)
# print(df_error_bar)

x = np.arange(0, len(df_error_bar["product_id"]), 1) 
y = df_error_bar["average_demand_per_day"]
error = df_error_bar["std_demand_per_day"]

ax = plt.subplot()
ax.errorbar(x, y, yerr=error)
ax.set_xlabel("Products")
ax.set_xticklabels([])
ax.set_ylabel("Average daily demand per day")
ax.set_title("Errorbar average daily demand per day per product")

plt.savefig(os.path.join(sys.path[0], 'errorbar_daily_avg.png'))
# plt.show()