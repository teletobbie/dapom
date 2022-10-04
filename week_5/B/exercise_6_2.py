"""
Dapom Week 5 Practical B file 02 ElasticSearch CreateOrderIndex.py renamed
Wout van Wezel, 2020

The term bucket aggregation can be explained as follows:
- Bucket: the group of documents for which the aggregation is requested
- Aggration: the calculation that you wish to perform on each bucket. If not specified 
in Elasticsearch, it returns the count, i.e., the number of records in the bucket. 
However, you can also request calculations on fields within the bucket, e.g., min, 
max and avg of price.

https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket.html

"""


from datetime import datetime
from elasticsearch import Elasticsearch
from auth import authorize_elastic
import json

username, password = authorize_elastic()

index_name = "products"

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))
if not es.indices.exists(index=index_name):
    print("no product orders found in db, so create some records")
    es.indices.create(index='products', ignore=400)
    es.index(index=index_name, document={
        "type": "trousers", "region": "france", "price": 10})
    es.index(index=index_name, document={
        "type": "jacket", "region": "spain", "price": 25})
    es.index(index=index_name, document={
        "type": "socks", "region": "france", "price": 5})
    es.index(index=index_name, document={
        "type": "trousers", "region": "france", "price": 5})
    es.index(index=index_name, document={
        "type": "socks", "region": "spain", "price": 7})
    print("Records added")

search_body = {
    'size': 0,
    'query': {
        'bool': {
            'must': {
                'term': {
                    # only return records that are complete/exact from field value 'trousers'
                    'type.keyword': 'trousers'
                }
            }
        }
    },
    'aggs': {
        "averagePrice": {
            "avg": {
                "field": "price"
            }
        }
    }
}

# create a bucket for each unique value of a field region (France & Spain)
search_body = {
    "size": 0,
    "aggs": {
        "countPerRegion": {
            "terms": {
                "field": "region.keyword"
            }
        }
    }
}

# create buckets for the field type, and calculate the average price for records in the bucket
search_body = {
    "size": 0,
    "aggs": {
        "countPerType": {
            "terms": {
                "field": "type.keyword"
            },
            "aggs": {
                "averagePrice": {
                    "avg": {"field": "price"}
                }
            }
        }
    }
}

# Range based buckets
search_body = {
    "aggs": {
        "price_ranges": {
            "range": {
                "field": "price",
                "ranges": [
                    {"to": 5},  # lower than six
                    # higher or equal than 5 - lower than 15
                    {"from": 5, "to": 15},
                    {"from": 25}
                ]
            }
        }
    }
}

# create buckets for type, and for each of these buckets, create buckets for region
search_body = {
    "size": 0,
    "aggs": {
        "countPerType": {
            "terms": {
                "field": "type.keyword"
            },
            "aggs": {
                "countPerRegion": {
                    "terms": {"field": "region.keyword"}
                }
            }
        }
    }
}


search_body = {
    "size": 0,
    "aggs": {
        "countPerType": { #create an bucket per product type of socks, trousers, and jackets
            "terms": {
                "field": "type.keyword"
            },
            "aggs": {
                "countPerRegion": { #create an bucket per region (france & spain) of product types socks, trousers, and jackets including the avg price. 
                    "terms": {"field": "region.keyword"},
                    "aggs": { 
                        "averagePrice": { # including the avg price per product types socks, trousers, and jackets per region of France or Spain
                            "avg": {"field": "price"}
                        }
                    }
                }
            }
        }
    }
}


result = es.search(index="products", body=search_body)
print(json.dumps(result, indent=1))
