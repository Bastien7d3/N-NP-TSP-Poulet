"""
Package TSP Livraison - Solveur de problème du voyageur de commerce avec contraintes.

Ce package contient les modules principaux pour résoudre des problèmes TSP
adaptés aux livraisons avec contraintes de carburant et de capacité.

Modules disponibles :
- index : Classes de base (Camion, GrapheLivraison)
- tsp_solver : Algorithmes de résolution (Force brute, Glouton, Génétique)
- analyse_performances : Outils d'analyse et de benchmarking
- algo_scenario : Générateur de scénarios de test

Auteur: Projet TSP Livraison
Date: 2025
"""

__version__ = "1.0.0"
__author__ = "Projet TSP Livraison"

# Imports principaux pour faciliter l'utilisation
from .index import Camion, GrapheLivraison
from .tsp_solver import SolveurTSP

__all__ = ['Camion', 'GrapheLivraison', 'SolveurTSP']