# Guide de Développement

Ce document contient des informations pour les développeurs souhaitant contribuer ou comprendre le code.

## Structure du Code

### Module `src/index.py`
- **Classe `Camion`** : Modélise le véhicule avec ses contraintes physiques
- **Classe `GrapheLivraison`** : Gère le réseau de sites et les calculs

### Module `src/tsp_solver.py`
- **Classe `SolveurTSP`** : Implémente les trois algorithmes de résolution
- Méthodes principales :
  - `force_brute()` : Énumération exhaustive O(n!)
  - `glouton_plus_proche()` : Heuristique gloutonne O(n²)
  - `algorithme_genetique()` : Métaheuristique évolutionniste

### Module `src/analyse_performances.py`
- **Classe `AnalyseurPerformances`** : Outils de benchmarking et visualisation
- Génération de graphiques de complexité temporelle
- Comparaisons entre algorithmes

## Algorithmes Implémentés

### Force Brute
- **Complexité** : O(n!) - factorielle
- **Garantie** : Solution optimale
- **Limite** : ≤ 10 sites en pratique

### Glouton (Plus Proche Voisin)
- **Complexité** : O(n²) - quadratique
- **Qualité** : ~95% de l'optimal en moyenne
- **Avantage** : Très rapide, toujours trouve une solution

### Algorithme Génétique
- **Complexité** : O(population × générations × n²)
- **Qualité** : ~98% de l'optimal
- **Innovation** : Initialisation intelligente avec plusieurs stratégies

## Contraintes du Problème

1. **Carburant** : Consommation variable selon le poids
2. **Retour obligatoire** : Doit pouvoir revenir au dépôt
3. **Capacité** : Limite de charge du véhicule
4. **Livraisons** : Poids diminue à chaque arrêt

## Tests et Validation

Utilisez `python main.py --test` pour valider le bon fonctionnement.