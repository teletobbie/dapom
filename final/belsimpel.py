import json
from tabnanny import check
from utils.encoding import get_encoding_from_file
from db import Db
from graphs import Graphs
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

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

# step 1.14
daily_demand_per_product = np.zeros((len(df_products) + 1, total_days))

def compute_daily_demand_on_product_id(index, product_id):

    def add_daily_demand_per_product(product_id, day, amount_sold):
        daily_demand_per_product[product_id][day - 1] = amount_sold

    product_search_id_query = {
        "bool": {
            "must": {
                "term": {
                    "product_id": product_id
                }
            }
        }
    }

    product_search_id_aggs = {
        "days": {  # key == day, doc_count = how many products from row["product_id"] are sold per day
            "histogram": { #source: ht tps://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-histogram-aggregation.html
                "field": "day",
                "interval": 1,
                "extended_bounds": { #add this return zero buckets source: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-histogram-aggregation.html#search-aggregations-bucket-histogram-aggregation-extended-bounds
                  "min": 1,
                },
                "order": {
                    "_key": "asc"
                }
            }
        }
    }

    product_search_result = es.search(index=index_name, query=product_search_id_query, aggs=product_search_id_aggs, size=0)

    df_demand_per_product_per_day = pd.json_normalize(product_search_result["aggregations"]["days"]["buckets"])

    df_products.at[index,"total_demand"] = df_demand_per_product_per_day["doc_count"].sum()
    df_products.at[index,"average_daily_demand"] = df_demand_per_product_per_day["doc_count"].mean()
    df_products.at[index,"std_average_daily_demand"] = df_demand_per_product_per_day["doc_count"].std()

    # 1.14: add the key (day) and doc_count (sold) to a destinct for the correlation matrix
    [add_daily_demand_per_product(product_id, day, amount_sold) for day, amount_sold in df_demand_per_product_per_day[["key","doc_count"]].to_numpy(dtype=int)]


start_time = datetime.datetime.now()
print("Compute basic stats of the daily demand for each of the", len(df_products), "unique products sold over", total_days, "days")
print("Starting at", start_time)
print("please wait... I am computing")
# use list comprension with an for faster iteration source: https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas 
[compute_daily_demand_on_product_id(index, product_id) for index, product_id in zip(df_products.index, df_products["product_id"])]

total_time = datetime.datetime.now() - start_time
print("Computing is finished and it took", total_time)
df_products["profit_margin"] = df_margins["margin"]
df_products["product_volume_cm3"] = df_sizes["length"] * df_sizes["width"] * df_sizes["height"]
df_products["average_daily_profit"] = df_products["average_daily_demand"] * df_products["profit_margin"]

print("Plotting daily demand")

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
print("Create product classes and plots")
df_products["product_class"] = pd.qcut(df_products["average_daily_profit"], [0, .50, .80, 1.], labels=["50%", "80%", "100%"])
df_low = df_products[df_products["product_class"].str.contains("50%")]
df_medium = df_products[df_products["product_class"].str.contains("80%")]
df_high = df_products[df_products["product_class"].str.contains("100%")]

product_classes = ["last 50%", 'mid 30%', 'top 20%']
dfs_product_classes = [df_low, df_medium, df_high]
dfs_average_profits = [df_low["average_daily_profit"], df_medium["average_daily_profit"], df_high["average_daily_profit"]]
graphs.plot_product_classes(dfs_product_classes, product_classes)
graphs.plot_total_profit_per_product_class(dfs_average_profits, product_classes)

"""
8. Plot  the  average  daily  profits  of  each  product  on  a  bar  chart  where  products  are  sorted  in  a 
descending order based on the profit they generate. Mark the products that are at the boundaries 
of the product classes so that they are visible. 
"""
# get de min / max rows from df_low, df_mid, and df_high
df_products_sorted_on_profit_desc = df_products.sort_values(by="average_daily_profit", ascending=False)

# source: https://stackoverflow.com/questions/32653825/how-to-color-data-points-based-on-some-rules-in-matplotlib
boundary_avg_d_profits = [
    df_low["average_daily_profit"].min(),
    df_low["average_daily_profit"].max(),
    df_medium["average_daily_profit"].min(),
    df_medium["average_daily_profit"].max(), 
    df_high["average_daily_profit"].min(),
    df_high["average_daily_profit"].max()
]

# colors_based_avg_profit = ["#B45C1F" if avg in boundary_products else "#1F77B4" for avg in df_products_sorted_on_profit_desc["average_daily_profit"].to_list()]
# boundary_products = df_products_sorted_on_profit_desc.loc[df_products_sorted_on_profit_desc["average_daily_profit"].isin(boundary_avg_d_profits)]["product_id"].to_list()

