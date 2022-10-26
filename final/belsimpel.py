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
from gurobipy import Model, GRB, multidict, quicksum
import math

db = Db()
graphs = Graphs()
index_name = "belsimpel"
document_file_path = os.path.join(sys.path[0], "data_dapom.csv")
buffer_size = 5000

# connect to elastic
es = db.connect()
# import the data from the .csv file in needed
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

# compute the daily demand per product 
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

# compute the margins, product volume and average daily profit
df_products["profit_margin"] = df_margins["margin"]
df_products["product_volume_cm3"] = df_sizes["length"] * df_sizes["width"] * df_sizes["height"]
df_products["average_daily_profit"] = df_products["average_daily_demand"] * df_products["profit_margin"]

# create the error bar
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

# plot the histogram of daily profits
bins = np.histogram_bin_edges(df_products["average_daily_profit"], bins='auto') #Get de proper amount of bins https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html
graphs.plot_hist(
    x_array=df_products["average_daily_profit"],
    xlabel="Average daily profit",
    ylabel="Amount",
    plot_title="Daily profit",
    image_title="histogram_daily_profit.png",
    bins=bins
)

# plot the histogram of product volumes
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
# cut the dataframe based on low to high average daily profit percentages (0%-50%, 50%-80%, 80%-100%)
df_products["product_class"] = pd.qcut(df_products["average_daily_profit"], [0, .50, .80, 1.], labels=["50%", "80%", "100%"])
df_low = df_products[df_products["product_class"].str.contains("50%")]
df_medium = df_products[df_products["product_class"].str.contains("80%")]
df_high = df_products[df_products["product_class"].str.contains("100%")]

print("Amount of products in class 50%", len(df_low))
print("Amount of products in class 30%", len(df_medium))
print("Amount of products in class 20%", len(df_high))

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

x = np.arange(1, len(df_products_sorted_on_profit_desc) + 1) 
y = df_products_sorted_on_profit_desc["average_daily_profit"]
cmap = ["red" if avg in boundary_avg_d_profits else "#17becf" for avg in y]
barlist = plt.bar(x, y, color=cmap, edgecolor=cmap, width=1.5)
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
# compute average demand based on the replenishment interval using Tμ
df_stock = df_stock.assign(avg_daily_demand_repln_intv=replenishment_interval * df_stock["average_daily_demand"])
# compute average std based on the replenishment interval using √Tσ
df_stock = df_stock.assign(avg_std_daily_demand_repln_intv=np.sqrt(replenishment_interval * df_stock["std_average_daily_demand"]))

# compute the base stock per product class based on the μ+zσ rule 
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
# create product couples based on each specific product correlation 
def create_product_couples(index, corr):
    global totalnr_of_highly_corr
    def is_first_product_a_higher_class(first_class_percentage : str, second_class_percentage : str):
        first_class = int(first_class_percentage.split("%")[0])
        second_class = int(second_class_percentage.split("%")[0])
        if first_class > second_class: return True
        else: return False
    # flatten the array
    flat = np.array(corr).flatten()
    #get all highly correlated products 
    result = np.where(flat >= 0.6)[0] #to get the the "natural" answer of numpy.where, we have to do [0] source: https://stackoverflow.com/questions/50646102/what-is-the-purpose-of-numpy-where-returning-a-tuple
    # check if there are highly correlated products indexes that are correlated to corr of the current product
    if len(result) > 1: 
        highly_correlated_indexes = np.array(result)
        totalnr_of_highly_corr = totalnr_of_highly_corr + len(highly_correlated_indexes)
        highly_correlated_indexes = highly_correlated_indexes[highly_correlated_indexes != index] # This removes the product index that is correlated to itself (the perfect 1.0 index)
        df_first_product = df_products.loc[df_products.index == index,:] # find the first product in df_products
        for correlated_index in highly_correlated_indexes: 
            df_second_product = df_products.loc[df_products.index == correlated_index,:] # find its pair in df_products
            # if df_first_product is of an higher class append the product ids of itself and its pair. 
            if is_first_product_a_higher_class(df_first_product["product_class"].values[0], df_second_product["product_class"].values[0]):
                product_couples.append((df_first_product["product_id"].values[0], df_second_product["product_id"].values[0]))

# loop over the correlation matrix and per iteration execute the create_product_couples() function  
[create_product_couples(index, corr) for index, corr in enumerate(corr_matrix)]
print("Found out of the", totalnr_of_highly_corr, "highly correlated products", len(product_couples), "product couples") 
print(product_couples)
print("Replot the correlation matrix marking the product couples")

# Replot the correlation matrix, but now with marked product pairs
cmap = sns.color_palette("coolwarm", as_cmap=True)
sns.heatmap(corr_matrix, cmap=cmap, cbar=True)
for couple in product_couples:
    plt.scatter(x=couple[0], y=couple[1], color="grey")
