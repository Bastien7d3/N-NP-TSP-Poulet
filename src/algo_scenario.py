"""
Module de génération de scénarios TSP pour livraison.

Ce module fournit des fonctions utilitaires pour générer des problèmes TSP
avec contraintes de capacité et de carburant dans le contexte de livraisons.

Auteur: Projet TSP Livraison
Date: 2025
"""

import random
import numpy as np


def generer_scenario_livraison(n_sites, distance_min=30, distance_max=200):
    """
    Génère un scénario de problème TSP pour la livraison avec contraintes réalistes.
    
    Crée une matrice de distances aléatoires entre sites de livraison, 
    incluant un dépôt central (site 0) et des sites de livraison numérotés.
    
    Args:
        n_sites (int): Nombre total de sites incluant le dépôt
        distance_min (int): Distance minimale entre sites en km
        distance_max (int): Distance maximale entre sites en km
    
    Returns:
        dict: Dictionnaire contenant:
            - 'distances': Matrice symétrique des distances entre sites
            - 'n_sites': Nombre total de sites
            - 'depot': Index du dépôt (toujours 0)
    """
    if n_sites < 2:
        raise ValueError("Il faut au moins 2 sites (dépôt + 1 site de livraison)")
    
    # Initialisation de la matrice de distances (symétrique)
    distances = np.zeros((n_sites, n_sites))
    
    # Génération des distances aléatoires pour la partie supérieure
    for i in range(n_sites):
        for j in range(i + 1, n_sites):
            distance = random.randint(distance_min, distance_max)
            distances[i][j] = distance
            distances[j][i] = distance  # Matrice symétrique
    
    return {
        'distances': distances,
        'n_sites': n_sites,
        'depot': 0
    }


def afficher_scenario(scenario):
    """
    Affiche les informations d'un scénario de manière lisible.
    
    Args:
        scenario (dict): Scénario généré par generer_scenario_livraison()
    """
    print(f"Scénario TSP - {scenario['n_sites']} sites total")
    print(f"Dépôt: Site {scenario['depot']}")
    print(f"Sites de livraison: {list(range(1, scenario['n_sites']))}")
    print(f"Matrice des distances ({scenario['n_sites']}x{scenario['n_sites']}):")
    
    # Affichage formaté de la matrice
    for i in range(scenario['n_sites']):
        row = []
        for j in range(scenario['n_sites']):
            if i == j:
                row.append("   0")
            else:
                row.append(f"{scenario['distances'][i][j]:4.0f}")
        print(f"Site {i}: [" + " ".join(row) + "]")


if __name__ == "__main__":
    """
    Exemple d'utilisation du générateur de scénarios.
    """
    print("=== GÉNÉRATEUR DE SCÉNARIOS TSP LIVRAISON ===\n")
    
    # Génération d'un petit scénario d'exemple
    scenario_test = generer_scenario_livraison(n_sites=5)
    afficher_scenario(scenario_test)
    
    print(f"\nDistances depuis le dépôt:")
    depot = scenario_test['depot']
    for site in range(1, scenario_test['n_sites']):
        distance = scenario_test['distances'][depot][site]
        print(f"  Dépôt → Site {site}: {distance:.0f} km")
