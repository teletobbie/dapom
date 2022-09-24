from datetime import datetime
from elasticsearch import Elasticsearch
from auth import authorize_elastic

username, password = authorize_elastic()

es = Elasticsearch(
    hosts=['localhost:9200'],
    http_auth=(username, password),
)
es.indices.create(index='persons', ignore=400) # an table
es.index(index="persons", id=1, document={"name": "tobias", "hobby": "programming yes yes", "age": 27, "timestamp": datetime.now()}) # data in the table
es.index(index="persons", id=2, document={"name": "anna", "hobby": "netflix", "age": 16, "timestamp": datetime.now()})
result = es.get(index="persons", id=1)
print(result, "\n")
print(result['_source']['hobby'])