x = np.arange(1, len(df_products_sorted_on_profit_desc) + 1) 
y = df_products_sorted_on_profit_desc["average_daily_profit"]
cmap = ["red" if avg in boundary_avg_d_profits else "#17becf" for avg in y]

barlist = plt.bar(x, y, color=cmap, edgecolor=cmap, width=1.5)

# for bp in boundary_products:
#     #source: https://stackoverflow.com/questions/18973404/setting-different-bar-color-in-matplotlib-python
#     # barlist[bp].set_capstyle("round")
#     # barlist[bp].set_label("Product class boundaries")
#     # barlist[bp].set_color("red")
#     # barlist[bp].set_edgecolor("red")
#     barlist[bp].set_alpha(1) 

plt.xlabel("Products")
plt.ylabel("Profits")
plt.title("Average daily profits of each product")
plt.savefig(os.path.join(sys.path[0], "plots", "average_daily_profit_per_product_with_markings.png"))
plt.close()

"""
10.  Compute the average and standard deviation of the demand over the replenishment interval for 
each product.  
Hint: If the average and the standard deviation of the daily demand are μ and σ; then those of the 
demand over T days will be Tμ and √Tσ, respectively.  
11.  Compute the base-stock level for each product.  
12.  Compute the number of pick-up boxes required for each product, based on the product volumes 
and that of the standard pick-up box. Plot these on a histogram using proper number of bins. 
13.  Briefly comment on your observations based on the graph you have produced. 
"""
print("Analyze the base-stock levels and storage space")
replenishment_interval = 7 # equals 7 days in this case
pickup_box_size = (40 * 40 * 20) * 0.9
low_50_z_score = 0.99
mid_30_z_score = 0.95
top_20_z_score = 0.90

df_stock = df_products[["product_id", "average_daily_demand", "std_average_daily_demand", "product_volume_cm3", "product_class"]]
# use assign in order to avoid SettingWithCopyWarning warning: https://www.machinelearningplus.com/pandas/pandas-add-column/ 
df_stock = df_stock.assign(avg_daily_demand_repln_intv=replenishment_interval * df_stock["average_daily_demand"])
df_stock = df_stock.assign(avg_std_daily_demand_repln_intv=np.sqrt(replenishment_interval * df_stock["std_average_daily_demand"]))

def compute_base_stock(index):
    product_class = df_stock.at[index, "product_class"]
    avg_daily_demand_repln_intv = df_stock.at[index, "avg_daily_demand_repln_intv"]
    avg_std_daily_demand_repln_intv = df_stock.at[index, "avg_std_daily_demand_repln_intv"]
    if product_class == "50%":
        df_stock.at[index, "base_stock"] = avg_daily_demand_repln_intv + (low_50_z_score * avg_std_daily_demand_repln_intv)
    elif product_class == "80%":
        df_stock.at[index, "base_stock"] = avg_daily_demand_repln_intv + (mid_30_z_score * avg_std_daily_demand_repln_intv)
    elif product_class == "100%":
        df_stock.at[index, "base_stock"] = avg_daily_demand_repln_intv + (top_20_z_score * avg_std_daily_demand_repln_intv)

[compute_base_stock(index) for index in df_stock.index]

# number of pickup boxes based on the multiplying the base stock with product volume divided by the pickup box volume (all in cm3)
df_stock = df_stock.assign(pickup_boxes=np.ceil((df_stock["base_stock"] * df_stock["product_volume_cm3"]) / pickup_box_size))

bins = np.histogram_bin_edges(df_stock["pickup_boxes"], bins="auto")
graphs.plot_hist(x_array=df_stock["pickup_boxes"], xlabel="Number of pickup boxes", ylabel="Amount of products", plot_title="Number of pick-up boxes required for each product", image_title="number_of_pickup_boxes", bins=bins)


"""
Identify the product couples with highly correlated demands. 
14.  Compute  the  correlation  matrix  between  the  average  daily  demands  of  products.  Plot  the 
correlation matrix on a heatmap5. Make sure that you use a colorbar and a suitable colormap for 
better visibility.
15.  Make a list of product couples such that 
     1. the correlation coefficient between their average daily demands  are  larger  than  or  equal  to  the  threshold  value  
     2. the  first  product  belongs  to a higher class than the second product. Report the number of product couples in your list.  
16.  Plot  your  correlation  matrix  once  again  but  this  time  highlight  the  product  couples  you  have 
determined with a visible mark. 
17.  Briefly comment on your observations based on the graphs you have produced.

Sources:
https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html
https://seaborn.pydata.org/generated/seaborn.heatmap.html  
"""
print("Identify product couples with highly correlated demands")
# daily_demand_per_product returns [product_id][day] = sales 
x = daily_demand_per_product[1:] # skip the first element because this has only zeroes
corr_matrix = np.corrcoef(x)
cmap = sns.color_palette("coolwarm", as_cmap=True)
sns.heatmap(corr_matrix, cmap=cmap, cbar=True)
plt.title("Corr. matrix between the average daily demands of products")
plt.savefig(os.path.join(sys.path[0], "plots", "corr_matrix_avg_daily_demand.png"))
plt.close()

