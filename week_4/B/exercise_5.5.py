import webbrowser
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
from auth import authorize_elastic
from db import ingest_bulk_from_file
from map import create_map_with_markers
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

# indices = es.indices.get(index_name)
# print(json.dumps(indices["taxi"]["mappings"], indent=4))

search_geo = {
    "query": {
        "bool" : {
            "must" : {
                "match_all": {}
            },
            "filter" : {
                "geo_distance" : {
                    "distance" : "1000m",
                    "pickup_location" : [
                        -73.84300994873047,
                        40.71905517578125
                    ]
                }
            }
        }
    }
}

result_geo = es.search(index=index_name, body=search_geo, size=100)

pickup_locations = []
for hit in result_geo["hits"]["hits"]:
    pickup_location = hit["_source"]["pickup_location"]
    if len(pickup_location) != 0:
        pickup_locations.append(pickup_location)

m = create_map_with_markers(pickup_locations)
m.save(os.path.join(sys.path[0],"taxi_pickup_locations.html"))






