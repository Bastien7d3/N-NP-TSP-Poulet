from gurobipy import Model, GRB, quicksum
import math

def solve_tsp_poulet_SEC_lazy(
    D, TAU, q, Q, F, a, b, time_limit=None, start_at=0, verbose=True
):
    """
    TSP 'Oh le poulet' avec SEC en lazy + carburant + charge + embouteillages.
    - D[i][j]   : distance de base (km)
    - TAU[i][j] : facteur d'embouteillage (>=1)
    - q[i]      : livraison au site i (q[0]=0), somme(q) <= Q
    - Q         : charge initiale (kg)
    - F         : capacité réservoir (L) (un seul plein)
    - a (L/km), b (L/(kg·km)) : conso
    """
    n = len(D)
    V = range(n)
    A = [(i, j) for i in V for j in V if i != j]

    # grand-M pour contraintes de charge (peut être Q)
    M = Q

    m = Model("TSP_Poulet_SEC_LAZY")
    if not verbose:
        m.Params.OutputFlag = 0
    if time_limit is not None:
        m.Params.TimeLimit = time_limit
    m.Params.LazyConstraints = 1

    # Variables
    
    x = m.addVars(A, vtype=GRB.BINARY, name="x")
    y = m.addVars(V, vtype=GRB.CONTINUOUS, lb=0.0, ub=Q, name="y")  # 0 <= y_i <= Q
    m.addConstr(y[0] == Q, name="charge_depot")                     # y_0 = Q
    z = m.addVars(A, vtype=GRB.CONTINUOUS, lb=0.0, name="z")        # y_i * x_ij

    # Objectif: carburant total
    def fuel_ij(i, j):
        return D[i][j] * TAU[i][j]
    m.setObjective(quicksum(
        a * fuel_ij(i, j) * x[i, j] + b * fuel_ij(i, j) * z[i, j]
        for (i, j) in A
    ), GRB.MINIMIZE)

    

    # Degré (entrée/sortie)
    m.addConstrs((quicksum(x[i, j] for j in V if j != i) == 1 for i in V), name="out_deg")
    m.addConstrs((quicksum(x[i, j] for i in V if i != j) == 1 for j in V), name="in_deg")

    # Charge au dépôt
    m.addConstr(y[0] == Q, name="charge_depot")

    # Propagation charge (si i->j est pris, y_j = y_i - q_j)
    # Propagation de la charge (seulement si j != 0)
    for i, j in A:
        if j == 0:
            continue  # ne PAS imposer y_0 = y_i sur le retour dépôt
        # y_j = y_i - q_j si l'arc i->j est pris (linéarisé)
        m.addConstr(y[j] <= y[i] - q[j] + M * (1 - x[i, j]), name=f"load_up_{i}_{j}")
        m.addConstr(y[j] >= y[i] - q[j] - M * (1 - x[i, j]), name=f"load_lo_{i}_{j}")


    # Linéarisation z_ij = y_i * x_ij
    for i, j in A:
        m.addConstr(z[i, j] <= y[i],               name=f"z_le_y_{i}_{j}")
        m.addConstr(z[i, j] <= Q * x[i, j],        name=f"z_le_Qx_{i}_{j}")
        m.addConstr(z[i, j] >= y[i] - Q*(1-x[i, j]), name=f"z_ge_yMx_{i}_{j}")



    # Réservoir: plein unique
    m.addConstr(quicksum(
        a * fuel_ij(i, j) * x[i, j] + b * fuel_ij(i, j) * z[i, j]
        for (i, j) in A
    ) <= F, name="tank_capacity")

    # ---- Callback : SEC + faisabilité retour dépôt étape par étape ----
    def extract_cycles(sol_x):
        succ = [-1] * n
        for (i, j), val in sol_x.items():
            if val > 0.5:
                succ[i] = j
        visited = [False] * n
        cycles = []
        for s in range(n):
            if not visited[s]:
                cyc = []
                cur = s
                while not visited[cur]:
                    visited[cur] = True
                    cyc.append(cur)
                    cur = succ[cur]
                if len(cyc) > 0:
                    cycles.append(cyc)
        return cycles

    def cb(model, where):
        if where != GRB.Callback.MIPSOL:
            return
        x_val = {(i, j): model.cbGetSolution(x[i, j]) for (i, j) in A}
        cycles = extract_cycles(x_val)
        if len(cycles) > 1:
            for cyc in cycles:
                if 2 <= len(cyc) < n:
                    model.cbLazy(quicksum(x[i,j] for i in cyc for j in cyc if i!=j) <= len(cyc)-1)

            # 2) Retour dépôt à chaque étape (coupures de faisabilité simples)
            #    On reconstruit le tour en partant de 0
            #    (en pratique robuste, on pourrait partir du premier succ de 0)
            #    Puis on vérifie le carburant restant contre le besoin pour retour direct.
            #    NB: coupe simple "interdire l'arc (k->k+1)" si violation repérée.
            #    (C'est une coupe paresseuse pragmatique.)
            # Reconstruire une permutation
            if len(cycles) == 1:
                succ = {i: None for i in V}
                for (i, j), val in x_val.items():
                    if val > 0.5:
                        succ[i] = j
                tour = [0]
                for _ in range(n - 1):
                    tour.append(succ[tour[-1]])

                # Simulation carburant
                fuel_used = 0.0
                for t in range(n):
                    i = tour[t]
                    j = tour[(t + 1) % n]
                    fuel_arc = (a + b * load_i) * D[i][j] * TAU[i][j]
                    # besoin pour retour direct depuis i
                    fuel_need_back = (a + b * load_i) * D[i][0] * TAU[i][0]
                    fuel_left = F - fuel_used
                    if fuel_left < fuel_need_back - 1e-6:
                        # Ajoute une coupe qui interdit cet arc i->j dans cette config
                        model.cbLazy(x[i, j] <= 0)  # simple, efficace
                        break
                    fuel_used += fuel_arc

    m.optimize(cb)


    # Extraire la tournée
    tour = []
    if m.SolCount > 0:
        x_val = {(i, j): x[i, j].X for (i, j) in A}
        # reconstruire depuis start_at
        cur = start_at
        tour = [cur]
        for _ in range(n - 1):
            nxt = max((j for j in V if j != cur), key=lambda j: x_val.get((cur, j), 0.0))
            tour.append(nxt)
            cur = nxt

    best = m.ObjVal if m.SolCount > 0 else math.inf
    return tour, best, m