plt.title("Corr. matrix between the average daily demands of products marked")
plt.savefig(os.path.join(sys.path[0], "plots", "corr_matrix_avg_daily_demand_masked.png"))
plt.close()

"""
Step 2 Optimization
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
# copy the list in order to not change the current product couples list
current_product_couples = product_couples.copy() 

# compute the profit loss per product based on product class
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

# get the other couples id by 
# example: if product_id = 1, product_couple=(1,2) returns couple_id = 2
def get_other_couple_id(product_id : int, product_couple : tuple):
    index_current_couple = product_couple.index(product_id)
    if index_current_couple == 0:
        return product_couple[1]
    return product_couple[0]

# check if there is enough storage in the current warehouse 
def enough_storage(threshold, current_storage, product_pickup_boxes):
    if threshold - current_storage >= product_pickup_boxes:
        return True
    return False

df_products["pickup_boxes"] = df_stock["pickup_boxes"]
[compute_profit_loss(index) for index in df_products.index]

# Use pandas.rank to create an ranking based on an column 
# https://vitalflux.com/ranking-algorithms-types-concepts-examples/#:~:text=A%20ranking%20algorithm%20is%20a,dataset%20according%20to%20some%20criterion.
# https://dataindependent.com/pandas/pandas-rank-rank-your-data-pd-df-rank/
# create an ratio by dividing the average daily profit loss column by pickup_boxes column, and convert the new column to absolute values 
df_products["ratio"] = np.abs(df_products["average_daily_profit_loss"] / df_products["pickup_boxes"])
# create two columns using pandas.rank, where the ranking is based on the average daily profit loss and ratio
df_products["rank_by_profit_loss"] = df_products["average_daily_profit_loss"].rank(ascending=True, method="first") # ranking based on the highest profit loss (so this is the lowest negative number)
df_products["rank_by_ratio"] = df_products["ratio"].rank(ascending=False, method="first")

# sort the ranks in df_products into two new dataframes
df_ranked_by_profit_loss = df_products.sort_values(by="rank_by_profit_loss")
df_ranked_by_ratio = df_products.sort_values(by="rank_by_ratio")

# initialize the warehouses for the first heuristic of ranking by profit loss
df_current_warehouse = pd.DataFrame(columns=df_ranked_by_profit_loss.columns)
df_rental_warehouse = pd.DataFrame(columns=df_ranked_by_profit_loss.columns)
df_scenarios = pd.DataFrame()

def optimize_by_rank(index):
    global pickup_boxes_theshold # == 960
    global current_pickup_boxes_in_storage # == 0 
    row = df_products.loc[index, :] # the row based on index starting with the first product that has rank 1
    product_id = row["product_id"]
    # check product already stored in one of warehouses, checking both product_id columns per df
    if product_id in df_current_warehouse["product_id"].values or product_id in df_rental_warehouse["product_id"].values:
        return 
    # get product couples by current product_id
    couples_by_id = get_product_couples_by_product_id(product_id) 
    # if current warehouse storage is full, store in the rental warehouse
    if pickup_boxes_theshold == current_pickup_boxes_in_storage:
        df_rental_warehouse.loc[len(df_rental_warehouse), :] = row
        if len(couples_by_id) > 0:
            for couple in couples_by_id:
                other_couple_id = get_other_couple_id(product_id, couple)
                df_rental_warehouse.loc[len(df_rental_warehouse), :] = df_products[df_products["product_id"] == other_couple_id].squeeze()
                current_product_couples.remove(couple) # Now the couple has been allocated remove them from the current couples list
    else: 
        allocated_in_the_warehouse_indexes = [] # used to keep track of current stored products of this iteratation
        allocated_pickup_boxes_for_product = 0 # used to keep track current pickup boxes used of this iteratation
        # if not enough storage store the product in the rental warehouse and return the function
        if not enough_storage(pickup_boxes_theshold, current_pickup_boxes_in_storage, row["pickup_boxes"]):
            df_rental_warehouse.loc[len(df_rental_warehouse), :] = row
            return
        # get the next index of the current warehouse
        next_free_index_in_warehouse = len(df_current_warehouse) 
        # allocated the product to the current warehouse
        df_current_warehouse.loc[next_free_index_in_warehouse] = row 
        # add the index of the current allocated row to the list to keep track 
        allocated_in_the_warehouse_indexes.append(next_free_index_in_warehouse)
        # increment the current storage and tracking by 1
        current_pickup_boxes_in_storage += row["pickup_boxes"]
        allocated_pickup_boxes_for_product += row["pickup_boxes"]
        # check if there are product couples
        if len(couples_by_id) > 0:
            for couple in couples_by_id:
                # get the other product by current iteratation product_id
                other_couple_id = get_other_couple_id(product_id, couple)
                # get the couple
                couple_row = df_products.loc[df_products["product_id"] == other_couple_id]
                if not enough_storage(pickup_boxes_theshold, current_pickup_boxes_in_storage, couple_row["pickup_boxes"].values[0]):
                    print("Not enough storage for product", couple_row["product_id"].values[0], "coupled to", row["product_id"], "cancel allocation!")
                    # drop all looped through couples including the current row from the current warehouse
                    df_current_warehouse.drop(allocated_in_the_warehouse_indexes)
                    # free up allocated storage space again 
                    current_pickup_boxes_in_storage -= allocated_pickup_boxes_for_product
                    return # exit the function 
                next_free_index_in_warehouse = len(df_current_warehouse)
                df_current_warehouse.loc[next_free_index_in_warehouse, :] = couple_row.squeeze()
                allocated_in_the_warehouse_indexes.append(next_free_index_in_warehouse)
                current_product_couples.remove(couple)
                current_pickup_boxes_in_storage += couple_row["pickup_boxes"].values[0]

# 2.2 heuristic by highest profit loss
print("Run ranking heuristic by highest profit loss")
[optimize_by_rank(index) for index in df_ranked_by_profit_loss.index]
print(len(df_current_warehouse), "products are allocated to the current warehouse") 
print(len(df_rental_warehouse), "products are allocated to the rental warehouse") 
df_scenarios.loc[0, "avg"] = df_rental_warehouse["average_daily_profit_loss"].sum() # add avg result

# Reinitialize variables to run the ratio scenario next
df_current_warehouse = pd.DataFrame(columns=df_ranked_by_ratio.columns)
df_rental_warehouse = pd.DataFrame(columns=df_ranked_by_ratio.columns)
current_pickup_boxes_in_storage = 0
current_product_couples = product_couples.copy()

# 2.3 heuristic by highest profit loss, running the same method in order to 
print("Run ranking heuristic by ratio of the average daily profit loss / number of pick-up boxes")
[optimize_by_rank(index) for index in df_ranked_by_ratio.index]
print(len(df_current_warehouse), "products are allocated to the current warehouse") 
print(len(df_rental_warehouse), "products are allocated to the rental warehouse") 
df_scenarios.loc[0, "ratio"] = df_rental_warehouse["average_daily_profit_loss"].sum() # add ratio result

# 2.4 solving the integer problem
# sources: 
# https://www.youtube.com/watch?v=0AeGqnM04yc 
# https://www.youtube.com/watch?v=t6_Dpq7L3YQ
# https://www.gurobi.com/documentation/9.5/refman/index.html
print("Solve the 0-1 Knapsack integer problem")
w = df_products["pickup_boxes"].to_list() # weight of item / corresponding number of pickup boxes
v = df_products["average_daily_profit_loss"].to_list() # value of item / or profit loss in this case
C = pickup_boxes_theshold # max allocation 960 pickup boxes
N = len(df_products) # number of products

knapsack_model = Model("knapsack")

x = knapsack_model.addVars(N, vtype=GRB.BINARY, name="product") # add binary vars 0/1 
knapsack_model.update()

objective = quicksum(v[i]*x[i] for i in range(N))
knapsack_model.setObjective(objective, GRB.MINIMIZE) # goal: minimize the profit loss

#The weight of knapsack == 980 (max allocation to the warehouse) should not be exceeded
knapsack_model.addConstr(quicksum(w[i]*x[i] for i in range(N)) <= C, "weight") 

# add product couple constraints
# https://support.gurobi.com/hc/en-us/community/posts/4407939434385-Multi-Knapsack-Problem-with-conditional-constraint
product_couple_dict = {}
for couple in product_couples:
    fp = df_products[df_products["product_id"] == couple[0]].index.values[0]
    sp = df_products[df_products["product_id"] == couple[1]].index.values[0]
    coupled_vars = (fp, sp)
    product_couple_dict[coupled_vars] = 1

rel, val = multidict(product_couple_dict)
# product couple represtation: (x1, x2) = 1
# the sum of right side of the tuple and the left de side of the tuple must be equal
knapsack_model.addConstrs((x.sum(i, "*") <= x.sum(i2, "*") for i, i2 in rel), name="product_couple")

knapsack_model.optimize()

allocated = [i for i in range(N) if x[i].X > 0.5] 
not_allocated = [i for i in range(N) if x[i].X < 0.5]  
print(len(allocated), "products are allocated to the current warehouse") 
print(len(not_allocated), "products are allocated to the rental warehouse") 
df_scenarios.loc[0, "knapsack"] = df_products.loc[not_allocated, "average_daily_profit_loss"].sum()

fig, ax = plt.subplots()
sns.barplot(df_scenarios)
ax.bar_label(ax.containers[-1], padding=0.5, fmt='%.2f,-')
ax.set_title("Allocation heuristics overview")
ax.set_xlabel("Heuristic results")
ax.set_ylabel("Profit losses")
fig.savefig(os.path.join(sys.path[0], "plots", "overview_heuristics.png"))
plt.close()

total_time = datetime.datetime.now() - start_time
print("Computing is finished and it took", total_time)