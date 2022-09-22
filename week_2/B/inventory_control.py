from gurobipy import Model, GRB, quicksum
import csv

def read_data(filepath):
    d = []
    c = []
    with open(filepath) as handler:
        content = csv.reader(handler)
        control_data = list(content)
    for data in control_data[1:]:
        d.append(int(data[0]))
        c.append(int(data[1]))
    #add 0 to the beginning of the list
    d.insert(0, 0)
    c.insert(0, 0)
    return d, c

m = Model("Inventory control")

R = 10
H = 1
D, C = read_data("D:\RUG\dapom\week_2\B\inv_control_data_1.csv")
t = len(D) #number of periods

X = m.addVars(t, lb=0, ub=C, name="X") #quantity produced during period t
I = m.addVars(t, lb=0, ub=D, name="I") #inventory at end of period t
S = m.addVars(t, lb=0, ub=D, name="S") #quantity sold during period t

m.addConstr(X[0]==0)
m.addConstr(S[0]==0)
m.addConstr(I[0]==0)

#16.2 & 16.3 constraints
for i in range(t):
    m.addConstr(X[i]<=C[i])
    m.addConstr(S[i]<=D[i])

#16.4 constraints It = It−1 + Xt − St
for i in range(t):
    if i == 0:
        continue
    m.addConstr(I[i-1]+X[i]-S[i] == I[i])

#sum(r*St - h*It)
m.setObjective(quicksum(R*S[i]-H*I[i] for i in range(t)), GRB.MAXIMIZE)

m.optimize()

# for v in m.getVars():
#     print("%s %g" % (v.varName, v.x))

print("Net profit: €%g" % m.objVal + ",-")

