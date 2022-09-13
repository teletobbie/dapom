from gurobipy import Model, GRB, quicksum

m = Model("Inventory control")

R = 10
H = 1
D = [0, 80, 100, 120, 140, 90, 140] #demand of the period t
C = [0, 100, 100, 100, 120, 120, 120] #capacity in period t

X = m.addVars(7, lb=0, ub=D, name="X") #quantity produced during period t
I = m.addVars(7, lb=0, ub=D, name="I") #inventory at end of period t
S = m.addVars(7, lb=0, ub=D, name="S") #quantity sold during period t

t = 6 #number of periods

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
    m.addConstr(I[i-1]+X[i]-S[i] == 0)

#sum(r*St - h*It)
m.setObjective(quicksum(R*S[i]-H*I[i] for i in range(t)), GRB.MAXIMIZE)

m.optimize()

# for v in m.getVars():
#     print("%s %g" % (v.varName, v.x))

print("Net profit: €%g" % m.objVal + ",-")