product_couples = []
totalnr_of_highly_corr = 0
#source: https://stackoverflow.com/questions/60162118/how-to-get-nth-max-correlation-coefficient-and-its-index-by-using-numpy
def create_product_couples(index, corr):
    global totalnr_of_highly_corr
    def is_first_product_a_higher_class(first_class_percentage : str, second_class_percentage : str):
        first_class = int(first_class_percentage.split("%")[0])
        second_class = int(second_class_percentage.split("%")[0])
        if first_class > second_class: return True
        else: return False

    flat = np.array(corr).flatten()
    #get all highly correlated products
    result = np.where(flat >= 0.6)[0] #to get the the "natural" answer of numpy.where, we have to do [0] source: https://stackoverflow.com/questions/50646102/what-is-the-purpose-of-numpy-where-returning-a-tuple
    if len(result) > 1: 
        highly_correlated_indexes = np.array(result)
        totalnr_of_highly_corr = totalnr_of_highly_corr + len(highly_correlated_indexes)
        highly_correlated_indexes = highly_correlated_indexes[highly_correlated_indexes != index] #This removes the product index that is correlated to itself (the perfect 1.0 index)
        df_first_product = df_products.loc[df_products.index == index,:] 
        for correlated_index in highly_correlated_indexes: 
            df_second_product = df_products.loc[df_products.index == correlated_index,:] 
            if is_first_product_a_higher_class(df_first_product["product_class"].values[0], df_second_product["product_class"].values[0]):
                corr_matrix[index, correlated_index] = np.nan
                product_couples.append((df_first_product["product_id"].values[0], df_second_product["product_id"].values[0]))

[create_product_couples(index, corr) for index, corr in enumerate(corr_matrix)]
print("Found out of the", totalnr_of_highly_corr, "highly correlated products", len(product_couples), "product couples") 
# print(product_couples)

cmap = sns.color_palette("coolwarm", as_cmap=True)
g = sns.heatmap(corr_matrix, cmap=cmap, cbar=True)
g.set_facecolor('xkcd:black')
plt.title("Corr. matrix between the average daily demands of products masked")
plt.savefig(os.path.join(sys.path[0], "plots", "corr_matrix_avg_daily_demand_masked.png"))
plt.close()

"""
1. For  all methods,  the most  critical  parameter  will  be  the  average  daily  profit  loss  per  product—
which will be realized in case the product cannot be stored in the current warehouse. Compute 
this value for each product.  
2. Implement the heuristic where the ranking is done following the average daily profit loss for each 
product. 
3. Implement the heuristic where the ranking is done following the ratio of the average daily profit 
loss to the number of pick-up boxes required for each product. 
4. Devise  an  integer  program  that  extends  the  0-1  Knapsack  problem  for  the  purposes  of  the 
allocation problem on hand. 
5. Solve  the  problem  using  all  three  approaches  you  have  devised,  and  report  the  resulting  total 
average daily profit losses on a small table.  
6. Briefly comment on your findings
"""
print("Looking for the optimal product warehouse allocation, please wait...")
pickup_boxes_theshold = 960
current_pickup_boxes_in_storage = 0
current_product_couples = product_couples

def compute_profit_loss(index):
    product_class = df_products.at[index, "product_class"]
    average_daily_profit = df_products.at[index, "average_daily_profit"]
    profit_margin = df_products.at[index, "profit_margin"]
    average_daily_demand = df_products.at[index, "average_daily_demand"]
    if product_class == "50%":
        df_products.at[index, "average_daily_profit_loss"] = ((average_daily_demand * 0.5) * profit_margin) - average_daily_profit
    elif product_class == "80%":
        df_products.at[index, "average_daily_profit_loss"] = ((average_daily_demand * 0.3) * profit_margin) - average_daily_profit
    elif product_class == "100%":
        df_products.at[index, "average_daily_profit_loss"] = ((average_daily_demand * 0.2) * profit_margin) - average_daily_profit

def get_product_couples_by_product_id(product_id : int):
    return [product_couples_by_id for product_couples_by_id in product_couples if product_couples_by_id[0] == product_id or product_couples_by_id[1] == product_id]

def get_other_couple_id(product_id : int, product_couple : tuple):
    index_current_couple = product_couple.index(product_id)
    if index_current_couple == 0:
        return product_couple[1]
    return product_couple[0]

def enough_storage(threshold, current_storage, product_pickup_boxes):
    if threshold - current_storage >= product_pickup_boxes:
        return True
    return False

