from elasticsearch import Elasticsearch
from auth import authorize_elastic
from encoding import get_encoding_from_file
from db import ingest_csv_file_into_elastic_index
import pandas as pd
import json
import os
import sys

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
df_products["profit_margin"] = df_margins["margin"]
df_products["dimensions_cm3"] = df_sizes["length"] * df_sizes["width"] * df_sizes["height"]
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
                    "order": {
                        "_key": "asc"
                    }
                }
            }
        }
    }

    product_search_result = es.search(index=index_name, body=product_search_id)
    df_demand_per_product_per_day = pd.json_normalize(product_search_result["aggregations"]["days"]["buckets"])
    df_products.at[index, "total_demand"] = df_demand_per_product_per_day["doc_count"].sum()
    df_products.at[index, "average_demand_per_day"] = round(df_demand_per_product_per_day["doc_count"].mean())
    df_products.at[index, "average_demand_std_per_day"] = df_demand_per_product_per_day["doc_count"].std()

    
