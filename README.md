# DAPOM
This codebase includes implementations of the weekly exercises and the final assignment of the course Data Analysis and Programming for Operations Management. 

## Prerequisites
In order to run this codebase the following requirements have to be satisfied.

- Have the lastest version of [python](https://www.python.org/) installed (codebase current version is 3.10.4) 
- Have [Gurobi](https://www.gurobi.com) installed on your machine
- Have [Elasticsearch](https://www.elastic.co/) installed and the server running on your machine

## For running
In order to run the codebase follow these directions:
1. `git clone` the project or download it via this page
2. Run `pip install -r requirements.txt` in the root project directory /dapom
3. Have elasticsearch server running (see prerequisites point 3)

### Extra note 
For running the final assignment change the secret.csv file in /dapom/final/utils folder to your elastic username and password. After this, you can run the final by starting the `belsimpel.py`