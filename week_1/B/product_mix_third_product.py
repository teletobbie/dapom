from gurobipy import Model, GRB

m = Model("product mix")

#decision variables
x1 = m.addVar(ub=80, name="x1") # products ub=product demand
x2 = m.addVar(ub=20, name="x2")
x3 = m.addVar(ub=20, name="x3")

#Example of an objective: sells as much as possible 
m.setObjective(45 * x1 + 60 * x2 + 90 * x3, GRB.MAXIMIZE)

#constrains can be demand, production rate in this case these are machine constraints
m.addConstr(15 * x1 + 10 * x2 + 10 * x3 <= 2400) # machine A
m.addConstr(15 * x1 + 35 * x2 + 5 * x3 <= 2400)  # machine B*
m.addConstr(15 * x1 + 5 * x2 + 18 * x3 <= 2400)  # machine C
m.addConstr(25 * x1 + 14 * x2 + 10 * x3 <= 2400) # machine D*

#examples of data 
# profits 

m.optimize()

for v in m.getVars():
    print("%s %g" % (v.varName, v.x))

print("Obj: %g" % m.objVal)