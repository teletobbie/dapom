from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
from auth import authorize_elastic
from db import ingest_bulk_from_file
import os
import sys

username, password = authorize_elastic()

template = {
    "number_of_shards": 3
}

prop = {
    'properties': {
        'pickup_datetime': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss"},
        'dropoff_datetime': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss"},
        'pickup_location': {'type': 'geo_point'},
        'dropoff_location': {'type': 'geo_point'}
    }
}

index_name = "taxi"

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))



# check if taxi indices already exists in elastic search, if not, then create it. 
if es.indices.exists(index=index_name) == False:
    print("haven't found an index document called", index_name)
    file = os.path.join(sys.path[0],"taxi-100000.json")
    ingest_bulk_from_file(es, file, index_name, template, prop)

result_all = es.search(index=index_name, body={"query":{"match_all":{}}})
print(result_all)



