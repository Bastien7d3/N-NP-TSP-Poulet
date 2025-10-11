# Solveur TSP avec Contraintes de Livraison 🚚

**Résolution du problème du voyageur de commerce adapté aux livraisons avec contraintes réalistes**

Ce projet implémente trois algorithmes de résolution pour un problème TSP avec contraintes de carburant, de capacité et de poids variable. L'application simule des livraisons où le camion devient plus léger (et donc plus économe) au fil des livraisons.

## 🎯 **Fonctionnalités Principales**

### **Algorithmes Disponibles**
- **🔬 Force Brute** : Énumération exhaustive garantissant l'optimum (≤ 10 sites)
- **⚡ Glouton** : Heuristique du plus proche voisin (rapide, complexité O(n²))
- **🧬 Génétique** : Métaheuristique évolutionniste (bon compromis qualité/temps)

### **Contraintes Réalistes**
- ✅ Consommation de carburant variable selon le poids du camion
- ✅ Obligation de retour au dépôt avec carburant suffisant
- ✅ Capacité maximale du véhicule
- ✅ Prise en compte des embouteillages

## 🚀 **Installation et Utilisation**

### **Prérequis**
- Python 3.7+
- Dépendances listées dans `requirements.txt`

### **Installation**
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### **Lancement Rapide**
```bash
# Menu interactif avec exemples
python main.py

# Test rapide de validation
python main.py --test

# Aide
python main.py --help

# Lancement direct des exemples
python examples/exemple_utilisation.py
```

## 📚 **Guide d'Utilisation**

### **Exemple Basique**
```python
from src.index import Camion, GrapheLivraison
from src.tsp_solver import SolveurTSP

# Configuration du camion (60T total : 3T vide + 57T charge max)
camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)

# Génération du problème (5 sites, 500kg par livraison)
graphe = GrapheLivraison(n_sites=5, camion=camion, quantite_par_site=500)

# Résolution
solveur = SolveurTSP(graphe)
tournee, cout = solveur.glouton_plus_proche(verbose=True)
print(f"Meilleure tournée : {tournee}")
print(f"Consommation : {cout:.2f}L")
```

## 🏗️ **Architecture du Projet**

```
📁 N-NP-TSP-Poulet/
├── 📄 main.py                     # Point d'entrée principal
├── 📄 requirements.txt            # Dépendances Python
├── 📄 .gitignore                  # Fichiers à ignorer par Git
├── 📄 README.md                   # Documentation principale
├── 📁 src/                        # Code source principal
│   ├── 📄 __init__.py             # Package Python
│   ├── 📄 index.py                # Classes de base (Camion, GrapheLivraison)
│   ├── 📄 tsp_solver.py           # Algorithmes de résolution TSP
│   ├── 📄 analyse_performances.py # Outils d'analyse et benchmarking
│   └── 📄 algo_scenario.py        # Générateur de scénarios de test
├── � examples/                   # Exemples et démonstrations
│   └── �📄 exemple_utilisation.py  # Menu interactif complet
├── � outputs/                    # Fichiers générés (graphiques, rapports)
│   └── 📄 README.md               # Documentation du dossier
└── � docs/                       # Documentation supplémentaire
```

## � **Performances et Complexités**

| Algorithme | Complexité | Usage Recommandé |
|------------|------------|------------------|
| **Force Brute** | O(n!) | n ≤ 10 sites |
| **Glouton** | O(n²) | Toutes tailles |
| **Génétique** | O(pop×gen×n²) | n > 10 sites |

## 🏆 **Résultats Remarquables**

### **Fiabilité de l'Algorithme Génétique**
- ✅ **100% de solutions valides** générées (population initiale intelligente)
- ✅ **Égale l'optimum** sur problèmes ≤ 10 sites  
- ✅ **+14% d'amélioration** vs glouton sur 25 sites
- ✅ **Temps raisonnable** : 6s pour 25 sites, 50 générations

### **Innovations Techniques**
- **Initialisation hybride** : 40% variations glouton + 30% proches d'abord + 30% aléatoire
- **Mutations intelligentes** : échange, inversion, déplacement
- **Amélioration locale** : 2-opt sur 10% des enfants
- **Élitisme adaptatif** : conservation des meilleures solutions

---

*Développé dans le cadre d'un projet d'optimisation combinatoire*