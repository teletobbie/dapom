from gurobipy import Model, GRB

m = Model("product mix")

x1 = m.addVar(ub=100, name="x1") 
x2 = m.addVar(ub=50, name="x2")

m.setObjective(45 * x1 + 60 * x2, GRB.MAXIMIZE)

m.addConstr(15 * x1 + 10 * x2 <= 2400) # machine A
m.addConstr(15 * x1 + 35 * x2 <= 2400) # machine B*
m.addConstr(15 * x1 + 5 * x2 <= 2400)  # machine C
m.addConstr(12 * x1 + 10 * x2 <= 2400) # machine D*
m.addConstr(13 * x1 + 7 * x2 <= 1500) # machine E

m.optimize()

for v in m.getVars():
    print("%s %g" % (v.varName, v.x))

print("Obj: %g" % m.objVal)