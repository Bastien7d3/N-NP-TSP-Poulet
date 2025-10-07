#import
import random
import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt


class Camion:
    """
    Représente le camion de livraison avec toutes ses caractéristiques physiques.
    
    Cette classe encapsule les propriétés du véhicule qui influencent :
    - La capacité de transport (combien de poulets peut-il transporter ?)
    - La consommation de carburant (qui dépend du poids)
    - L'autonomie (capacité du réservoir)
    """
    
    def __init__(self, poids_vide: float, charge_max: float, capacite_reservoir: float):
        """
        Initialise un camion avec ses caractéristiques techniques.
        
        Args:
            poids_vide: Poids du camion sans aucune marchandise (kg)
            charge_max: Poids maximum de marchandises transportables (kg)
            capacite_reservoir: Capacité du réservoir de carburant (litres)
        """
        self.poids_vide = poids_vide
        self.charge_max = charge_max
        # Le poids plein est utilisé pour les calculs de consommation au départ
        self.poids_plein = poids_vide + charge_max
        self.capacite_reservoir = capacite_reservoir
        
    def poids_actuel(self, charge_restante: float) -> float:
        """
        Calcule le poids total actuel du camion.
        
        Le poids total change au cours de la tournée car le camion livre
        des poulets à chaque arrêt. Un camion plus léger consomme moins.
        
        Args:
            charge_restante: Poids de poulets encore dans le camion (kg)
        
        Returns:
            Poids total = poids du véhicule vide + marchandises restantes (kg)
        """
        return self.poids_vide + charge_restante
    
    def __repr__(self):
        """Représentation textuelle du camion pour affichage"""
        return (f"Camion(vide={self.poids_vide}kg, charge_max={self.charge_max}kg, "
                f"reservoir={self.capacite_reservoir}L)")


