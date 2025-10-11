"""
Solveur TSP pour le problème de livraison avec contraintes de carburant.

Ce module implémente trois algorithmes de résolution pour le problème du voyageur de commerce
adapté au contexte de livraisons avec contraintes réalistes :

Algorithmes disponibles :
- Force brute : Énumération exhaustive garantissant l'optimum (complexité O(n!))
- Glouton : Heuristique du plus proche voisin (complexité O(n²))  
- Génétique : Métaheuristique évolutionniste (complexité à calculer)

Contraintes prises en compte :
- Consommation de carburant variable selon le poids du camion
- Obligation de retour au dépôt avec carburant suffisant
- Capacité maximale du camion en charge

"""

import itertools
import random
import math
from typing import List, Tuple, Optional


class SolveurTSP:
    """
    Résout le problème de tournée de livraison adapté du TSP classique.
    
    Différences avec le TSP classique :
    - Le coût n'est pas la distance mais la consommation de carburant
    - La consommation dépend du poids du camion (qui diminue au fil des livraisons)
    - Contrainte : le camion doit toujours pouvoir revenir au dépôt
    """
    
    def __init__(self, graphe):
        """
        Initialise le solveur avec un graphe de livraison.
        
        Args:
            graphe: Instance de GrapheLivraison contenant le réseau et le camion
        """
        self.graphe = graphe
        self.camion = graphe.camion
        self.meilleure_tournee = None
        self.meilleur_cout = float('inf')
    
    
    def calculer_cout_tournee(self, tournee: List[int], verbose: bool = False) -> Tuple[float, bool, str]:
        """
        Calcule le coût total (carburant) d'une tournée et vérifie sa validité.
        
        Cette fonction simule l'exécution complète de la tournée en :
        1. Partant du dépôt avec le réservoir plein et le camion chargé
        2. Visitant chaque site dans l'ordre donné
        3. Livrant la quantité fixe à chaque arrêt (poids diminue)
        4. Calculant la consommation à chaque tronçon
        5. Vérifiant qu'on peut toujours revenir au dépôt
        
        Args:
            tournee: Liste des sites à visiter dans l'ordre [0, site1, site2, ..., 0]
            verbose: Si True, affiche les détails étape par étape
        
        Returns:
            Tuple (cout_total, est_valide, message_erreur)
            - cout_total: Consommation totale de carburant (litres)
            - est_valide: True si la tournée respecte toutes les contraintes
            - message_erreur: Description du problème si non valide
        """
        # Vérifications de base
        if tournee[0] != 0 or tournee[-1] != 0:
            return float('inf'), False, "La tournée doit commencer et finir au dépôt (indice 0)"
        
        if len(set(tournee[1:-1])) != len(tournee[1:-1]):
            return float('inf'), False, "Un site est visité plusieurs fois"
        
        if len(tournee) - 2 != self.graphe.n_sites:
            return float('inf'), False, f"Il manque des sites (attendu: {self.graphe.n_sites}, trouvé: {len(tournee)-2})"
        
        # Initialisation de la simulation
        carburant_restant = self.camion.capacite_reservoir  # Réservoir plein
        charge_restante = self.graphe.n_sites * self.graphe.quantite_par_site  # Camion chargé
        cout_total = 0.0
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"SIMULATION DE LA TOURNÉE: {tournee}")
            print(f"{'='*70}")
            print(f"Départ - Carburant: {carburant_restant:.1f}L, Charge: {charge_restante:.0f}kg")
        
        # Simuler chaque tronçon de la tournée
        for i in range(len(tournee) - 1):
            site_depart = tournee[i]
            site_arrivee = tournee[i + 1]
            
            # Calculer la distance du tronçon
            distance = self.graphe.distance_ajustee(site_depart, site_arrivee)
            
            # Calculer le poids actuel du camion
            poids_actuel = self.camion.poids_actuel(charge_restante)
            
            # Calculer la consommation pour ce tronçon
            consommation = self.graphe.consommation_carburant(distance, poids_actuel)
            
            # Vérifier qu'on a assez de carburant pour ce tronçon
            if consommation > carburant_restant:
                msg = f"Panne sèche entre site {site_depart} et {site_arrivee} (besoin: {consommation:.1f}L, disponible: {carburant_restant:.1f}L)"
                if verbose:
                    print(f"\n❌ {msg}")
                return float('inf'), False, msg
            
            # Effectuer le déplacement
            carburant_restant -= consommation
            cout_total += consommation
            
            if verbose:
                print(f"\nÉtape {i+1}: Site {site_depart} -> Site {site_arrivee}")
                print(f"  Distance: {distance:.2f} km")
                print(f"  Poids camion: {poids_actuel:.0f} kg")
                print(f"  Consommation: {consommation:.2f} L")
                print(f"  Carburant restant: {carburant_restant:.2f} L")
            
            # Si on arrive à un site de livraison (pas le dépôt), livrer
            if site_arrivee != 0:
                charge_restante -= self.graphe.quantite_par_site
                
                # CONTRAINTE CRITIQUE : Vérifier qu'on peut revenir au dépôt
                peut_revenir = self.graphe.peut_revenir_au_depot(
                    site_arrivee, carburant_restant, charge_restante
                )
                
                if not peut_revenir:
                    distance_retour = self.graphe.distance_ajustee(site_arrivee, 0)
                    poids_retour = self.camion.poids_actuel(charge_restante)
                    conso_retour = self.graphe.consommation_carburant(distance_retour, poids_retour)
                    msg = (f"Impossible de revenir au dépôt depuis site {site_arrivee} "
                           f"(besoin: {conso_retour:.1f}L, disponible: {carburant_restant:.1f}L)")
                    if verbose:
                        print(f"  Livraison: {self.graphe.quantite_par_site:.0f} kg")
                        print(f"  Charge restante: {charge_restante:.0f} kg")
                        print(f"\n❌ {msg}")
                    return float('inf'), False, msg
                
                if verbose:
                    print(f"  Livraison: {self.graphe.quantite_par_site:.0f} kg")
                    print(f"  Charge restante: {charge_restante:.0f} kg")
                    print(f"  ✓ Peut revenir au dépôt")
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"✓ TOURNÉE VALIDE")
            print(f"Consommation totale: {cout_total:.2f} L")
            print(f"Carburant restant à l'arrivée: {carburant_restant:.2f} L")
            print(f"{'='*70}\n")
        
        return cout_total, True, ""
    
    
    def force_brute(self, verbose: bool = True) -> Tuple[List[int], float]:
        """
        Résout le problème par force brute (énumération exhaustive).
        
        Cette méthode teste TOUTES les permutations possibles des sites
        et garde la meilleure tournée valide.
        
        ⚠️ ATTENTION : Complexité O(n!) - Utilisable uniquement pour n ≤ 10 sites
        
        Exemples de temps d'exécution :
        - 5 sites : 120 permutations (instantané)
        - 10 sites : 3 628 800 permutations (quelques secondes)
        - 15 sites : 1 307 674 368 000 permutations (impossible en pratique)
        
        Args:
            verbose: Si True, affiche la progression
        
        Returns:
            Tuple (meilleure_tournee, meilleur_cout)
        """
        if self.graphe.n_sites > 10:
            raise ValueError(
                f"Force brute impossible avec {self.graphe.n_sites} sites "
                f"(il y aurait {math.factorial(self.graphe.n_sites):,} permutations à tester !)"
            )
        
        sites_a_visiter = list(range(1, self.graphe.n_total))  # Tous sauf le dépôt
        meilleure_tournee = None
        meilleur_cout = float('inf')
        nb_permutations = math.factorial(len(sites_a_visiter))
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"FORCE BRUTE - Test de {nb_permutations:,} permutations")
            print(f"{'='*70}\n")
        
        compteur = 0
        tournees_valides = 0
        
        # Tester toutes les permutations possibles
        for permutation in itertools.permutations(sites_a_visiter):
            compteur += 1
            
            # Construire la tournée complète : Dépôt → sites → Dépôt
            tournee = [0] + list(permutation) + [0]
            
            # Calculer le coût
            cout, valide, _ = self.calculer_cout_tournee(tournee)
            
            if valide:
                tournees_valides += 1
                if cout < meilleur_cout:
                    meilleur_cout = cout
                    meilleure_tournee = tournee
                    if verbose:
                        print(f"Nouvelle meilleure tournée trouvée! Coût: {cout:.2f}L")
                        print(f"  Parcours: {' -> '.join([f'Site {s}' if s != 0 else 'Dépôt' for s in tournee])}")
            
            # Afficher la progression tous les 10%
            if verbose and compteur % max(1, nb_permutations // 10) == 0:
                progression = (compteur / nb_permutations) * 100
                print(f"Progression: {progression:.0f}% ({compteur:,}/{nb_permutations:,})")
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"RÉSULTATS FORCE BRUTE")
            print(f"{'='*70}")
            print(f"Permutations testées: {compteur:,}")
            print(f"Tournées valides: {tournees_valides:,} ({tournees_valides/compteur*100:.1f}%)")
            print(f"Meilleur coût: {meilleur_cout:.2f}L")
            print(f"{'='*70}\n")
        
        self.meilleure_tournee = meilleure_tournee
        self.meilleur_cout = meilleur_cout
        return meilleure_tournee, meilleur_cout
    
    
    def glouton_plus_proche(self, verbose: bool = True) -> Tuple[List[int], float]:
        """
        Algorithme glouton : À chaque étape, visiter le site non visité le plus proche.
        
        Principe :
        1. Partir du dépôt
        2. Choisir le site le plus proche parmi ceux non encore visités
        3. Vérifier qu'on peut faire l'aller-retour avec le carburant restant
        4. Répéter jusqu'à avoir visité tous les sites
        5. Retourner au dépôt
        
        Avantages :
        - Très rapide : O(n²)
        - Toujours trouve une solution
        - Donne souvent de bons résultats
        
        Inconvénients :
        - Pas optimal (peut rater la meilleure solution)
        - Décisions locales sans vision globale
        
        Args:
            verbose: Si True, affiche les étapes
        
        Returns:
            Tuple (tournee, cout)
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"ALGORITHME GLOUTON : Plus proche voisin")
            print(f"{'='*70}\n")
        
        # Initialisation
        tournee = [0]  # Commencer au dépôt
        sites_restants = set(range(1, self.graphe.n_total))
        carburant = self.camion.capacite_reservoir
        charge = self.graphe.n_sites * self.graphe.quantite_par_site
        
        # Tant qu'il reste des sites à visiter
        while sites_restants:
            site_actuel = tournee[-1]
            meilleur_site = None
            meilleure_distance = float('inf')
            
            # Chercher le site le plus proche parmi ceux non visités
            for site in sites_restants:
                distance = self.graphe.distance_ajustee(site_actuel, site)
                
                # Vérifier qu'on peut aller à ce site ET revenir au dépôt après
                poids_actuel = self.camion.poids_actuel(charge)
                conso_aller = self.graphe.consommation_carburant(distance, poids_actuel)
                
                if conso_aller <= carburant:
                    # Simuler la livraison
                    charge_apres = charge - self.graphe.quantite_par_site
                    carburant_apres = carburant - conso_aller
                    
                    # Vérifier qu'on peut revenir au dépôt
                    if self.graphe.peut_revenir_au_depot(site, carburant_apres, charge_apres):
                        if distance < meilleure_distance:
                            meilleure_distance = distance
                            meilleur_site = site
            
            # Si aucun site accessible, la tournée est impossible
            if meilleur_site is None:
                if verbose:
                    print(f"X Impossible de continuer depuis site {site_actuel}")
                    print(f"Sites restants: {sites_restants}")
                return None, float('inf')
            
            # Aller au site choisi
            poids = self.camion.poids_actuel(charge)
            conso = self.graphe.consommation_carburant(meilleure_distance, poids)
            carburant -= conso
            charge -= self.graphe.quantite_par_site
            
            tournee.append(meilleur_site)
            sites_restants.remove(meilleur_site)
            
            if verbose:
                print(f"Étape {len(tournee)-1}: Site {site_actuel} -> Site {meilleur_site}")
                print(f"  Distance: {meilleure_distance:.2f} km")
                print(f"  Consommation: {conso:.2f} L")
                print(f"  Carburant restant: {carburant:.2f} L")
                print(f"  Sites restants: {len(sites_restants)}\n")
        
        # Retour au dépôt
        tournee.append(0)
        
        # Calculer le coût total
        cout, valide, msg = self.calculer_cout_tournee(tournee, verbose=False)
        
        if verbose:
            print(f"{'='*70}")
            print(f"Tournée finale: {' -> '.join([f'Site {s}' if s != 0 else 'Dépôt' for s in tournee])}")
            print(f"Coût total: {cout:.2f}L")
            print(f"Validité: {'OK VALIDE' if valide else 'X INVALIDE - ' + msg}")
            print(f"{'='*70}\n")
        
        self.meilleure_tournee = tournee
        self.meilleur_cout = cout
        return tournee, cout
    
    
    def comparer_methodes(self):
        """
        Compare force brute et glouton (si le nombre de sites le permet).
        
        Utile pour :
        - Voir l'écart entre l'optimal (force brute) et l'heuristique (glouton)
        - Comprendre les limites de chaque approche
        """
        print(f"\n{'#'*70}")
        print(f"COMPARAISON DES MÉTHODES")
        print(f"{'#'*70}\n")
        
        # Glouton (toujours faisable)
        print("1️⃣  Méthode GLOUTON (Plus proche voisin)")
        print("─" * 70)
        tournee_glouton, cout_glouton = self.glouton_plus_proche(verbose=False)
        print(f"Tournée: {' -> '.join([f'S{s}' if s != 0 else 'D' for s in tournee_glouton])}")
        print(f"Coût: {cout_glouton:.2f}L\n")
        
        # Force brute (si possible)
        if self.graphe.n_sites <= 10:
            print("2️⃣  Méthode FORCE BRUTE (Optimal)")
            print("─" * 70)
            tournee_fb, cout_fb = self.force_brute(verbose=False)
            print(f"Tournée: {' -> '.join([f'S{s}' if s != 0 else 'D' for s in tournee_fb])}")
            print(f"Coût: {cout_fb:.2f}L\n")
            
            # Analyse
            print("📊 ANALYSE")
            print("─" * 70)
            if cout_glouton == cout_fb:
                print("✓ Le glouton a trouvé la solution OPTIMALE !")
            else:
                ecart = cout_glouton - cout_fb
                ecart_pct = (ecart / cout_fb) * 100
                print(f"Écart: +{ecart:.2f}L (+{ecart_pct:.1f}%)")
                print(f"Le glouton consomme {ecart:.2f}L de plus que l'optimal")
        else:
            print(f"⚠️  Force brute impossible avec {self.graphe.n_sites} sites")
            print(f"   (il faudrait tester {math.factorial(self.graphe.n_sites):,} permutations !)\n")
        
        print(f"{'#'*70}\n")
    
    
    def algorithme_genetique(self, taille_population: int = 50, 
                            nb_generations: int = 100,
                            taux_mutation: float = 0.1,
                            taux_elitisme: float = 0.2,
                            verbose: bool = True) -> Tuple[List[int], float, List[float]]:
        """
        Résout le problème avec un algorithme génétique évolutionniste.
        
        Métaheuristique inspirée de l'évolution naturelle qui fait évoluer
        une population de solutions vers des tournées de meilleure qualité.
        
        Étapes principales :
        1. Génération d'une population initiale intelligente (mélange de strategies)
        2. Évaluation du fitness de chaque individu (inverse du coût)
        3. Sélection des meilleurs parents par tournoi
        4. Croisement (Order Crossover) pour créer des enfants
        5. Mutation intelligente avec plusieurs stratégies
        6. Élitisme pour conserver les meilleures solutions
        
        Args:
            taille_population: Nombre d'individus dans la population
            nb_generations: Nombre de générations à faire évoluer
            taux_mutation: Probabilité de mutation (0.0 à 1.0)
            taux_elitisme: Fraction des meilleurs individus conservés
            verbose: Affichage des détails de progression
        
        Returns:
            Tuple (meilleure_tournee, meilleur_cout, historique_progression)
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"ALGORITHME GÉNÉTIQUE")
            print(f"{'='*70}")
            print(f"Population: {taille_population} individus")
            print(f"Générations: {nb_generations}")
            print(f"Taux de mutation: {taux_mutation*100}%")
            print(f"Élitisme: {taux_elitisme*100}%\n")
        
        sites = list(range(1, self.graphe.n_total))
        
        # === ÉTAPE 1 : INITIALISATION INTELLIGENTE DE LA POPULATION ===
        def creer_individu_aleatoire():
            """Crée un individu (tournée) aléatoire."""
            individu = sites.copy()
            random.shuffle(individu)
            return [0] + individu + [0]
        
        def creer_individu_glouton_varie():
            """
            Crée un individu basé sur l'algorithme glouton avec variation.
            
            Utilise le glouton comme base mais ajoute de la randomisation
            pour créer de la diversité tout en gardant une structure valide.
            """
            try:
                # Essayer de créer une solution glouton valide
                tournee_glouton, _ = self.glouton_plus_proche(verbose=False)
                if tournee_glouton is not None:
                    # Ajouter une variation à la solution glouton
                    sites_visite = tournee_glouton[1:-1]  # Sans les dépôts
                    
                    # Variation aléatoire : échanger 2 sites avec 50% de chance
                    if random.random() < 0.5 and len(sites_visite) >= 2:
                        i, j = random.sample(range(len(sites_visite)), 2)
                        sites_visite[i], sites_visite[j] = sites_visite[j], sites_visite[i]
                    
                    return [0] + sites_visite + [0]
                else:
                    # Si glouton échoue, créer aléatoire
                    return creer_individu_aleatoire()
            except:
                return creer_individu_aleatoire()
        
        def creer_individu_plus_proche_first():
            """
            Crée un individu en partant du site le plus proche du dépôt.
            
            Stratégie conservative : commencer par les sites proches
            pour maximiser les chances de validité.
            """
            sites_distances = []
            for site in sites:
                dist = self.graphe.distance_ajustee(0, site)
                sites_distances.append((site, dist))
            
            # Trier par distance croissante
            sites_distances.sort(key=lambda x: x[1])
            
            # Prendre les 60% plus proches en premier, puis mélanger
            nb_proches = max(1, int(len(sites_distances) * 0.6))
            sites_proches = [s[0] for s in sites_distances[:nb_proches]]
            sites_lointains = [s[0] for s in sites_distances[nb_proches:]]
            
            random.shuffle(sites_proches)
            random.shuffle(sites_lointains)
            
            return [0] + sites_proches + sites_lointains + [0]
        
        def reparer_individu(tournee):
            """
            Répare un individu invalide en réorganisant les sites.
            
            Si une tournée n'est pas valide (contraintes de carburant),
            essaie de la réorganiser pour la rendre valide.
            """
            cout, valide, _ = self.calculer_cout_tournee(tournee, verbose=False)
            if valide:
                return tournee  # Déjà valide
            
            # Stratégie de réparation : trier par distance depuis le dépôt
            sites_tournee = tournee[1:-1]  # Sites sans les dépôts
            sites_avec_dist = []
            
            for site in sites_tournee:
                dist = self.graphe.distance_ajustee(0, site)
                sites_avec_dist.append((site, dist))
            
            # Trier par distance croissante (plus proches d'abord)
            sites_avec_dist.sort(key=lambda x: x[1])
            sites_repares = [s[0] for s in sites_avec_dist]
            
            tournee_reparee = [0] + sites_repares + [0]
            
            # Vérifier si la réparation a fonctionné
            cout, valide, _ = self.calculer_cout_tournee(tournee_reparee, verbose=False)
            if valide:
                return tournee_reparee
            else:
                # Si la réparation échoue, retourner l'originale
                return tournee
        
        # === CRÉATION DE LA POPULATION HYBRIDE ===
        population = []
        
        # 1. D'abord, essayer d'inclure une solution glouton valide
        try:
            tournee_glouton, cout_glouton = self.glouton_plus_proche(verbose=False)
            if tournee_glouton is not None:
                population.append(tournee_glouton)
                if verbose:
                    print(f"✓ Solution glouton ajoutée à la population (coût: {cout_glouton:.2f}L)")
        except:
            pass
        
        # 2. Créer le reste de la population avec différentes stratégies
        while len(population) < taille_population:
            rand = random.random()
            
            if rand < 0.4:  # 40% : Variations du glouton
                individu = creer_individu_glouton_varie()
            elif rand < 0.7:  # 30% : Plus proches d'abord
                individu = creer_individu_plus_proche_first()
            else:  # 30% : Complètement aléatoire
                individu = creer_individu_aleatoire()
            
            # Tenter de réparer si invalide
            individu = reparer_individu(individu)
            population.append(individu)
        
        if verbose:
            # Compter combien de solutions valides dans la population initiale
            nb_valides = 0
            for individu in population:
                _, valide, _ = self.calculer_cout_tournee(individu, verbose=False)
                if valide:
                    nb_valides += 1
            
            print(f"Population initiale: {nb_valides}/{len(population)} solutions valides ({nb_valides/len(population)*100:.1f}%)")
        
        # === FONCTION FITNESS AMÉLIORÉE ===
        def evaluer_fitness(tournee):
            """
            Évalue la qualité d'une tournée.
            Retourne (fitness, cout, validite)
            
            Fitness élevé = bonne solution
            """
            cout, valide, _ = self.calculer_cout_tournee(tournee, verbose=False)
            if not valide:
                # Pénaliser fortement les solutions invalides
                return 0.0, cout, False
            else:
                # Fitness inversement proportionnel au coût
                # Plus le coût est faible, plus le fitness est élevé
                fitness = 1000.0 / cout
                return fitness, cout, True
        
        # === OPÉRATEURS GÉNÉTIQUES ===
        def selectionner_parents(population_evaluee):
            """
            Sélection par tournoi : choisir N individus au hasard,
            garder le meilleur.
            """
            taille_tournoi = 3
            tournoi = random.sample(population_evaluee, taille_tournoi)
            gagnant = max(tournoi, key=lambda x: x[1])  # x[1] = fitness
            return gagnant[0]  # Retourner la tournée
        
        def croiser(parent1, parent2):
            """
            Croisement OX (Order Crossover) :
            1. Choisir un segment du parent1
            2. Compléter avec les villes du parent2 dans l'ordre
            """
            # Extraire les sites (sans les dépôts au début et fin)
            p1 = parent1[1:-1]
            p2 = parent2[1:-1]
            
            # Choisir un segment aléatoire
            debut = random.randint(0, len(p1) - 2)
            fin = random.randint(debut + 1, len(p1))
            
            # Segment du parent1
            enfant = [None] * len(p1)
            enfant[debut:fin] = p1[debut:fin]
            
            # Compléter avec parent2
            pos = fin
            for site in p2:
                if site not in enfant:
                    if pos >= len(enfant):
                        pos = 0
                    while enfant[pos] is not None:
                        pos += 1
                        if pos >= len(enfant):
                            pos = 0
                    enfant[pos] = site
            
            return [0] + enfant + [0]
        
        def muter(tournee):
            """
            Mutation intelligente avec plusieurs stratégies.
            """
            if random.random() >= taux_mutation:
                return tournee
            
            tournee_mut = tournee.copy()
            strategie = random.random()
            
            if strategie < 0.4:  # 40% : Échange simple
                i, j = random.sample(range(1, len(tournee) - 1), 2)
                tournee_mut[i], tournee_mut[j] = tournee_mut[j], tournee_mut[i]
            
            elif strategie < 0.7:  # 30% : Inversion d'un segment
                debut = random.randint(1, len(tournee) - 3)
                fin = random.randint(debut + 1, len(tournee) - 1)
                tournee_mut[debut:fin] = reversed(tournee_mut[debut:fin])
            
            else:  # 30% : Déplacement d'un site
                # Prendre un site et le déplacer ailleurs
                if len(tournee) > 3:  # Au moins 2 sites
                    site_idx = random.randint(1, len(tournee) - 2)
                    site = tournee_mut.pop(site_idx)
                    nouvelle_pos = random.randint(1, len(tournee_mut) - 1)
                    tournee_mut.insert(nouvelle_pos, site)
            
            return tournee_mut
        
        def amelioration_locale(tournee):
            """
            Amélioration locale 2-opt : échange les arêtes pour réduire le coût.
            """
            meilleure_tournee = tournee.copy()
            cout_actuel, valide_actuel, _ = self.calculer_cout_tournee(meilleure_tournee, verbose=False)
            
            if not valide_actuel:
                return meilleure_tournee  # Pas d'amélioration sur solution invalide
            
            # Essayer toutes les améliorations 2-opt
            for i in range(1, len(tournee) - 2):
                for j in range(i + 1, len(tournee) - 1):
                    # Créer une nouvelle tournée en inversant le segment [i:j+1]
                    nouvelle_tournee = tournee.copy()
                    nouvelle_tournee[i:j+1] = reversed(nouvelle_tournee[i:j+1])
                    
                    cout_nouveau, valide_nouveau, _ = self.calculer_cout_tournee(nouvelle_tournee, verbose=False)
                    
                    if valide_nouveau and cout_nouveau < cout_actuel:
                        meilleure_tournee = nouvelle_tournee
                        cout_actuel = cout_nouveau
            
            return meilleure_tournee
        
        # === ÉVOLUTION SUR PLUSIEURS GÉNÉRATIONS ===
        meilleur_cout_global = float('inf')
        meilleure_tournee_globale = None
        historique_meilleurs = []
        
        nb_elite = int(taille_population * taux_elitisme)
        
        for generation in range(nb_generations):
            # Évaluer toute la population
            population_evaluee = []
            for individu in population:
                fitness, cout, valide = evaluer_fitness(individu)
                population_evaluee.append((individu, fitness, cout, valide))
            
            # Trier par fitness (meilleurs en premier)
            population_evaluee.sort(key=lambda x: x[1], reverse=True)
            
            # Garder le meilleur
            meilleur_generation = population_evaluee[0]
            if meilleur_generation[3] and meilleur_generation[2] < meilleur_cout_global:
                meilleur_cout_global = meilleur_generation[2]
                meilleure_tournee_globale = meilleur_generation[0]
                if verbose:
                    print(f"Génération {generation+1}: Nouveau meilleur coût = {meilleur_cout_global:.2f}L")
            
            historique_meilleurs.append(meilleur_cout_global)
            
            # Afficher progression tous les 10%
            if verbose and (generation + 1) % max(1, nb_generations // 10) == 0:
                print(f"  Génération {generation+1}/{nb_generations} - Meilleur: {meilleur_cout_global:.2f}L")
            
            # === CRÉER LA NOUVELLE GÉNÉRATION ===
            nouvelle_population = []
            
            # Élitisme : garder les meilleurs
            for i in range(nb_elite):
                nouvelle_population.append(population_evaluee[i][0])
            
            # Créer le reste par croisement et mutation
            while len(nouvelle_population) < taille_population:
                parent1 = selectionner_parents(population_evaluee)
                parent2 = selectionner_parents(population_evaluee)
                enfant = croiser(parent1, parent2)
                enfant = muter(enfant)
                
                # Amélioration locale occasionnelle (10% des enfants)
                if random.random() < 0.1:
                    enfant = amelioration_locale(enfant)
                
                nouvelle_population.append(enfant)
            
            population = nouvelle_population
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"RÉSULTATS ALGORITHME GÉNÉTIQUE")
            print(f"{'='*70}")
            print(f"Meilleur coût trouvé: {meilleur_cout_global:.2f}L")
            print(f"Tournée: {' -> '.join([f'Site {s}' if s != 0 else 'Dépôt' for s in meilleure_tournee_globale])}")
            print(f"{'='*70}\n")
        
        self.meilleure_tournee = meilleure_tournee_globale
        self.meilleur_cout = meilleur_cout_global
        
        return meilleure_tournee_globale, meilleur_cout_global, historique_meilleurs