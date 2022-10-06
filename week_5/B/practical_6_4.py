"""
6.4 Practical assignment

In the previous section, we discussed that date/time buckets can be used to get the
aggregate per day, month, etc. You will now do this for the taxi data imported in practical
4B.

1. To start, create an overview of the count per day. Use the pickup_datetime field.
Tip: use a date_histogram aggregation instead of a terms aggregation, and use the
calendar_interval parameter.

2. Second, extend your program to calculate the statistics of total_amount per day.
Study each day. Do you see any illogical results?

3. Remember that your aggregates can be filtered by adding queries. So instead of
removing illogical results from your source data, you can also filter them out at
query time. So, add a query to your request so your aggregation does not use obvious
faulty records anymore, and again calculate the statistics for total_amount per day.
Tip: you can use a range query on numerical fields.

4. Lastly, look at the final assignment. In step 1, it shows how you can aggregate over
the weekdays (Monday, Tuesday, etc.). Implement it for your taxi data to calculate
the statistics per weekday.

Tip: think about how you should change the code from the final assignment so it
considers the pickup_datetime field
Interpret the results. What would "key": "6" mean?

Sources used during this practical:
https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-datehistogram-aggregation.html 
https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-range-aggregation.html
https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-pipeline-bucket-script-aggregation.html
https://discuss.elastic.co/t/average-per-day-of-week-aggregation/124132/2 
"""

from elasticsearch import Elasticsearch
from auth import authorize_elastic
import json

username, password = authorize_elastic()

index_name = "taxi"

es = Elasticsearch(hosts=['localhost:9200'], http_auth=(username, password))

#points 1, 2, and 3
search_body = {
    "size": 1,
    "aggs": {
        "total_amount_range": {
            "range": {
                "field": "total_amount",
                "ranges": [
                    # taking out negative values and very high values
                    {"from": 0, "to": 200}
                ]
            },
            "aggs": {
                "count_per_day": {
                    "date_histogram": {
                        "field": "pickup_datetime",
                        "calendar_interval": "day"
                    },
                    "aggs": {
                        "statistics_total_amount": {"extended_stats": {"field": "total_amount"}}
                    },
                }
            }
        }
    }
}

# 4. Aggregate over the weekdays (Monday, Tuesday, etc.) and calculate the statistics per weekday
search_body = {
    "size": 0,
    "aggs": {
        "total_amount_range": {
            "range": {
                "field": "total_amount",
                "ranges": [
                    # taking out negative values and very high values
                    {"from": 0, "to": 200}
                ]
            },
            "aggs": {
                "taxi_drives_per_day": {
                    "terms": {
                        "script": {
                            "source": "doc['pickup_datetime'].value.dayOfWeek"
                        }
                    },
                    "aggs": {
                        "statistics_total_amount": {"extended_stats": {"field": "total_amount"}}
                    }
                }
            }
        }
    }
}

result = es.search(index=index_name, body=search_body)
print(json.dumps(result, indent=1))
