import random  # Pour générer des nombres aléatoires
import numpy as np  # Pour les matrices et calculs numériques
import matplotlib.pyplot as plt  # Pour les graphiques

# --- Génération du scénario TSP pour livraison de poulets ---
def generer_scenario(N, distance_min=5, distance_max=100,
                     charge_fixe_par_livraison=50, capacite_max_charge=1000, 
                     reservoir_carburant=100, embouteillage_min=0.8, embouteillage_max=1.5):
    """
    Génère un scénario de problème TSP pour la livraison de poulets avec embouteillages
    
    Args:
        N: Nombre total de villes (incluant le dépôt)
        distance_min/max: Plage des distances de base entre villes (en km)
        charge_fixe_par_livraison: Charge fixe livrée à chaque arrêt (en kg)
        capacite_max_charge: Capacité maximale du camion (en kg)
        reservoir_carburant: Capacité du réservoir en litres
        embouteillage_min/max: Facteur d'embouteillage (1.0 = normal, >1.0 = ralentissement)
    
    Returns:
        dict: Dictionnaire contenant tous les paramètres du scénario
    """
    # Création de la matrice des distances de base (graphe complet non orienté)
    distances_base = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):  # Parcourir seulement la moitié supérieure de la matrice
            dist = random.randint(distance_min, distance_max)  # Distance de base aléatoire
            distances_base[i][j] = dist  # Affecter la distance
            distances_base[j][i] = dist  # Matrice symétrique (distance i->j = distance j->i)
    
    # Génération des facteurs d'embouteillage pour chaque tronçon
    facteurs_embouteillage = np.ones((N, N))  # Matrice des facteurs d'embouteillage
    for i in range(N):
        for j in range(i+1, N):
            # Facteur aléatoire d'embouteillage (1.0 = normal, >1.0 = plus lent)
            facteur = random.uniform(embouteillage_min, embouteillage_max)
            facteurs_embouteillage[i][j] = facteur
            facteurs_embouteillage[j][i] = facteur  # Matrice symétrique
    
    # Calcul des distances réelles avec embouteillages
    distances_reelles = distances_base * facteurs_embouteillage

    # Génération de la charge à livrer par ville (ville 0 = dépôt)
    # Chaque ville reçoit une charge fixe
    charges_par_ville = [0]  # Le dépôt (ville 0) n'a pas de charge à livrer
    charges_par_ville.extend([charge_fixe_par_livraison for _ in range(N - 1)])  # Charge fixe par ville
    
    # Construction du dictionnaire de retour avec tous les paramètres
    scenario = {
        'distances_base': distances_base,  # Distances de base sans embouteillages
        'distances_reelles': distances_reelles,  # Distances avec embouteillages
        'facteurs_embouteillage': facteurs_embouteillage,  # Facteurs d'embouteillage par tronçon
        'charges_par_ville': charges_par_ville,  # Charge à livrer par ville (kg)
        'charge_fixe_par_livraison': charge_fixe_par_livraison,  # Charge fixe par livraison
        'capacite_max_charge': capacite_max_charge,  # Capacité maximale du camion (kg)
        'reservoir_carburant': reservoir_carburant  # Capacité du réservoir de carburant
    }
    return scenario

# --- Calcul de la consommation de carburant ---
def consommation_carburant(distance_reelle, charge_actuelle):
    """
    Calcule la consommation de carburant en fonction de la distance réelle et de la charge
    
    Cette fonction implémente un modèle réaliste de consommation :
    - Consommation de base pour un camion vide
    - Augmentation proportionnelle au poids transporté
    - Prise en compte des embouteillages via la distance réelle
    
    Args:
        distance_reelle: distance à parcourir en km (avec embouteillages)
        charge_actuelle: charge actuelle du camion en kg
    
    Returns:
        consommation en litres pour parcourir cette distance
    """
    poids_vide_camion = 3000  # Poids du camion vide en kg
    poids_total = poids_vide_camion + charge_actuelle  # Poids total chargé
    
    # Modèle de consommation amélioré :
    # - Consommation de base : 8L/100km pour un camion vide
    # - Augmentation de 2% par tranche de 100kg de charge supplémentaire
    # - Les embouteillages sont déjà pris en compte dans distance_reelle
    consommation_base = 8  # L/100km (optimisé pour minimiser la consommation)
    facteur_charge = 1 + (charge_actuelle / 100) * 0.02  # Facteur d'augmentation plus réaliste
    consommation_aux_100km = consommation_base * facteur_charge  # Consommation réelle aux 100km
    
    # Calcul final : (distance_reelle/100) * consommation_aux_100km
    return (distance_reelle / 100) * consommation_aux_100km

