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

# print(df_sizes.dtypes)
# print(df_sizes.columns)
# print("\n---------------------------------------\n")
# print(df_margins.dtypes)
# print(df_margins.columns)
"""
Gather  the  following  information  for  each  product:  (1)  total  demand  on  each  day,  (2)  profit 
margin, (3) dimensions. A requirement is that you load the orders file in Elasticsearch, and that 
you will never have a complete copy of all individual orders in Python/Pandas. In this way, you 
will make it possible to scale your solution to bigger order files (more products, more days). This 
implies that you need to use Elasticsearch to aggregate individual orders to days. 
"""

search_body = {
    "size": 0,
    "aggs": {
        "products": {
            "terms": {
                "field": "product_id",
                "size": 10,
                "order": {
                    "_key":"asc"
                }
            }
        }
    }
}


result = es.search(index=index_name, body=search_body)
# print(json.dumps(result, indent=1))

df_products = pd.json_normalize(result["aggregations"]["products"]["buckets"])
df_products.rename(columns={"key": "product_id", "doc_count": "amount_sold"}, inplace=True)

for index, row in df_products.iterrows():
    print(row)
    day_search = {
        "size":0,
        "aggs": {

        }
    }

print(df_products)


# print(json_normalize(result["aggregations"]["products"]["buckets"]))
