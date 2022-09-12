from gurobipy import Model, GRB

m = Model("product mix 2")
# demand of two products
D = [100,50]
# profits of two products
P = [45, 60]
C = [2400] * 4 #equals [2400, 2400, 2400, 2400]

#PT[0][1] corresponds to the production time of product 2 at machine A
PT=[[15,10],[15,35],[15,5],[25,14]] 

number_of_products = len(P)
number_of_machines = len(C)

x = m.addVars(number_of_products, lb=0, ub=D, name="x")

for i in range(number_of_machines):
    m.addConstr(sum(PT[i][j] * x[j] for j in range(number_of_products)) <= C[i])

m.setObjective(sum(P[i]*x[i] for i in range(number_of_products)), GRB.MAXIMIZE)

m.optimize()

for v in m.getVars():
    print("%s %g" % (v.varName, v.x))

print("Obj: %g" % m.objVal)


    













