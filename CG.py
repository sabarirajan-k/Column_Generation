from gurobipy import Model, GRB, quicksum
import gurobipy as gp
import numpy as np
import math
from colorama import Fore, Style

# Define input data
n = [i for i in range(3)]
D = {0: 150, 1: 200, 2: 300}
l = {0: 5, 1: 7, 2: 9}
pattern = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

# Function to define the master problem
def define_master_problem(pattern):
    pattern_range = range(len(pattern))
    pattern = np.array(pattern, dtype=int)
    
    m = gp.Model("master_problem")
    x = m.addVars(pattern_range, vtype=GRB.CONTINUOUS, name="x")

    m.setObjective(quicksum(x[i] for i in pattern_range), GRB.MINIMIZE)
    m.addConstrs(quicksum(pattern[i, j] * x[i] for i in pattern_range) == D[j] for j in n)
    
    return m

# Function to define the subproblem
def define_subproblem(dual_variables):
    s = gp.Model("sub_problem")
    
    y = s.addVars(n, vtype=GRB.INTEGER, name="y")
    s.setObjective(quicksum(y[i] * dual_variables[i] for i in n), GRB.MAXIMIZE)
    s.addConstr(quicksum(l[i] * y[i] for i in n) <= 20)
    
    return s

# Function to print the solution
def print_solution(m, pattern):
    use = [math.ceil(var.x) for var in m.getVars()]
    
    for i, p in enumerate(pattern):
        if use[i] > 0:
            print(f"\nPattern {i}: Number of times to be used: {use[i]}")
            print("------------------------------")
            for j, order in enumerate(p):
                if order > 0:
                    print(f"Order {j} cut from pattern {i}: {order}")
    print(f"\nTotal number of rolls used: {int(np.sum(use))}")

# Function for column generation
def column_generation():
    objVal_history = []
    iteration = 1
    
    while True:
        print(f"\nIteration {iteration}")
        print("-------------------------")
        m = define_master_problem(pattern)
        m.optimize()
        objVal_history.append(m.objVal)
        
        dual_variables = np.array([constraint.pi for constraint in m.getConstrs()])
        print(Fore.RED + f"Shadow prices: {dual_variables}" + Style.RESET_ALL)
        
        s = define_subproblem(dual_variables)
        s.optimize()
        
        if s.objVal < 1 + 1e-2:
            break
        
        new_pattern = [int(var.x) for var in s.getVars()]
        pattern.append(new_pattern)
        print(Fore.GREEN + f"New pattern added: {new_pattern}" + Style.RESET_ALL)
        
        iteration += 1
    
    print_solution(m, pattern)
    return objVal_history

# Run column generation
Sol = column_generation()