# --- Algorithme TSP optimisé pour minimiser la consommation et maximiser les livraisons ---
def tsp_livraison_optimise(scenario):
    """
    Résout le problème TSP avec optimisation bi-objectif :
    1. Minimiser la consommation totale de carburant
    2. Maximiser le nombre de livraisons effectuées
    
    Contraintes prises en compte :
    1. Capacité maximale du camion en charge (kg)
    2. Contrainte de carburant (doit pouvoir revenir au dépôt)
    3. Chaque ville doit être visitée au plus une fois
    4. Charge fixe livrée à chaque arrêt
    5. Embouteillages affectant les distances réelles
    
    Stratégie : Heuristique gloutonne optimisant le rapport efficacité/distance
    
    Args:
        scenario: dictionnaire contenant tous les paramètres du problème
    
    Returns:
        tuple: (ordre_villes_visitees, consommation_totale, nb_livraisons, charge_totale_livree)
    """
    N = len(scenario['distances_reelles'])  # Nombre total de villes
    villes_non_visitees = set(range(1, N))  # Ensemble des villes à visiter (exclut le dépôt ville 0)
    ordre_villes = []  # Liste ordonnée des villes visitées
    ville_actuelle = 0  # Position actuelle (commence au dépôt)
    
    # État du camion au départ
    charge_actuelle = scenario['capacite_max_charge']  # Camion plein au départ
    carburant_restant = scenario['reservoir_carburant']  # Réservoir plein au départ
    
    # Variables de suivi des objectifs
    consommation_totale = 0  # Carburant total consommé (à minimiser)
    nb_livraisons = 0  # Nombre de livraisons effectuées (à maximiser)
    charge_totale_livree = 0  # Charge totale livrée

    # Boucle principale : continuer tant qu'il reste des villes et de la charge
    while villes_non_visitees and charge_actuelle >= scenario['charge_fixe_par_livraison']:
        # Étape 1 : Déterminer les villes accessibles avec contraintes multiples
        # Une ville est accessible si :
        # - On a assez de charge pour effectuer la livraison
        # - On a assez de carburant pour y aller ET revenir au dépôt
        villes_accessibles = []
        for ville in villes_non_visitees:
            charge_requise = scenario['charges_par_ville'][ville]  # Charge nécessaire pour cette ville
            
            # Vérifier si on a assez de charge pour cette livraison
            if charge_requise <= charge_actuelle:
                # Calculer la consommation pour aller à cette ville (avec embouteillages)
                distance_aller = scenario['distances_reelles'][ville_actuelle][ville]
                consommation_aller = consommation_carburant(distance_aller, charge_actuelle)
                
                # Calculer la consommation pour revenir au dépôt depuis cette ville
                # (avec moins de charge car on aura livré)
                distance_retour = scenario['distances_reelles'][ville][0]
                charge_apres_livraison = charge_actuelle - charge_requise
                consommation_retour = consommation_carburant(distance_retour, charge_apres_livraison)
                
                # Vérifier si on a assez de carburant pour le trajet complet
                if consommation_aller + consommation_retour <= carburant_restant:
                    villes_accessibles.append(ville)  # Cette ville est accessible
        
        # Si aucune ville n'est accessible, arrêter l'algorithme
        if not villes_accessibles:
            break  # Plus de villes accessibles avec les contraintes actuelles
        
        # Étape 2 : Optimiser le choix selon un critère composite
        # Critère : minimiser le ratio (consommation / efficacité)
        # où efficacité = charge_livrée / distance_parcourue
        def critere_optimisation(ville):
            distance_reelle = scenario['distances_reelles'][ville_actuelle][ville]
            charge_livree = scenario['charges_par_ville'][ville]
            consommation = consommation_carburant(distance_reelle, charge_actuelle)
            
            # Efficacité : charge livrée par km parcouru
            efficacite = charge_livree / distance_reelle if distance_reelle > 0 else 0
            
            # Critère composite : favoriser faible consommation ET haute efficacité
            return consommation / (efficacite + 0.1)  # +0.1 pour éviter division par zéro
        
        # Choisir la ville optimisant le critère composite
        meilleure_ville = min(villes_accessibles, key=critere_optimisation)
        
        # Étape 3 : Effectuer le déplacement vers la ville optimale
        distance_parcourue = scenario['distances_reelles'][ville_actuelle][meilleure_ville]
        consommation_trajet = consommation_carburant(distance_parcourue, charge_actuelle)
        charge_livree = scenario['charges_par_ville'][meilleure_ville]
        
        # Mettre à jour tous les états après le déplacement et la livraison
        ordre_villes.append(meilleure_ville)  # Ajouter la ville à l'itinéraire
        consommation_totale += consommation_trajet  # Cumuler la consommation
        carburant_restant -= consommation_trajet  # Décrémenter le carburant restant
        nb_livraisons += 1  # Incrémenter le nombre de livraisons
        charge_totale_livree += charge_livree  # Cumuler la charge livrée
        charge_actuelle -= charge_livree  # Retirer la charge livrée
        villes_non_visitees.remove(meilleure_ville)  # Marquer la ville comme visitée
        ville_actuelle = meilleure_ville  # Mettre à jour la position actuelle

    # Étape finale : Retour obligatoire au dépôt
    # Si on n'est pas déjà au dépôt, calculer et ajouter la consommation du retour
    if ville_actuelle != 0:
        distance_retour = scenario['distances_reelles'][ville_actuelle][0]
        consommation_retour = consommation_carburant(distance_retour, charge_actuelle)
        consommation_totale += consommation_retour  # Ajouter cette consommation au total

    # Retourner les résultats de l'algorithme optimisé
    return ordre_villes, consommation_totale, nb_livraisons, charge_totale_livree