df_products["pickup_boxes"] = df_stock["pickup_boxes"]
[compute_profit_loss(index) for index in df_products.index]

#Ranking 
# https://vitalflux.com/ranking-algorithms-types-concepts-examples/#:~:text=A%20ranking%20algorithm%20is%20a,dataset%20according%20to%20some%20criterion.
# https://dataindependent.com/pandas/pandas-rank-rank-your-data-pd-df-rank/
df_products["ratio"] = np.abs(df_products["average_daily_profit_loss"] / df_products["pickup_boxes"])
df_products["rank_by_profit_loss"] = df_products["average_daily_profit_loss"].rank(ascending=True, method="first") # ranking based on the highest profit loss (so this is the lowest negative number)
df_products["rank_by_ratio"] = df_products["ratio"].rank(ascending=False, method="first")

df_ranked_by_profit_loss = df_products.sort_values(by="rank_by_profit_loss")
df_ranked_by_ratio = df_products.sort_values(by="rank_by_ratio")

df_current_warehouse = pd.DataFrame(columns=df_ranked_by_profit_loss.columns)
df_rental_warehouse = pd.DataFrame(columns=df_ranked_by_profit_loss.columns)
df_scenarios = pd.DataFrame([{"total_avg_daily_profit_losses_1": 0, "total_avg_daily_profit_losses_ratio": 0, "total_avg_daily_profit_losses_knapsack": 0}])

def optimize_by_rank(index):
    global pickup_boxes_theshold
    global current_pickup_boxes_in_storage
    row = df_ranked_by_profit_loss.loc[index, :]
    product_id = row["product_id"]
    # check product already stored in one of warehouses
    if product_id in df_current_warehouse["product_id"].values or product_id in df_rental_warehouse["product_id"].values:
        return 
    # get product couples by current product_id
    couples_by_id = get_product_couples_by_product_id(product_id) # get all the couples
    # if current warehouse storage is full, store in the rental warehouse
    if pickup_boxes_theshold == current_pickup_boxes_in_storage:
        df_rental_warehouse.loc[len(df_rental_warehouse), :] = row
        if len(couples_by_id) > 0:
            for couple in couples_by_id:
                other_couple_id = get_other_couple_id(product_id, couple)
                df_rental_warehouse.loc[len(df_rental_warehouse), :] = df_ranked_by_profit_loss[df_ranked_by_profit_loss["product_id"] == other_couple_id].squeeze()
                current_product_couples.remove(couple) # Now the couple has been allocated remove them from the current couples list
    else: 
        if not enough_storage(pickup_boxes_theshold, current_pickup_boxes_in_storage, row["pickup_boxes"]):
            print("Not enough storage for product", row["product_id"], "need", row["pickup_boxes"], "pickup boxes, but only", pickup_boxes_theshold - current_pickup_boxes_in_storage, "pickup boxes are left")
            return
        df_current_warehouse.loc[len(df_current_warehouse)] = row
        current_pickup_boxes_in_storage += row["pickup_boxes"]
        if len(couples_by_id) > 0:
            for couple in couples_by_id:
                other_couple_id = get_other_couple_id(product_id, couple)
                couple_row = df_ranked_by_profit_loss.loc[df_ranked_by_profit_loss["product_id"] == other_couple_id]
                if not enough_storage(pickup_boxes_theshold, current_pickup_boxes_in_storage, couple_row["pickup_boxes"].values[0]):
                    print("Not enough storage for product", couple_row["product_id"].values[0], "need", couple_row["pickup_boxes"].values[0], "pickup boxes, but only", pickup_boxes_theshold - current_pickup_boxes_in_storage, "pickup boxes are left")
                    return
                df_current_warehouse.loc[len(df_current_warehouse), :] = couple_row.squeeze()
                current_product_couples.remove(couple)
                current_pickup_boxes_in_storage += couple_row["pickup_boxes"].values[0]
# 2.2 heuristic by highest profit loss
print("Run ranking heuristic by highest profit loss")
[optimize_by_rank(index) for index in df_ranked_by_profit_loss.index]
df_scenarios["total_avg_daily_profit_losses_1"] = df_rental_warehouse["average_daily_profit_loss"].sum()

#Reinitialize variables to run the ratio scenario
df_current_warehouse = pd.DataFrame(columns=df_ranked_by_ratio.columns)
df_rental_warehouse = pd.DataFrame(columns=df_ranked_by_ratio.columns)
current_pickup_boxes_in_storage = 0
current_product_couples = product_couples

# 2.3 heuristic by highest profit loss
print("Run ranking heuristic by ratio of the average daily profit loss / number of pick-up boxes")
[optimize_by_rank(index) for index in df_ranked_by_ratio.index]
df_scenarios["total_avg_daily_profit_losses_ratio"] = df_rental_warehouse["average_daily_profit_loss"].sum()














