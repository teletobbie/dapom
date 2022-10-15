from utils.encoding import get_encoding_from_file
from db import Db
from graphs import Graphs
import pandas as pd
import numpy as np
import json
import os
import sys
import matplotlib.pyplot as plt

db = Db()
graphs = Graphs()
index_name = "belsimpel"
document_file_path = os.path.join(sys.path[0], "data_dapom.csv")
buffer_size = 5000

es = db.connect()
db.create_index_and_documents(es, index_name, document_file_path, buffer_size)

file_sizes = os.path.join(sys.path[0], "data_dapom_sizes.csv")
file_margins = os.path.join(sys.path[0], "data_dapom_margins.csv")
encode_file_sizes = get_encoding_from_file(file_sizes)
encode_file_margins = get_encoding_from_file(file_margins)

print("Creating sizes and margins dataframes")
df_sizes = pd.read_csv(file_sizes, sep=",", encoding=encode_file_sizes)
df_margins = pd.read_csv(file_margins, sep=",", encoding=encode_file_margins)

print("Get all products")
get_products_search = {
    "products": {
        "terms": {
            "field": "product_id",
            "size": 100000,
            "order": {
                "_key": "asc"
            }
        }
    }
}

all_products = es.search(index=index_name, aggs=get_products_search, size=0)
df_products = pd.json_normalize(all_products["aggregations"]["products"]["buckets"])
df_products.drop(columns=["doc_count"], inplace=True)
df_products.rename(columns={"key": "product_id"}, inplace=True)

day_count_search = {
    "unique_days_count": {
        "cardinality": {"field": "day"}
    }
}
day_count = es.search(index=index_name, aggs=day_count_search, size=0)
total_days = day_count["aggregations"]["unique_days_count"]["value"]

print("Compute basic stats of the daily demand for each of the", len(df_products), "unique products sold over", total_days, "days")
print("please wait... I am computing")
for index, row in df_products.iterrows():
    product_search_id_query = {
        "bool": {
            "must": {
                "term": {
                    "product_id": row["product_id"]
                }
            }
        }
    }

    product_search_id_aggs = {
        "days": {  # key == day, doc_count = how many products from row["product_id"] are sold per day
            "terms": {
                "field": "day",
                "size": 100000,
                # "min_doc_count": 0, # this is working to also get the 0 buckets, but this is very slow
                "order": {
                    "_key": "asc"
                }
            }
        }
    }

    product_search_result = es.search(index=index_name, query=product_search_id_query, aggs=product_search_id_aggs, size=0)

    df_demand_per_product_per_day = pd.json_normalize(product_search_result["aggregations"]["days"]["buckets"])

    # TODO: this can be an function
    # adding zeroes for the days that the product hasn't been sold
    length_df_demand_per_product_per_day = len(df_demand_per_product_per_day)

    if length_df_demand_per_product_per_day < total_days:
        zero_keys = np.arange(length_df_demand_per_product_per_day, total_days, 1)
        zero_doc_count = np.zeros(total_days - length_df_demand_per_product_per_day)
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
        df_zeroes = pd.DataFrame(
            {
                "key": zero_keys,
                "doc_count": zero_doc_count
            },
            index=zero_keys
        )
        df_demand_per_product_per_day = pd.concat([df_demand_per_product_per_day, df_zeroes])

    df_products.at[index,"total_demand"] = df_demand_per_product_per_day["doc_count"].sum()
    df_products.at[index,"average_daily_demand"] = df_demand_per_product_per_day["doc_count"].mean()
    df_products.at[index,"std_average_daily_demand"] = df_demand_per_product_per_day["doc_count"].std()

# print(df_products)

df_products["profit_margin"] = df_margins["margin"]
df_products["product_volume_cm3"] = df_sizes["length"] * df_sizes["width"] * df_sizes["height"]
df_products["average_daily_profit"] = df_products["average_daily_demand"] * df_products["profit_margin"]

print("Generating plots")

df_error_bar = df_products[["product_id", "average_daily_demand", "std_average_daily_demand"]].sort_values(by="average_daily_demand", ascending=False)

graphs.plot_error_bar(
    df_error_bar["product_id"], 
    df_error_bar["average_daily_demand"], 
    df_error_bar["std_average_daily_demand"], 
    "Products",
    "Average daily demand per day",
    "Errorbar average daily demand per day per product",
    "errorbar_daily_avg.png",
    "#B45C1F"
)


# TODO: set three classes of products based on the average daily profit (is this correct?)
bins = np.histogram_bin_edges(df_products["average_daily_profit"], bins='auto') #Get de proper amount of bins https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html
graphs.plot_hist(
    x_array=df_products["average_daily_profit"],
    xlabel="Average daily profit",
    ylabel="Amount",
    plot_title="Daily profit",
    image_title="histogram_daily_profit.png",
    bins=bins
)

bins = np.histogram_bin_edges(df_products["product_volume_cm3"], bins="auto")
graphs.plot_hist(
    x_array = df_products["product_volume_cm3"], 
    xlabel = "Product volume",
    ylabel = "Amount",
    plot_title="Product volume in cm^3",
    image_title="histogram_product_volume.png",
    bins=bins
)

"""
Product classes  
Belsimpel wants to use product classes to effectively manage its large assortment. The classification will 
be  based  on  the  importance  of  products  which  is  measured  by  the  profit  they  generate  (sales  x  profit 
margin). There will be three classes of products. These will correspond to the top 20%, following 30%, and 
the last 50% of products, respectively.

6. Make a list of products in each product class. 
7. Plot the number of products and the total average daily profit generated by the products in each 
product class on separate bar charts.  
8. Plot  the  average  daily  profits  of  each  product  on  a  bar  chart  where  products  are  sorted  in  a 
descending order based on the profit they generate. Mark the products that are at the boundaries 
of the product classes so that they are visible. 
9. Briefly comment on your observations based on the graphs you have produced
"""
#sources:
# https://stackoverflow.com/questions/38936854/categorize-data-in-a-column-in-dataframe 
# https://pandas.pydata.org/docs/reference/api/pandas.qcut.html
print("Create product classes and plot")
df_products["product_class"] = pd.qcut(df_products["average_daily_profit"], [0, .50, .80, 1.], labels=["50%", "80%", "100%"])
df_low = df_products[df_products["product_class"].str.contains("50%")].reset_index(drop=True)
df_medium = df_products[df_products["product_class"].str.contains("80%")].reset_index(drop=True)
df_high = df_products[df_products["product_class"].str.contains("100%")].reset_index(drop=True)

classes = ["last 50%", 'mid 30%', 'top 20%']
dfs_product_classes = [df_low, df_medium, df_high]
graphs.plot_product_classes(dfs_product_classes, classes)









