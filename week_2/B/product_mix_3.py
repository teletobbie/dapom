from gurobipy import Model, GRB

def optimize(m, D, P, C, PT):
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

m = Model("product mix 3")
D = [100,50]
P = [45, 60]
C = [2400] * 4 
PT=[[15,10],[15,35],[15,5],[25,14]] 

optimize(m, D, P, C, PT)
