
from elasticsearch import Elasticsearch, helpers
from encoding import get_encoding_from_file
import pandas as pd
import uuid
import datetime
import json

def convert_csv_file_to_bufferized_json_lines_list(csv_file_name: str, buffer_size):
    encoding = get_encoding_from_file(csv_file_name)
    df = pd.read_csv(csv_file_name, encoding=encoding)
    json_list = json.loads(df.to_json(orient='records'))

    buffer_list = []
    total_nr_docs = len(json_list)
    for i in range(0, total_nr_docs, buffer_size):
        buffer_list.append(json_list[i: i + buffer_size])
    return buffer_list

def bulk_json(json_buffer, _index):
    for doc in json_buffer:
        # use a `yield` generator so that the data
        # isn't loaded into memory
        if '{"index"' not in doc:
            yield {
                "_index": _index,
                "_id": uuid.uuid4(),
                "_source": doc
            }

def ingest_csv_file_into_elastic_index(csv_file_name: str, es: Elasticsearch, index_name: str, template = {}, properties = {}, buffer_size=5000):
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name, settings=template, mappings=properties)
    print("empty index", index_name, "created")
    
    start_time = datetime.datetime.now()
    print("Creating an elastic search index bulk for", index_name, "at", start_time)
    print("Convert data to chunks of", buffer_size, "please wait...")
    chunks = convert_csv_file_to_bufferized_json_lines_list(csv_file_name, buffer_size=buffer_size)
    print("Chunks created, start indexing bulk...")
    for i, buffer in zip(range(len(chunks)), chunks):
        try:
            response = helpers.bulk(es, bulk_json(json_buffer=buffer, _index=index_name))
            print("bulk_json() RESPONSE for chunk:", i, response)
        except Exception as e:
            print("\nERROR:", e)
    total_time = datetime.datetime.now() - start_time
    print('Indexing bulk finished after', total_time)