# =============================================================================
# SECTION DE TEST ET D'ANALYSE DE PERFORMANCE
# =============================================================================

# --- Test automatique pour plusieurs valeurs de N ---
N_values = [5, 10, 15, 20, 25]  # Différentes tailles de problèmes à tester
consommations_totales = []  # Liste pour stocker les consommations
livraisons_totales = []  # Liste pour stocker les nombres de livraisons
charges_livrees_totales = []  # Liste pour stocker les charges totales livrées
efficacites = []  # Liste pour stocker les efficacités (charge/carburant)

print("=== RÉSULTATS DE L'ALGORITHME TSP OPTIMISÉ POUR LIVRAISON ===")
print("Format: N=villes, Carburant=L, Livraisons=nb, Charge=kg, Efficacité=kg/L, Ordre=itinéraire")
print()

# --- Test automatique pour plusieurs valeurs de N ---
N_values = [5, 10, 15, 20, 25]  # Différentes tailles de problèmes à tester
consommations_totales = []  # Liste pour stocker les consommations
livraisons_totales = []  # Liste pour stocker les nombres de livraisons
charges_livrees_totales = []  # Liste pour stocker les charges totales livrées
efficacites = []  # Liste pour stocker les efficacités (charge/carburant)

print("=== RÉSULTATS DE L'ALGORITHME TSP OPTIMISÉ POUR LIVRAISON ===")
print("Format: N=villes, Carburant=L, Livraisons=nb, Charge=kg, Efficacité=kg/L, Ordre=itinéraire")
print()

