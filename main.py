#!/usr/bin/env python3
"""
Point d'entrée principal du projet TSP Livraison.

Ce script lance le menu interactif avec les exemples d'utilisation.
Il peut aussi être utilisé pour des tests rapides des algorithmes.

Usage:
    python main.py                    # Lance le menu interactif
    python main.py --test             # Lance un test rapide
    python main.py --help             # Affiche l'aide
"""

import sys
import os

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_rapide():
    """Lance un test rapide pour vérifier que tout fonctionne."""
    try:
        from src.index import Camion, GrapheLivraison
        from src.tsp_solver import SolveurTSP
        
        print("🧪 Test rapide du solveur TSP...")
        
        # Configuration test
        camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)
        graphe = GrapheLivraison(n_sites=5, camion=camion, quantite_par_site=500, seed=42)
        solveur = SolveurTSP(graphe)
        
        # Test glouton
        tournee, cout = solveur.glouton_plus_proche(verbose=False)
        print(f"✅ Algorithme glouton : {cout:.1f}L pour {graphe.n_sites} sites")
        
        # Test génétique (rapide)
        tournee_gen, cout_gen, _ = solveur.algorithme_genetique(
            taille_population=20, nb_generations=10, verbose=False
        )
        print(f"✅ Algorithme génétique : {cout_gen:.1f}L")
        
        print("🎉 Tous les tests sont passés avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

def lancer_menu():
    """Lance le menu interactif complet."""
    try:
        # Import et lancement du menu
        from examples.exemple_utilisation import menu_principal
        menu_principal()
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("Vérifiez que tous les fichiers sont présents dans les bons dossiers.")
    except Exception as e:
        print(f"❌ Erreur lors du lancement du menu : {e}")

def afficher_aide():
    """Affiche l'aide d'utilisation."""
    print("""
🚚 Solveur TSP avec Contraintes de Livraison

Usage:
    python main.py                    # Lance le menu interactif complet
    python main.py --test             # Lance un test rapide de validation
    python main.py --help             # Affiche cette aide

Description:
    Ce projet résout le problème du voyageur de commerce (TSP) adapté aux
    livraisons avec contraintes de carburant, de capacité et de poids variable.

Algorithmes disponibles:
    • Force Brute : Optimal (≤ 10 sites)
    • Glouton : Rapide (toutes tailles)
    • Génétique : Bon compromis qualité/temps

Pour plus d'informations, consultez le README.md
    """)

def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help']:
            afficher_aide()
        elif arg in ['--test', '-t', 'test']:
            success = test_rapide()
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Argument inconnu : {arg}")
            print("Utilisez --help pour voir les options disponibles.")
            sys.exit(1)
    else:
        # Lancement du menu par défaut
        lancer_menu()

if __name__ == "__main__":
    main()