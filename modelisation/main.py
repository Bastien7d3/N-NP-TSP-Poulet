from tsp_po import solve_tsp_poulet_SEC_lazy

# --- Données ---
D = [
    [1e9, 10, 12, 20, 25],
    [10, 1e9, 8, 9, 14],
    [12, 11, 1e9, 7, 10],
    [20, 9, 10, 1e9, 5],
    [25, 14, 10, 5, 1e9],
]
TAU = [
    [1, 1.2, 1.1, 1.3, 1.0],
    [1, 1,   1.2, 1.0, 1.1],
    [1, 1.0, 1,   1.4, 1.3],
    [1, 1.1, 1.0, 1,   1.2],
    [1, 1.0, 1.3, 1.1, 1],
]
q = [0, 10, 8, 12, 5]
Q = 40
F = 300
a = 0.2
b = 0.0005

tour, cost, model = solve_tsp_poulet_SEC_lazy(D, TAU, q, Q, F, a, b, verbose=True)
print("Tournée optimale :", tour)
print("Coût (litres) :", cost)

# Afficher les arcs utilisés + conso recalculée (optionnel)
n = len(D)
x_sol = {(i, j): model.getVarByName(f"x[{i},{j}]").X for i in range(n) for j in range(n) if i != j}
arcs = [(i, j) for (i, j), v in x_sol.items() if v > 0.5]
print("Arcs choisis :", arcs)

y_vals = [model.getVarByName(f"y[{i}]").X for i in range(n)]
def compute_fuel(tour, y_vals):
    fuel = 0.0
    for t in range(n):
        i = tour[t]
        j = tour[(t + 1) % n]
        fuel += (a + b * y_vals[i]) * D[i][j] * TAU[i][j]
    return fuel
print("Conso recalculée (L) :", compute_fuel(tour, y_vals))

import csv

# --- Export tour (ordre des villes) ---
with open("tour.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["order", "node"])
    for k, node in enumerate(tour): w.writerow([k, node])

# --- Export arcs sélectionnés x_ij ---
with open("arcs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["i","j","x_ij"])
    for (i,j), v in x_sol.items(): 
        if v > 0.5: w.writerow([i,j,1])

# --- Export charges y_i ---
with open("charges.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["i","y_i"])
    for i, yi in enumerate(y_vals): w.writerow([i, yi])

# Reconstituer la charge après chaque visite selon q
charge_seq = [Q]
cur = Q
for k in range(1, len(tour)):
    cur -= q[tour[k]]
    charge_seq.append(cur)
print("Charge le long de la tournée :", list(zip(tour, charge_seq)))

time_like = sum(D[i][j]*TAU[i][j] for (i,j),v in x_sol.items() if v>0.5)
print("Somme d_ij * tau_ij :", time_like)
