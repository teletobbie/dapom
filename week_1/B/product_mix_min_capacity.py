from gurobipy import Model, GRB

m = Model("product mix")

#decision variables
x1 = m.addVar(lb=100, name="x1") # products ub=product demand
x2 = m.addVar(lb=50, name="x2")

c1 = m.addVar(name="capacity 1")
c2 = m.addVar(name="capacity 2")
c3 = m.addVar(name="capacity 3")
c4 = m.addVar(name="capacity 4")

#Example of an objective: sells as much as possible 
m.setObjective(c1 + c2 + c3 + c4, GRB.MINIMIZE)

#constrains can be demand, production rate in this case these are machine constraints
m.addConstr(15 * x1 + 10 * x2 <= c1) # machine A
m.addConstr(15 * x1 + 35 * x2 <= c2) # machine B*
m.addConstr(15 * x1 + 5 * x2 <= c3)  # machine C
m.addConstr(25 * x1 + 14 * x2 <= c4) # machine D*

#examples of data 
# profits 

m.optimize()

for v in m.getVars():
    print("%s %g" % (v.varName, v.x))

print("Objective minimum capacity: %g" % m.objVal)