class GrapheLivraison:
    """
    Représente le réseau de villes et routes pour les livraisons de poulets.
    
    Cette classe gère :
    - Les positions des sites (dépôt + sites de livraison)
    - Les distances entre sites avec prise en compte des embouteillages
    - Les contraintes de capacité et de carburant du camion
    """
    
    def __init__(self, n_sites: int = None, camion: Camion = None, 
                 quantite_par_site: float = None, seed: int = None,
                 matrice_distances: np.ndarray = None, positions: np.ndarray = None):
        """
        Initialise le graphe de livraison.
        
        Deux modes d'utilisation possibles :
        1) Génération automatique : fournir n_sites, camion, quantite_par_site
        2) Import personnalisé : fournir matrice_distances, camion, quantite_par_site
        
        Args:
            n_sites: Nombre de sites de livraison (sans le dépôt)
            camion: Instance de la classe Camion
            quantite_par_site: Quantité de poulets livrée à chaque site (kg)
            seed: Graine aléatoire pour reproductibilité (mode génération)
            matrice_distances: Matrice personnalisée des distances (mode import)
                              Format: array de taille (n+1, n+1) où n = nb sites
                              L'indice 0 doit correspondre au dépôt
            positions: Positions 2D des sites pour visualisation (optionnel en mode import)
        """
        # Initialiser le générateur aléatoire si seed fourni
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Stockage des paramètres essentiels
        self.camion = camion
        self.quantite_par_site = quantite_par_site
        self.depot = 0  # Le dépôt est toujours le nœud d'indice 0
        
        # === MODE IMPORT : Matrice personnalisée fournie ===
        if matrice_distances is not None:
            self._init_from_matrix(matrice_distances, positions)
        # === MODE GENERATION : Création automatique ===
        elif n_sites is not None:
            self._init_from_generation(n_sites)
        else:
            raise ValueError(
                "Il faut fournir soit 'n_sites' (génération auto), "
                "soit 'matrice_distances' (import)"
            )
        
        # Vérification : la charge totale ne doit pas dépasser la capacité du camion
        charge_totale_necessaire = self.n_sites * quantite_par_site
        if charge_totale_necessaire > camion.charge_max:
            raise ValueError(
                f"Charge totale nécessaire ({charge_totale_necessaire}kg) "
                f"dépasse la capacité du camion ({camion.charge_max}kg)"
            )
    
    def _init_from_matrix(self, matrice_distances: np.ndarray, positions: np.ndarray = None):
        """
        Initialise le graphe à partir d'une matrice de distances personnalisée.
        
        Cette méthode permet d'importer un graphe déjà défini plutôt que d'en
        générer un aléatoirement.
        
        Args:
            matrice_distances: Matrice carrée symétrique des distances (km)
            positions: Positions 2D optionnelles pour la visualisation
        """
        # Vérifications de la matrice
        if len(matrice_distances.shape) != 2:
            raise ValueError("La matrice doit être 2D")
        if matrice_distances.shape[0] != matrice_distances.shape[1]:
            raise ValueError("La matrice doit être carrée")
        
        # Calcul du nombre de sites (en excluant le dépôt)
        self.n_total = matrice_distances.shape[0]
        self.n_sites = self.n_total - 1
        
        # Utiliser directement la matrice fournie comme distances de base
        self.distances_base = matrice_distances.copy()
        
        # Générer des facteurs d'embouteillage aléatoires
        self.facteurs_embouteillage = self._generer_embouteillages()
        
        # Calculer les distances finales (base × embouteillage)
        self.distances_ajustees = self.distances_base * self.facteurs_embouteillage
        
        # Gérer les positions pour la visualisation
        if positions is not None:
            self.positions = positions
        else:
            # Générer des positions arbitraires pour pouvoir visualiser
            # (ce ne sera pas géographiquement exact mais permet le dessin)
            self.positions = self._generer_positions()
    
    def _init_from_generation(self, n_sites: int):
        """
        Initialise le graphe en générant aléatoirement les positions et distances.
        
        Cette méthode crée un réseau de sites distribués aléatoirement dans
        un espace 2D, puis calcule les distances euclidiennes entre eux.
        
        Args:
            n_sites: Nombre de sites de livraison à générer
        """
        self.n_sites = n_sites
        self.n_total = n_sites + 1  # +1 pour inclure le dépôt
        
        # Étape 1 : Générer les positions 2D de tous les sites
        self.positions = self._generer_positions()
        
        # Étape 2 : Calculer les distances euclidiennes entre tous les sites
        self.distances_base = self._calculer_distances_base()
        
        # Étape 3 : Générer des facteurs d'embouteillage aléatoires
        self.facteurs_embouteillage = self._generer_embouteillages()
        
        # Étape 4 : Combiner distance et embouteillage pour obtenir la distance finale
        self.distances_ajustees = self.distances_base * self.facteurs_embouteillage
        
    def _generer_positions(self) -> np.ndarray:
        """
        Génère des positions aléatoires pour chaque site dans un espace 2D.
        
        Le dépôt est placé au centre (0, 0) et les sites de livraison sont
        distribués aléatoirement autour dans un carré de 200km × 200km.
        
        Returns:
            Array numpy de forme (n_total, 2) contenant les coordonnées (x, y)
            de chaque site. L'indice 0 correspond au dépôt.
        """
        # Initialiser le tableau : une ligne par site, 2 colonnes (x, y)
        positions = np.zeros((self.n_total, 2))
        
        # Le dépôt (indice 0) reste à l'origine (0, 0)
        # positions[0] = [0, 0] (déjà fait par np.zeros)
        
        # Générer des positions aléatoires pour les autres sites (indices 1 à n)
        # Chaque coordonnée est tirée uniformément entre -100 et +100 km
        positions[1:] = np.random.uniform(-100, 100, (self.n_sites, 2))
        
        return positions
    
    def _calculer_distances_base(self) -> np.ndarray:
        """
        Calcule la matrice des distances euclidiennes entre tous les sites.
        
        La distance euclidienne entre deux points (x1, y1) et (x2, y2) est :
        distance = √[(x2-x1)² + (y2-y1)²]
        
        Cette matrice représente les distances "à vol d'oiseau" sans tenir
        compte des embouteillages (qui seront ajoutés après).
        
        Returns:
            Matrice carrée symétrique de taille (n_total, n_total) où
            distances[i][j] = distance entre le site i et le site j
        """
        n = self.n_total
        distances = np.zeros((n, n))
        
        # Parcourir tous les couples de sites (i, j)
        # On ne calcule que la moitié supérieure de la matrice car elle est symétrique
        for i in range(n):
            for j in range(i + 1, n):
                # Calculer la distance euclidienne entre les sites i et j
                # np.linalg.norm calcule la norme du vecteur différence
                dist = np.linalg.norm(self.positions[i] - self.positions[j])
                
                # Remplir les deux cases symétriques
                distances[i, j] = dist
                distances[j, i] = dist
        
        return distances
    
    def _generer_embouteillages(self) -> np.ndarray:
        """
        Génère des facteurs d'embouteillage aléatoires pour chaque route.
        
        Chaque route entre deux sites peut être plus ou moins embouteillée.
        Un facteur de 1.0 signifie trafic fluide (pas de rallongement).
        Un facteur de 2.0 signifie trafic dense (distance effective doublée).
        
        Ces facteurs simulent les conditions de circulation variables selon
        les routes et les heures.
        
        Returns:
            Matrice carrée symétrique de taille (n_total, n_total) où
            facteurs[i][j] = coefficient multiplicateur entre 1.0 et 2.0
        """
        n = self.n_total
        # Initialiser à 1.0 (pas d'embouteillage par défaut)
        facteurs = np.ones((n, n))
        
        # Parcourir tous les couples de sites
        for i in range(n):
            for j in range(i + 1, n):
                # Tirer aléatoirement un facteur entre 1.0 et 2.0
                # 1.0 = fluide, 1.5 = modéré, 2.0 = très embouteillé
                facteur = random.uniform(1.0, 2.0)
                
                # Remplir symétriquement (aller et retour ont le même facteur)
                facteurs[i, j] = facteur
                facteurs[j, i] = facteur
        
        return facteurs
    
    def consommation_carburant(self, distance: float, poids_camion: float) -> float:
        """
        Calcule la consommation de carburant pour parcourir un tronçon.
        
        La consommation dépend de deux facteurs :
        1. La distance à parcourir
        2. Le poids du camion (un camion chargé consomme plus)
        
        Formule utilisée : 
        consommation = (distance / 100) × (conso_base + coef_poids × poids)
        
        Exemple concret :
        - Camion de 10 000 kg
        - Distance de 50 km
        - Consommation = (50/100) × (20 + 0.005×10000) = 0.5 × 70 = 35 litres
        
        Args:
            distance: Distance du tronçon en kilomètres
            poids_camion: Poids actuel total du camion en kg
        
        Returns:
            Consommation estimée en litres
        """
        # Paramètres calibrés pour un camion de livraison réaliste
        coef_base = 20      # Consommation à vide : 20 L/100km
        coef_poids = 0.005  # Augmentation : 0.5 L/100km par tonne
        
        # Calculer la consommation aux 100 km
        conso_par_100km = coef_base + coef_poids * poids_camion
        
        # Ajuster pour la distance réelle parcourue
        return (distance / 100) * conso_par_100km
    
    def distance_ajustee(self, site_i: int, site_j: int) -> float:
        """
        Retourne la distance effective entre deux sites en tenant compte des embouteillages.
        
        Cette distance combine :
        - La distance géographique réelle (distance "à vol d'oiseau")
        - Le facteur d'embouteillage de la route
        
        Exemple : Si la distance de base est 50 km et le facteur d'embouteillage
        est 1.5, la distance ajustée sera 75 km (équivalent temps/carburant).
        
        Args:
            site_i: Indice du premier site
            site_j: Indice du deuxième site
        
        Returns:
            Distance ajustée en kilomètres
        """
        return self.distances_ajustees[site_i, site_j]
    
    def peut_revenir_au_depot(self, site_actuel: int, carburant_restant: float, 
                              charge_restante: float) -> bool:
        """
        Vérifie si le camion a assez de carburant pour revenir au dépôt.
        
        Cette fonction est CRUCIALE pour la contrainte de sécurité : à tout moment
        de la tournée, le camion doit pouvoir rentrer au dépôt. Si ce n'est pas
        le cas, certains sites ne pourront pas être visités.
        
        Le calcul prend en compte :
        1. La distance pour revenir au dépôt depuis la position actuelle
        2. Le poids actuel du camion (avec la charge restante)
        3. La consommation de carburant induite
        
        Args:
            site_actuel: Site où se trouve actuellement le camion (indice)
            carburant_restant: Quantité de carburant encore disponible (litres)
            charge_restante: Poids de poulets encore dans le camion (kg)
        
        Returns:
            True si le retour est possible avec le carburant disponible
            False sinon (situation dangereuse, ne pas aller plus loin)
        """
        # Étape 1 : Calculer la distance du site actuel jusqu'au dépôt
        distance_retour = self.distance_ajustee(site_actuel, self.depot)
        
        # Étape 2 : Calculer le poids total actuel du camion
        poids = self.camion.poids_actuel(charge_restante)
        
        # Étape 3 : Estimer la consommation nécessaire pour ce trajet retour
        conso_retour = self.consommation_carburant(distance_retour, poids)
        
        # Étape 4 : Vérifier si on a assez de carburant
        return carburant_restant >= conso_retour
    
    def visualiser(self, tournee: Optional[List[int]] = None):
        """
        Visualise le graphe et optionnellement une tournée spécifique.
        
        Cette fonction crée un graphique montrant :
        - Toutes les routes possibles (en gris clair)
        - La tournée proposée si fournie (en bleu avec flèches)
        - Le dépôt (carré vert)
        - Les sites de livraison (points rouges)
        
        Args:
            tournee: Liste ordonnée des sites formant la tournée
                    Exemple : [0, 2, 4, 1, 3, 5, 0]
                    signifie : Dépôt → Site2 → Site4 → Site1 → Site3 → Site5 → Dépôt
                    Si None, affiche seulement le réseau sans parcours
        """
        plt.figure(figsize=(10, 8))
        
        # === ÉTAPE 1 : Dessiner toutes les routes possibles en arrière-plan ===
        for i in range(self.n_total):
            for j in range(i + 1, self.n_total):
                plt.plot([self.positions[i, 0], self.positions[j, 0]],
                        [self.positions[i, 1], self.positions[j, 1]],
                        'lightgray', linewidth=0.5, zorder=1)
        
        # === ÉTAPE 2 : Dessiner la tournée si elle est fournie ===
        if tournee:
            # Tracer chaque segment de la tournée
            for i in range(len(tournee) - 1):
                site_depart = tournee[i]
                site_arrivee = tournee[i + 1]
                
                # Tracer la ligne entre les deux sites
                plt.plot([self.positions[site_depart, 0], self.positions[site_arrivee, 0]],
                        [self.positions[site_depart, 1], self.positions[site_arrivee, 1]],
                        'b-', linewidth=2, zorder=2)
                
                # Ajouter une flèche pour indiquer le sens de parcours
                dx = self.positions[site_arrivee, 0] - self.positions[site_depart, 0]
                dy = self.positions[site_arrivee, 1] - self.positions[site_depart, 1]
                plt.arrow(self.positions[site_depart, 0], self.positions[site_depart, 1],
                         dx * 0.8, dy * 0.8, head_width=3, head_length=2,
                         fc='blue', ec='blue', zorder=2)
        
        # === ÉTAPE 3 : Dessiner les sites ===
        # Sites de livraison (points rouges)
        plt.scatter(self.positions[1:, 0], self.positions[1:, 1],
                   c='red', s=200, zorder=3, label='Sites de livraison')
        # Dépôt (carré vert plus gros)
        plt.scatter(self.positions[0, 0], self.positions[0, 1],
                   c='green', s=300, marker='s', zorder=3, label='Dépôt')
        
        # === ÉTAPE 4 : Ajouter les étiquettes des sites ===
        for i in range(self.n_total):
            label = 'Dépôt' if i == 0 else f'Site {i}'
            plt.annotate(label, self.positions[i], fontsize=9,
                        ha='center', va='bottom')
        
        # === ÉTAPE 5 : Mise en forme du graphique ===
        plt.xlabel('Position X (km)')
        plt.ylabel('Position Y (km)')
        plt.title('Réseau de livraison de poulets')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')  # Même échelle sur x et y
        plt.tight_layout()
        plt.show()
    
    def __repr__(self):
        """Représentation textuelle du graphe pour affichage"""
        return (f"GrapheLivraison(sites={self.n_sites}, "
                f"quantite_par_site={self.quantite_par_site}kg)")


