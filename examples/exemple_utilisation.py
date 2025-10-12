"""
Exemples d'utilisation du solveur TSP pour le problème de livraison.

Ce fichier contient plusieurs exemples progressifs montrant comment :
1. Résoudre un petit problème avec toutes les méthodes
2. Comparer les performances
3. Analyser la complexité
4. Utiliser sur de grandes instances

Lancement :
    python examples/exemple_utilisation.py
    ou
    python main.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Création du dossier outputs s'il n'existe pas
outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
os.makedirs(outputs_dir, exist_ok=True)

from index import Camion, GrapheLivraison
from tsp_solver import SolveurTSP
from analyse_performances import AnalyseurPerformances
import numpy as np
import math


def exemple_1_petit_probleme():
    """
    EXEMPLE 1 : Petit problème (5 sites) - Test de toutes les méthodes
    
    Montre comment utiliser les 3 algorithmes et comparer les résultats.
    """
    print("\n" + "="*80)
    print("EXEMPLE 1 : Petit problème avec 5 sites")
    print("="*80)
    
    # Créer l'environnement - Configuration camion 60T (3T vide + 57T charge)
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # 60T total, 1000L réservoir
    graphe = GrapheLivraison(
        n_sites=5,
        camion=camion,
        quantite_par_site=500,  # 500kg max comme demandé
        seed=42
    )
    
    print(f"\nProblème créé: {graphe.n_sites} sites à livrer")
    print(f"Camion: {camion}")
    
    # Créer le solveur
    solveur = SolveurTSP(graphe)
    
    # Méthode 1 : Glouton (rapide)
    print("\n" + "─"*80)
    print(">> METHODE GLOUTON (HEURISTIQUE)")
    print("─"*80)
    tournee_glouton, cout_glouton = solveur.glouton_plus_proche(verbose=True)
    
    # Méthode 2 : Force brute (optimal mais lent)
    print("\n" + "─"*80)
    print(">> METHODE FORCE BRUTE (OPTIMAL)")
    print("─"*80)
    tournee_optimal, cout_optimal = solveur.force_brute(verbose=True)
    
    # Méthode 3 : Algorithme génétique (métaheuristique)
    print("\n" + "─"*80)
    print(">> METHODE GENETIQUE (METAHEURISTIQUE)")
    print("─"*80)
    tournee_genetique, cout_genetique, historique = solveur.algorithme_genetique(
        taille_population=30,
        nb_generations=50,
        taux_mutation=0.15,
        taux_elitisme=0.2,
        verbose=True
    )
    
    # Résumé des résultats
    print("\n" + "="*80)
    print("RÉSUMÉ DES RÉSULTATS")
    print("="*80)
    print(f"Glouton:    {cout_glouton:.2f}L  ({(cout_glouton/cout_optimal-1)*100:+.1f}% vs optimal)")
    print(f"Génétique:  {cout_genetique:.2f}L  ({(cout_genetique/cout_optimal-1)*100:+.1f}% vs optimal)")
    print(f"Optimal:    {cout_optimal:.2f}L  (référence)")
    print("="*80)
    
    # Visualiser la meilleure solution
    print("\n📊 Visualisation de la solution optimale...")
    graphe.visualiser(tournee=tournee_optimal)


def exemple_2_analyse_complexite():
    """
    EXEMPLE 2 : Analyse de complexité
    
    Mesure le temps d'exécution en fonction de la taille du problème
    et génère des graphiques.
    """
    print("\n" + "="*80)
    print("EXEMPLE 2 : Analyse de complexité temporelle")
    print("="*80)
    
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # Configuration 60T (3T+57T)
    analyseur = AnalyseurPerformances()
    
    # Analyser force brute (petites tailles seulement)
    print("\n📊 Analyse FORCE BRUTE (petites instances)...")
    analyseur.analyser_complexite_algorithme(
        methode='force_brute',
        tailles=[3, 4, 5, 6, 7, 8, 9],  # Limité à 9 sites (optimal temps/démonstration)
        camion=camion,
        repetitions=2  # 2 répétitions suffisent pour les gros calculs
    )
    
    # Analyser glouton (peut gérer de grandes tailles)
    print("\n📊 Analyse GLOUTON (toutes tailles)...")
    analyseur.analyser_complexite_algorithme(
        methode='glouton',
        tailles=[3, 5, 8, 10, 12, 15, 18, 20, 25],  # Limité à 25 sites
        camion=camion,
        repetitions=5  # Plus de répétitions pour capturer les petits temps
    )
    
    # Analyser génétique
    print("\n📊 Analyse GÉNÉTIQUE (tailles moyennes)...")
    analyseur.analyser_complexite_algorithme(
        methode='genetique',
        tailles=[3, 5, 8, 10, 12, 15, 18, 20, 25],  # Limité à 25 sites
        camion=camion,
        repetitions=2
    )
    
    # Tracer les courbes de complexité
    print("\n📈 Génération des graphiques...")
    
    # Graphique de complexité temporelle
    output_path_temps = os.path.join(outputs_dir, 'complexite_temporelle.png')
    analyseur.tracer_complexite_temporelle(sauvegarder=output_path_temps)
    
    # Graphique d'évolution des coûts
    output_path_cout = os.path.join(outputs_dir, 'evolution_cout_carburant.png')
    analyseur.tracer_evolution_cout(sauvegarder=output_path_cout)


def exemple_3_rapport_comparatif():
    """
    EXEMPLE 3 : Rapport comparatif détaillé
    
    Compare toutes les méthodes sur une instance donnée avec
    calcul d'indicateurs de performance.
    """
    print("\n" + "="*80)
    print("EXEMPLE 3 : Rapport comparatif complet")
    print("="*80)
    
    # Créer un problème de taille moyenne avec config 60T (3T+57T)
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # 60T total
    graphe = GrapheLivraison(
        n_sites=7,
        camion=camion,
        quantite_par_site=500,  # 7 × 500kg = 3500kg < 57000kg max
        seed=123
    )
    
    # Générer le rapport
    analyseur = AnalyseurPerformances()
    resultats = analyseur.rapport_comparatif(graphe, verbose=True)
    
    # Visualiser la meilleure solution trouvée
    if resultats['optimal']:
        print("\n📊 Visualisation de la solution optimale...")
        graphe.visualiser(tournee=resultats['optimal']['tournee'])
    else:
        print("\n📊 Visualisation de la solution génétique...")
        graphe.visualiser(tournee=resultats['genetique']['tournee'])


def exemple_4_grand_probleme():
    """
    EXEMPLE 4 : Grand problème (métaheuristiques uniquement)
    
    Montre comment traiter un problème de grande taille où seules
    les métaheuristiques sont utilisables.
    """
    print("\n" + "="*80)
    print("EXEMPLE 4 : Grand problème (25 sites)")
    print("="*80)
    
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # Configuration 60T (3T+57T)
    graphe = GrapheLivraison(
        n_sites=25,
        camion=camion,
        quantite_par_site=400,  # 25 × 400kg = 10000kg < 57000kg max
        seed=456
    )
    
    print(f"\n⚠️  Avec 25 sites, force brute = {math.factorial(25):,} permutations")
    print("    -> IMPOSSIBLE à calculer !")
    print("\n🚀 Comparaison glouton vs génétique...\n")
    
    solveur = SolveurTSP(graphe)
    
    # Glouton
    import time
    print("1. Algorithme GLOUTON...")
    debut = time.time()
    tournee_g, cout_g = solveur.glouton_plus_proche(verbose=False)
    temps_g = time.time() - debut
    print(f"   Coût: {cout_g:.2f}L")
    print(f"   Temps: {temps_g:.3f}s")
    
    # Génétique
    print("\n2. Algorithme GÉNÉTIQUE...")
    debut = time.time()
    tournee_gen, cout_gen, hist = solveur.algorithme_genetique(
        taille_population=100,
        nb_generations=200,
        taux_mutation=0.2,
        taux_elitisme=0.1,
        verbose=False
    )
    temps_gen = time.time() - debut
    print(f"   Coût: {cout_gen:.2f}L")
    print(f"   Temps: {temps_gen:.3f}s")
    
    # Comparaison
    print("\n" + "─"*80)
    print("📊 RÉSULTATS:")
    print("─"*80)
    print(f"Glouton:    {cout_g:.2f}L (temps: {temps_g:.3f}s)")
    print(f"Génétique:  {cout_gen:.2f}L (temps: {temps_gen:.3f}s)")
    amelioration = (cout_g - cout_gen) / cout_g * 100
    print(f"\nAmélioration génétique vs glouton: {amelioration:.1f}%")
    print("─"*80)
    
    # Visualiser l'évolution du génétique
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.plot(hist, linewidth=2, color='blue')
    plt.xlabel('Génération', fontsize=12)
    plt.ylabel('Meilleur coût (L)', fontsize=12)
    plt.title('Évolution de l\'algorithme génétique', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # Chemin absolu pour la sauvegarde
    evolution_path = os.path.join(outputs_dir, 'evolution_genetique.png')
    plt.savefig(evolution_path, dpi=300)
    print(f"\n✅ Graphique sauvegardé : {os.path.relpath(evolution_path)}")
    plt.show()
    
    # Visualiser la meilleure solution
    print("\n📊 Visualisation de la meilleure solution (génétique)...")
    graphe.visualiser(tournee=tournee_gen)


def exemple_5_graphe_personnalise():
    """
    EXEMPLE 5 : Import d'un graphe personnalisé
    
    Montre comment utiliser une matrice de distances personnalisée
    (par exemple issue de données GPS réelles).
    """
    print("\n" + "="*80)
    print("EXEMPLE 5 : Graphe personnalisé (matrice importée)")
    print("="*80)
    
    # Matrice de distances custom (par exemple, issue de données GPS)
    matrice_custom = np.array([
        [0,   45,  80,  120, 75],   # Dépôt → Sites
        [45,  0,   50,  90,  60],   # Site 1 → Sites
        [80,  50,  0,   70,  40],   # Site 2 → Sites
        [120, 90,  70,  0,   55],   # Site 3 → Sites
        [75,  60,  40,  55,  0]     # Site 4 → Sites
    ])
    
    print("\nMatrice de distances importée:")
    print(matrice_custom)
    print(f"\nNombre de sites: {matrice_custom.shape[0] - 1}")
    
    # Positions optionnelles pour visualisation
    positions_custom = np.array([
        [0, 0],      # Dépôt au centre
        [45, 0],     # Site 1 à l'est
        [0, 80],     # Site 2 au nord
        [-90, -40],  # Site 3 au sud-ouest
        [60, 60]     # Site 4 au nord-est
    ])
    
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # Configuration 60T (3T+57T)
    
    # Créer le graphe avec la matrice personnalisée
    graphe_custom = GrapheLivraison(
        matrice_distances=matrice_custom,
        positions=positions_custom,
        camion=camion,
        quantite_par_site=500,  # 500kg max
        seed=789
    )
    
    print("\n✅ Graphe créé avec succès!")
    
    # Résoudre avec les différentes méthodes
    solveur_custom = SolveurTSP(graphe_custom)
    
    print("\n1. Glouton:")
    tournee_g, cout_g = solveur_custom.glouton_plus_proche(verbose=False)
    print(f"   Coût: {cout_g:.2f}L")
    
    print("\n2. Génétique:")
    tournee_gen, cout_gen, _ = solveur_custom.algorithme_genetique(
        taille_population=40,
        nb_generations=80,
        verbose=False
    )
    print(f"   Coût: {cout_gen:.2f}L")
    
    print("\n3. Force brute (optimal):")
    tournee_opt, cout_opt = solveur_custom.force_brute(verbose=False)
    print(f"   Coût: {cout_opt:.2f}L")
    
    # Comparaison
    print("\n" + "─"*80)
    print("📊 COMPARAISON:")
    print("─"*80)
    print(f"Glouton:   {cout_g:.2f}L ({(cout_g/cout_opt - 1)*100:+.1f}%)")
    print(f"Génétique: {cout_gen:.2f}L ({(cout_gen/cout_opt - 1)*100:+.1f}%)")
    print(f"Optimal:   {cout_opt:.2f}L (référence)")
    print("─"*80)
    
    # Visualiser
    print("\n📊 Visualisation du graphe personnalisé...")
    graphe_custom.visualiser(tournee=tournee_opt)


def exemple_6_tester_tournee_manuelle():
    """
    EXEMPLE 6 : Tester une tournée proposée manuellement
    
    Montre comment évaluer une tournée spécifique et la comparer
    aux solutions automatiques.
    """
    print("\n" + "="*80)
    print("EXEMPLE 6 : Test d'une tournée manuelle")
    print("="*80)
    
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # Configuration 60T (3T+57T)
    graphe = GrapheLivraison(
        n_sites=5,
        camion=camion,
        quantite_par_site=500,  # 500kg max
        seed=42
    )
    
    # Proposer une tournée manuellement
    ma_tournee = [0, 3, 1, 5, 2, 4, 0]
    
    print(f"\nTournée proposée: {' -> '.join([f'Site {s}' if s != 0 else 'Dépôt' for s in ma_tournee])}")
    
    # Tester la tournée
    solveur = SolveurTSP(graphe)
    cout, valide, msg = solveur.calculer_cout_tournee(ma_tournee, verbose=True)
    
    if valide:
        print(f"\n✅ Tournée VALIDE")
        print(f"Coût: {cout:.2f}L")
        
        # Comparer avec l'optimal
        _, cout_optimal = solveur.force_brute(verbose=False)
        
        if cout == cout_optimal:
            print("\n🏆 C'est la solution OPTIMALE !")
        else:
            ecart = cout - cout_optimal
            ecart_pct = (ecart / cout_optimal) * 100
            print(f"\n📊 Écart avec l'optimal:")
            print(f"   +{ecart:.2f}L (+{ecart_pct:.1f}%)")
        
        # Visualiser
        graphe.visualiser(tournee=ma_tournee)
    else:
        print(f"\n❌ Tournée INVALIDE")
        print(f"Raison: {msg}")


# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def menu_principal():
    """
    Menu interactif pour choisir quel exemple lancer.
    """
    print("\n" + "#"*80)
    print(" "*20 + "EXEMPLES D'UTILISATION DU SOLVEUR TSP")
    print("#"*80)
    
    print("\nChoisissez un exemple à exécuter:\n")
    print("  1. Petit problème (5 sites) - Toutes les méthodes")
    print("  2. Analyse de complexité temporelle")
    print("  3. Rapport comparatif détaillé")
    print("  4. Grand problème (25 sites)")
    print("  5. Import de graphe personnalisé")
    print("  6. Tester une tournée manuelle")
    print("  7. Lancer TOUS les exemples")
    print("  0. Quitter")
    
    while True:
        try:
            choix = input("\nVotre choix (0-7): ").strip()
            
            if choix == '0':
                print("\nAu revoir! 👋")
                break
            elif choix == '1':
                exemple_1_petit_probleme()
            elif choix == '2':
                exemple_2_analyse_complexite()
            elif choix == '3':
                exemple_3_rapport_comparatif()
            elif choix == '4':
                exemple_4_grand_probleme()
            elif choix == '5':
                exemple_5_graphe_personnalise()
            elif choix == '6':
                exemple_6_tester_tournee_manuelle()
            elif choix == '7':
                print("\n🚀 Lancement de tous les exemples...\n")
                exemple_1_petit_probleme()
                exemple_2_analyse_complexite()
                exemple_3_rapport_comparatif()
                exemple_4_grand_probleme()
                exemple_5_graphe_personnalise()
                exemple_6_tester_tournee_manuelle()
                print("\n✅ Tous les exemples terminés!")
                break
            else:
                print("❌ Choix invalide. Veuillez entrer un nombre entre 0 et 7.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interruption utilisateur. Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            print("Veuillez réessayer.")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    menu_principal()