# Boucle de test pour chaque taille de problème
for N in N_values:
    # Générer un scénario aléatoire avec N villes
    scenario = generer_scenario(N)
    
    # Résoudre le problème TSP avec notre algorithme optimisé
    ordre_villes, consommation_totale, nb_livraisons, charge_totale_livree = tsp_livraison_optimise(scenario)
    
    # Calculer l'efficacité (charge livrée par litre de carburant)
    efficacite = charge_totale_livree / consommation_totale if consommation_totale > 0 else 0
    
    # Stocker les résultats pour les graphiques
    consommations_totales.append(consommation_totale)
    livraisons_totales.append(nb_livraisons)
    charges_livrees_totales.append(charge_totale_livree)
    efficacites.append(efficacite)
    
    # Afficher les résultats pour cette taille de problème
    print(f"N={N}, Carburant={consommation_totale:.1f}L, Livraisons={nb_livraisons}, "
          f"Charge={charge_totale_livree}kg, Efficacité={efficacite:.2f}kg/L, Ordre={ordre_villes}")

# Analyse détaillée des performances et optimisation
print("\n=== ANALYSE DE L'OPTIMISATION BI-OBJECTIF ===")
for i, N in enumerate(N_values):
    # Calculer les métriques d'optimisation
    nb_villes_disponibles = N - 1  # Exclut le dépôt
    taux_livraison = (livraisons_totales[i] / nb_villes_disponibles) * 100
    
    # Charge maximale théoriquement livrable
    charge_max_theorique = nb_villes_disponibles * 50  # 50kg par ville
    taux_charge = (charges_livrees_totales[i] / charge_max_theorique) * 100
    
    print(f"N={N}: Livraisons={taux_livraison:.1f}%, Charge={taux_charge:.1f}%, "
          f"Consommation={consommations_totales[i]:.1f}L")

# =============================================================================
# SECTION DE VISUALISATION GRAPHIQUE
# =============================================================================

# --- Tracé graphique des résultats ---
# Créer une figure avec 3 sous-graphiques pour analyser l'optimisation
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# Graphique 1: Consommation de carburant vs Nombre de livraisons
ax1.set_xlabel("Nombre de villes (N)")
ax1.set_ylabel("Consommation (L)", color='tab:blue')
ax1.plot(N_values, consommations_totales, 'o-', color='tab:blue', label='Consommation carburant')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax1_twin = ax1.twinx()
ax1_twin.set_ylabel("Nombre de livraisons", color='tab:orange')
ax1_twin.plot(N_values, livraisons_totales, 's--', color='tab:orange', label='Livraisons effectuées')
ax1_twin.tick_params(axis='y', labelcolor='tab:orange')

ax1.set_title("Objectif 1: Minimiser la consommation vs Objectif 2: Maximiser les livraisons")
ax1.grid(True, alpha=0.3)

# Graphique 2: Charge totale livrée
ax2.set_xlabel("Nombre de villes (N)")
ax2.set_ylabel("Charge livrée (kg)", color='tab:green')
ax2.plot(N_values, charges_livrees_totales, '^-', color='tab:green', label='Charge totale livrée')
ax2.tick_params(axis='y', labelcolor='tab:green')
ax2.set_title("Charge totale livrée par scénario")
ax2.grid(True, alpha=0.3)

# Graphique 3: Efficacité globale (kg de charge par litre de carburant)
ax3.set_xlabel("Nombre de villes (N)")
ax3.set_ylabel("Efficacité (kg/L)", color='tab:red')
ax3.plot(N_values, efficacites, 'd-', color='tab:red', label='Efficacité charge/carburant')
ax3.tick_params(axis='y', labelcolor='tab:red')
ax3.set_title("Efficacité globale de la tournée (kg de charge livrée par litre de carburant)")
ax3.grid(True, alpha=0.3)

# Ajuster automatiquement l'espacement entre les graphiques
fig.tight_layout()

# Afficher les graphiques
plt.show()
