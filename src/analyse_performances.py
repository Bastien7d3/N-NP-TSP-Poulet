"""
Module d'analyse de performances pour les algorithmes TSP.

Ce module fournit des outils d'évaluation et de comparaison :
1. Mesure de la complexité temporelle  
2. Génération de graphiques de performances
3. Calcul d'indicateurs de qualité des solutions
4. Comparaisons multi-algorithmes

Auteur: Projet TSP Livraison
Date: 2025
"""

import time
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Callable


class AnalyseurPerformances:
    """
    Analyse les performances des algorithmes de résolution.
    
    Permet de :
    - Mesurer le temps d'exécution en fonction de n
    - Tracer la complexité temporelle
    - Comparer différents algorithmes
    - Calculer des indicateurs de qualité
    """
    
    def __init__(self):
        """Initialise l'analyseur avec des structures pour stocker les résultats."""
        self.resultats = {
            'force_brute': {'n': [], 'temps': [], 'couts': []},
            'glouton': {'n': [], 'temps': [], 'couts': []},
            'genetique': {'n': [], 'temps': [], 'couts': []}
        }
    
    
    def mesurer_temps_execution(self, fonction: Callable, *args, **kwargs) -> Tuple[float, any]:
        """
        Mesure le temps d'exécution d'une fonction.
        
        Args:
            fonction: Fonction à mesurer
            *args, **kwargs: Arguments de la fonction
        
        Returns:
            Tuple (temps_execution_secondes, resultat_fonction)
        """
        debut = time.time()
        resultat = fonction(*args, **kwargs)
        fin = time.time()
        temps = fin - debut
        return temps, resultat
    
    
    def analyser_complexite_algorithme(self, 
                                       methode: str,
                                       tailles: List[int],
                                       camion,
                                       repetitions: int = 3,
                                       verbose: bool = True):
        """
        Analyse la complexité temporelle d'un algorithme pour différentes tailles.
        
        Cette fonction :
        1. Crée des graphes de différentes tailles (n sites)
        2. Exécute l'algorithme sur chaque graphe
        3. Mesure le temps d'exécution
        4. Répète plusieurs fois pour avoir une moyenne fiable
        
        Args:
            methode: 'force_brute', 'glouton' ou 'genetique'
            tailles: Liste des tailles à tester (ex: [3, 4, 5, 6, 7])
            camion: Instance de Camion à utiliser
            repetitions: Nombre de répétitions par taille (pour moyenner)
            verbose: Afficher la progression
        """
        from index import GrapheLivraison
        from tsp_solver import SolveurTSP
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"ANALYSE DE COMPLEXITÉ : {methode.upper()}")
            print(f"{'='*70}")
            print(f"Tailles testées: {tailles}")
            print(f"Répétitions par taille: {repetitions}\n")
        
        for n in tailles:
            if methode == 'force_brute' and n > 10:
                if verbose:
                    print(f"⚠️  Taille n={n} trop grande pour force brute, ignorée")
                continue
            
            temps_liste = []
            couts_liste = []
            
            if verbose:
                print(f"Test avec n={n} sites...", end=' ')
            
            # Répéter plusieurs fois pour avoir une moyenne
            for rep in range(repetitions):
                # Créer un graphe aléatoire
                graphe = GrapheLivraison(
                    n_sites=n,
                    camion=camion,
                    quantite_par_site=500,  # 500kg max comme demandé
                    seed=42 + rep  # Seed différent à chaque répétition
                )
                
                solveur = SolveurTSP(graphe)
                
                # Mesurer le temps
                if methode == 'force_brute':
                    temps, (tournee, cout) = self.mesurer_temps_execution(
                        solveur.force_brute, verbose=False
                    )
                elif methode == 'glouton':
                    temps, (tournee, cout) = self.mesurer_temps_execution(
                        solveur.glouton_plus_proche, verbose=False
                    )
                elif methode == 'genetique':
                    temps, (tournee, cout, hist) = self.mesurer_temps_execution(
                        solveur.algorithme_genetique, 
                        taille_population=50,
                        nb_generations=100,
                        verbose=False
                    )
                else:
                    raise ValueError(f"Méthode inconnue: {methode}")
                
                temps_liste.append(temps)
                couts_liste.append(cout)
            
            # Calculer les moyennes
            temps_moyen = np.mean(temps_liste)
            cout_moyen = np.mean(couts_liste)
            
            # Stocker les résultats
            self.resultats[methode]['n'].append(n)
            self.resultats[methode]['temps'].append(temps_moyen)
            self.resultats[methode]['couts'].append(cout_moyen)
            
            if verbose:
                print(f"Temps moyen: {temps_moyen:.4f}s (coût: {cout_moyen:.2f}L)")
        
        if verbose:
            print(f"\n{'='*70}\n")
    
    
    def tracer_complexite_temporelle(self, sauvegarder: str = None):
        """
        Trace la complexité temporelle des algorithmes testés.
        
        Crée un graphique montrant :
        - Temps d'exécution en fonction de n (échelle log)
        - Courbes théoriques de référence (n², n!, etc.)
        
        Args:
            sauvegarder: Chemin pour sauvegarder le graphique (optionnel)
                        Exemple: 'resultats/complexite.png'
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # ===== GRAPHIQUE 1 : Échelle normale =====
        ax1.set_title('Complexité temporelle (échelle normale)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Nombre de sites (n)', fontsize=12)
        ax1.set_ylabel('Temps d\'exécution (secondes)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Tracer les résultats
        for methode, data in self.resultats.items():
            if len(data['n']) > 0:
                label = methode.replace('_', ' ').title()
                ax1.plot(data['n'], data['temps'], 'o-', linewidth=2, 
                        markersize=8, label=label)
        
        ax1.legend(fontsize=11)
        
        # ===== GRAPHIQUE 2 : Échelle logarithmique =====
        ax2.set_title('Complexité temporelle (échelle log)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Nombre de sites (n)', fontsize=12)
        ax2.set_ylabel('Temps d\'exécution (secondes, log)', fontsize=12)
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3, which='both')
        
        # Tracer les résultats
        for methode, data in self.resultats.items():
            if len(data['n']) > 0:
                label = methode.replace('_', ' ').title()
                ax2.plot(data['n'], data['temps'], 'o-', linewidth=2, 
                        markersize=8, label=label)
        
        # Ajouter des courbes théoriques de référence
        if len(self.resultats['force_brute']['n']) > 0:
            n_max = max(self.resultats['force_brute']['n'])
            n_ref = np.arange(1, n_max + 1)
            
            # Calibrer sur le premier point
            t_ref = self.resultats['force_brute']['temps'][0]
            n_ref_val = self.resultats['force_brute']['n'][0]
            
            # O(n!)
            factorielle = np.array([math.factorial(n) for n in n_ref])
            factorielle_normalisee = t_ref * (factorielle / math.factorial(n_ref_val))
            ax2.plot(n_ref, factorielle_normalisee, '--', alpha=0.5, 
                    label='O(n!) théorique', color='red')
        
        if len(self.resultats['glouton']['n']) > 0:
            n_max = max(self.resultats['glouton']['n'])
            n_ref = np.arange(1, n_max + 1)
            
            # Calibrer sur le premier point
            t_ref = self.resultats['glouton']['temps'][0]
            n_ref_val = self.resultats['glouton']['n'][0]
            
            # O(n²)
            quadratique = n_ref ** 2
            quadratique_normalise = t_ref * (quadratique / (n_ref_val ** 2))
            ax2.plot(n_ref, quadratique_normalise, '--', alpha=0.5, 
                    label='O(n²) théorique', color='green')
        
        ax2.legend(fontsize=11)
        
        plt.tight_layout()
        
        if sauvegarder:
            plt.savefig(sauvegarder, dpi=300, bbox_inches='tight')
            print(f"✅ Graphique sauvegardé : {sauvegarder}")
        
        plt.show()
    
    
    def calculer_indicateurs_qualite(self, cout_obtenu: float, 
                                     cout_optimal: float = None,
                                     cout_aleatoire: float = None) -> Dict[str, float]:
        """
        Calcule des indicateurs de qualité de la solution.
        
        Plusieurs indicateurs possibles :
        1. Gap optimality : écart avec l'optimal (si connu)
        2. Amélioration vs aléatoire : combien on fait mieux qu'une solution random
        3. Ratio de performance : cout_obtenu / cout_optimal
        
        Args:
            cout_obtenu: Coût de la solution trouvée
            cout_optimal: Coût de la solution optimale (si connu)
            cout_aleatoire: Coût d'une solution aléatoire moyenne
        
        Returns:
            Dictionnaire avec les indicateurs calculés
        """
        indicateurs = {'cout_obtenu': cout_obtenu}
        
        if cout_optimal is not None and cout_optimal > 0:
            # Gap d'optimalité (en %)
            gap = ((cout_obtenu - cout_optimal) / cout_optimal) * 100
            indicateurs['gap_optimalite_pct'] = gap
            
            # Ratio de performance
            ratio = cout_obtenu / cout_optimal
            indicateurs['ratio_performance'] = ratio
            
            # Qualité (100% = optimal, 0% = très mauvais)
            qualite = max(0, 100 - gap)
            indicateurs['qualite_pct'] = qualite
        
        if cout_aleatoire is not None and cout_aleatoire > 0:
            # Amélioration par rapport au random (en %)
            amelioration = ((cout_aleatoire - cout_obtenu) / cout_aleatoire) * 100
            indicateurs['amelioration_vs_random_pct'] = amelioration
        
        return indicateurs
    
    
    def generer_solution_aleatoire(self, graphe) -> Tuple[List[int], float]:
        """
        Génère une solution aléatoire valide pour comparaison.
        
        Utile pour avoir une baseline : "au pire, on fait au moins mieux
        qu'une solution tirée au hasard"
        
        Args:
            graphe: Instance de GrapheLivraison
        
        Returns:
            Tuple (tournee, cout)
        """
        from tsp_solver import SolveurTSP
        
        sites = list(range(1, graphe.n_total))
        np.random.shuffle(sites)
        tournee = [0] + sites + [0]
        
        solveur = SolveurTSP(graphe)
        cout, valide, _ = solveur.calculer_cout_tournee(tournee, verbose=False)
        
        # Si la tournée aléatoire n'est pas valide, en générer une autre
        tentatives = 0
        while not valide and tentatives < 100:
            np.random.shuffle(sites)
            tournee = [0] + sites + [0]
            cout, valide, _ = solveur.calculer_cout_tournee(tournee, verbose=False)
            tentatives += 1
        
        return tournee, cout
    
    
    def rapport_comparatif(self, graphe, verbose: bool = True):
        """
        Génère un rapport comparatif complet des différentes méthodes.
        
        Compare :
        - Force brute (si possible)
        - Glouton
        - Génétique
        - Solution aléatoire (baseline)
        
        Calcule les indicateurs de performance pour chaque méthode.
        
        Args:
            graphe: Instance de GrapheLivraison à résoudre
            verbose: Afficher les détails
        
        Returns:
            Dictionnaire avec les résultats de chaque méthode
        """
        from tsp_solver import SolveurTSP
        
        print(f"\n{'#'*70}")
        print(f"RAPPORT COMPARATIF DE PERFORMANCES")
        print(f"{'#'*70}")
        print(f"Problème: {graphe.n_sites} sites de livraison\n")
        
        solveur = SolveurTSP(graphe)
        resultats = {}
        
        # Solution aléatoire (baseline)
        print("🎲 Solution ALÉATOIRE (baseline)...")
        temps, (tournee_rand, cout_rand) = self.mesurer_temps_execution(
            self.generer_solution_aleatoire, graphe
        )
        resultats['aleatoire'] = {
            'tournee': tournee_rand,
            'cout': cout_rand,
            'temps': temps
        }
        if verbose:
            print(f"   Coût: {cout_rand:.2f}L")
            print(f"   Temps: {temps:.4f}s\n")
        
        # Glouton
        print("🚀 Algorithme GLOUTON...")
        temps, (tournee_glouton, cout_glouton) = self.mesurer_temps_execution(
            solveur.glouton_plus_proche, verbose=False
        )
        resultats['glouton'] = {
            'tournee': tournee_glouton,
            'cout': cout_glouton,
            'temps': temps
        }
        if verbose:
            print(f"   Coût: {cout_glouton:.2f}L")
            print(f"   Temps: {temps:.4f}s\n")
        
        # Génétique
        print("🧬 Algorithme GÉNÉTIQUE...")
        temps, (tournee_gen, cout_gen, hist) = self.mesurer_temps_execution(
            solveur.algorithme_genetique,
            taille_population=50,
            nb_generations=100,
            verbose=False
        )
        resultats['genetique'] = {
            'tournee': tournee_gen,
            'cout': cout_gen,
            'temps': temps
        }
        if verbose:
            print(f"   Coût: {cout_gen:.2f}L")
            print(f"   Temps: {temps:.4f}s\n")
        
        # Force brute (si possible)
        if graphe.n_sites <= 10:
            print("🔬 FORCE BRUTE (optimal)...")
            temps, (tournee_optimal, cout_optimal) = self.mesurer_temps_execution(
                solveur.force_brute, verbose=False
            )
            resultats['optimal'] = {
                'tournee': tournee_optimal,
                'cout': cout_optimal,
                'temps': temps
            }
            if verbose:
                print(f"   Coût: {cout_optimal:.2f}L")
                print(f"   Temps: {temps:.4f}s\n")
        else:
            resultats['optimal'] = None
            print(f"⚠️  Force brute impossible avec {graphe.n_sites} sites\n")
        
        # Calcul des indicateurs
        print("="*70)
        print("INDICATEURS DE PERFORMANCE")
        print("="*70)
        
        cout_optimal = resultats['optimal']['cout'] if resultats['optimal'] else None
        
        # Indicateurs pour chaque méthode
        for methode in ['glouton', 'genetique']:
            if methode in resultats:
                ind = self.calculer_indicateurs_qualite(
                    resultats[methode]['cout'], 
                    cout_optimal=cout_optimal,
                    cout_aleatoire=cout_rand
                )
                
                print(f"\n[RESULTATS] {methode.upper()}:")
                print(f"   Coût: {ind['cout_obtenu']:.2f}L")
                if 'gap_optimalite_pct' in ind:
                    print(f"   Gap d'optimalité: {ind['gap_optimalite_pct']:.2f}%")
                    print(f"   Qualité: {ind['qualite_pct']:.1f}/100")
                if 'amelioration_vs_random_pct' in ind:
                    print(f"   Amélioration vs aléatoire: +{ind['amelioration_vs_random_pct']:.1f}%")
        
        # Tableau récapitulatif
        print("\n" + "="*70)
        print("TABLEAU RÉCAPITULATIF")
        print("="*70)
        
        data = []
        for methode, res in resultats.items():
            if res is not None:
                facteur = f"{res['cout']/cout_optimal:.2f}x" if cout_optimal else "N/A"
                data.append({
                    'Méthode': methode.capitalize(),
                    'Coût (L)': f"{res['cout']:.2f}",
                    'Temps (s)': f"{res['temps']:.4f}",
                    'Facteur vs optimal': facteur
                })
        
        # Affichage formaté du tableau (sans pandas)
        print("=" * 70)
        print("TABLEAU RÉCAPITULATIF")
        print("=" * 70)
        headers = ["Méthode", "Coût (L)", "Temps (s)", "Facteur vs optimal"]
        print(f"{headers[0]:>9} {headers[1]:>8} {headers[2]:>9} {headers[3]:>18}")
        
        for row in data:
            methode = row['Méthode']
            cout = row['Coût (L)']
            temps = row['Temps (s)']
            facteur = row['Facteur vs optimal']
            print(f"{methode:>9} {cout:>8} {temps:>9} {facteur:>18}")
        
        print("=" * 70 + "\n")
        
        return resultats


# ============================================================================
# EXEMPLE D'UTILISATION SI LANCÉ DIRECTEMENT
# ============================================================================

if __name__ == "__main__":
    from index import Camion, GrapheLivraison
    
    print("="*70)
    print("MODULE D'ANALYSE DE PERFORMANCES")
    print("="*70)
    print("\nCe module s'utilise depuis exemple_utilisation.py")
    print("Pour un test rapide, voici un exemple:\n")
    
    # Créer un camion 60T (3T vide + 57T charge)
    camion = Camion(poids_vide=3000, charge_max=57000, capacite_reservoir=1000)  # 60T total
    
    # Créer l'analyseur
    analyseur = AnalyseurPerformances()
    
    # Test rapide de complexité
    print("Test de complexité sur petites tailles...")
    analyseur.analyser_complexite_algorithme(
        methode='glouton',
        tailles=[3, 5, 7],
        camion=camion,
        repetitions=2
    )
    
    # Tracer
    analyseur.tracer_complexite_temporelle()
    
    print("\n✅ Module fonctionnel! Voir exemple_utilisation.py pour plus d'exemples.")