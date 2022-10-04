"""
6.1 Statistics in Elasticsearch 

In Practical 4A you worked with Pandas, and you did some basic calculations, such as 
mean, median, min, and max. In Pandas, working with really large datasets can give 
problems. It can be slow, or you can run out of memory. Using Elasticsearch, you can also 
do statistics on large datasets

Lets try a basic example: calculate the average of the field total_amount in our taxi index:
"""

from elasticsearch import Elasticsearch
from auth import authorize_elastic
import json

username, password = authorize_elastic()

index_name = "taxi"

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))

search_body = {
    "size": 0,
    "aggs": {
        "avg_amount": {"avg": {"field": "total_amount"}}
    }
}

# ask the statistics for the field total_amount, for taxi trips of which the pickup location is at most 100 meters from the gps coordinate (-73.84300994873047, 40.71905517578125)
search_body = { 
    "size": 0,
    "query": {
        "bool": {
            "must": {
                "geo_distance": {
                    "distance": "100m",
                    "pickup_location": {
                        "lon": -73.84300994873047,
                        "lat": 40.71905517578125
                    }
                }
            }
        }
    },
    "aggs": {
        "statistics_amount": {"extended_stats": {"field": "total_amount"}}
    }
}

result = es.search(index="taxi", body=search_body)
# print(json.dumps(result, indent=1))
print(json.dumps(result["aggregations"]["statistics_amount"], indent=1))
