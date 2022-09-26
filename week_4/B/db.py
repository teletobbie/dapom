
from elasticsearch import Elasticsearch, helpers
import datetime

def ingest_from_file(es: Elasticsearch, file_name: str, index_name: str, template: dict, properties: dict):
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


def ingest_bulk_from_file(es: Elasticsearch, file_name: str, index_name: str, template: dict, properties: dict):
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


