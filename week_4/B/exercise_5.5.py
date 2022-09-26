from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch, helpers
from auth import authorize_elastic
import datetime
import os
import sys
import json

username, password = authorize_elastic()

def ingest_from_file(es: Elasticsearch, file_name: str, index_name: str, template: dict, properties: dict):
    # elasticsearch_cluster_object = Elasticsearch(hosts="http://elastic:vivo&Bok@localhost:9200")
    
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name, settings=template, mappings=properties)
    print("empty index", index_name, "created")

    with open(file_name) as file:
        docs = [line.strip() for line in file]
    print(file_name, "file reading ended")

    start_time = datetime.datetime.now()
    print("start indexing at", start_time)

    for doc in docs:
        print(doc)
        es.index(index=index_name, document=doc)

    total_time = datetime.datetime.now() - start_time
    print('finished after', total_time)


def taxi_rides_to_elastic(es: Elasticsearch, file_name: str, index_name: str, template: dict, properties: dict):
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name, settings=template, mappings=properties)
    print("empty index", index_name, "created")
    
    print("Reading:", file_name)
    with open(file_name) as file:
        docs = [line.strip() for line in file]
        file.close()
    print("Finished reading", len(docs), "entries from the file")
    print("Creating an bulk to index")

    start_time = datetime.datetime.now()
    actions = []
    print("start indexing at", start_time)
    for doc in docs:
        action = {
            "_index": index_name,
            "doc": doc
        }
        actions.append(action)
    
    helpers.bulk(es, actions)
    
    # es.bulk(index=index_name, body=docs)
    total_time = datetime.datetime.now() - start_time
    print('Indexing bulk finished after', total_time)

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

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))
file = os.path.join(sys.path[0],"taxi-100000.json")

taxi_rides_to_elastic(es, file, "taxi", template, prop)

# result = es.get(index="taxi", id=0)
result_all = es.search(index="taxi", body={"query":{"match_all":{}}})
print(json.dumps(result_all, indent=5))
# print(result)
# bulk_reponse = taxi_rides_to_elastic(es, file, "taxi", template, prop)