# ============================================================================
# EXEMPLES D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    
    # ========================================================================
    # EXEMPLE 1 : Génération automatique d'un graphe
    # ========================================================================
    print("="*70)
    print("EXEMPLE 1 : Génération automatique")
    print("="*70)
    
    # Créer un camion avec des caractéristiques réalistes
    camion = Camion(
        poids_vide=8000,        # 8 tonnes à vide
        charge_max=12000,       # 12 tonnes de charge maximale
        capacite_reservoir=300  # 300 litres de carburant
    )
    
    # Créer un graphe avec 5 sites de livraison générés aléatoirement
    graphe_auto = GrapheLivraison(
        n_sites=5,
        camion=camion,
        quantite_par_site=2000,  # 2 tonnes de poulets par site
        seed=42  # Pour avoir toujours le même graphe (reproductibilité)
    )
    
    print(graphe_auto)
    print(camion)
    print(f"\nCharge totale à livrer: {graphe_auto.n_sites * graphe_auto.quantite_par_site}kg")
    print(f"\nDistances ajustées entre le dépôt et les sites:")
    for i in range(1, graphe_auto.n_total):
        dist = graphe_auto.distance_ajustee(0, i)
        facteur = graphe_auto.facteurs_embouteillage[0, i]
        print(f"  Dépôt -> Site {i}: {dist:.2f} km (embouteillage: x{facteur:.2f})")
    
    # Test de consommation
    print(f"\n{'─'*70}")
    print("Test de consommation pour aller du dépôt au site 1 (camion plein):")
    dist = graphe_auto.distance_ajustee(0, 1)
    poids = camion.poids_plein
    conso = graphe_auto.consommation_carburant(dist, poids)
    print(f"  Distance: {dist:.2f} km")
    print(f"  Poids: {poids:.0f} kg")
    print(f"  Consommation: {conso:.2f} L")
    
    # Visualisation du graphe seul
    print("\nVisualisation du réseau...")
    graphe_auto.visualiser()
    
    # Exemple de tournée manuelle
    print(f"\n{'─'*70}")
    print("Visualisation avec une tournée exemple:")
    tournee_exemple = [0, 2, 4, 1, 3, 5, 0]  # Dépôt -> sites -> Dépôt
    print(f"Tournée: {' -> '.join([f'Site {i}' if i != 0 else 'Dépôt' for i in tournee_exemple])}")
    graphe_auto.visualiser(tournee=tournee_exemple)
    
    
    # ========================================================================
    # EXEMPLE 2 : Import d'un graphe personnalisé via matrice
    # ========================================================================
    print("\n" + "="*70)
    print("EXEMPLE 2 : Import d'un graphe personnalisé")
    print("="*70)
    
    # Créer une matrice de distances personnalisée
    # Ici : dépôt (0) + 4 sites de livraison (1, 2, 3, 4)
    matrice_custom = np.array([
        [0,   50,  80,  120, 90],   # Distances depuis le dépôt
        [50,  0,   40,  100, 70],   # Distances depuis site 1
        [80,  40,  0,   60,  50],   # Distances depuis site 2
        [120, 100, 60,  0,   40],   # Distances depuis site 3
        [90,  70,  50,  40,  0]     # Distances depuis site 4
    ])
    
    # Optionnel : définir des positions pour une meilleure visualisation
    positions_custom = np.array([
        [0, 0],      # Dépôt au centre
        [50, 0],     # Site 1 à l'est
        [0, 80],     # Site 2 au nord
        [-70, -50],  # Site 3 au sud-ouest
        [60, 60]     # Site 4 au nord-est
    ])
    
    # Créer le graphe à partir de la matrice
    graphe_custom = GrapheLivraison(
        matrice_distances=matrice_custom,
        positions=positions_custom,  # Optionnel
        camion=camion,
        quantite_par_site=2500,  # 2.5 tonnes par site
        seed=123
    )
    
    print(graphe_custom)
    print(f"\nMatrice de distances importée:")
    print(matrice_custom)
    
    print(f"\nDistances ajustées avec embouteillages:")
    for i in range(1, graphe_custom.n_total):
        dist_base = graphe_custom.distances_base[0, i]
        dist_ajustee = graphe_custom.distance_ajustee(0, i)
        print(f"  Dépôt -> Site {i}: {dist_base:.0f} km → {dist_ajustee:.2f} km")
    
    # Visualiser le graphe personnalisé
    print("\nVisualisation du graphe personnalisé...")
    graphe_custom.visualiser()
    
    
    # ========================================================================
    # EXEMPLE 3 : Test de la contrainte de retour au dépôt
    # ========================================================================
    print("\n" + "="*70)
    print("EXEMPLE 3 : Test de la contrainte 'peut revenir au dépôt'")
    print("="*70)
    
    # Simuler une situation en cours de tournée
    site_actuel = 3
    carburant_restant = 100  # litres
    charge_restante = 4000   # kg (on a déjà livré 2 sites)
    
    print(f"\nSituation actuelle:")
    print(f"  - Position: Site {site_actuel}")
    print(f"  - Carburant restant: {carburant_restant} L")
    print(f"  - Charge restante: {charge_restante} kg")
    
    peut_revenir = graphe_auto.peut_revenir_au_depot(
        site_actuel, 
        carburant_restant, 
        charge_restante
    )
    
    distance_retour = graphe_auto.distance_ajustee(site_actuel, 0)
    poids_actuel = camion.poids_actuel(charge_restante)
    conso_necessaire = graphe_auto.consommation_carburant(distance_retour, poids_actuel)
    
    print(f"\nCalculs pour le retour:")
    print(f"  - Distance jusqu'au dépôt: {distance_retour:.2f} km")
    print(f"  - Poids actuel du camion: {poids_actuel:.0f} kg")
    print(f"  - Consommation nécessaire: {conso_necessaire:.2f} L")
    print(f"  - Peut revenir au dépôt? {'✓ OUI' if peut_revenir else '✗ NON (DANGER!)'}")
    
    if peut_revenir:
        marge = carburant_restant - conso_necessaire
        print(f"  - Marge de sécurité: {marge:.2f} L")
    else:
        deficit = conso_necessaire - carburant_restant
        print(f"  - Déficit: {deficit:.2f} L (il manque du carburant!)")
    
    print("\n" + "="*70)
    print("FIN DES EXEMPLES")
    print("="*70)