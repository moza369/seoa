"""
Système de recommandation de soutien pédagogique.
Gère les dispositifs de soutien adaptés au profil de l'étudiant.
"""

from typing import List, Dict
from models import Etudiant, NiveauMotivation, NiveauPotentiel, TypeSoutien


class DisposifSoutien:
    """
    Classe représentant un dispositif de soutien pédagogique.
    
    Attributes:
        id: Identifiant du dispositif
        nom: Nom du dispositif
        description: Description détaillée
        duree: Durée estimée (en semaines)
        frequence: Fréquence (h/semaine)
        public_cible: Description du profil cible
    """
    
    def __init__(self, id: str, nom: str, description: str, 
                 duree: int, frequence: float, public_cible: str):
        self.id = id
        self.nom = nom
        self.description = description
        self.duree = duree
        self.frequence = frequence
        self.public_cible = public_cible
    
    def __repr__(self):
        return f"DisposifSoutien({self.nom}, {self.duree}w, {self.frequence}h/w)"


class SystemeDeSoutien:
    """
    Système de gestion des dispositifs de soutien pédagogique.
    Recommande les soutiens adaptés en fonction du profil de l'étudiant.
    """
    
    def __init__(self):
        """Initialise le système de soutien avec les dispositifs disponibles."""
        self.dispositifs: Dict[str, DisposifSoutien] = {}
        self._initialiser_dispositifs()
    
    def _initialiser_dispositifs(self):
        """Initialise la base de dispositifs de soutien disponibles."""
        
        # Soutiens généraux
        self.dispositifs['remise_math'] = DisposifSoutien(
            id='remise_math',
            nom='Remise à niveau en mathématiques',
            description='Cours intensif couvrant les fondamentaux des mathématiques '
                       'avec pratique sur des exercices pertinents.',
            duree=12,
            frequence=3.0,
            public_cible='Étudiants avec note < 10 en mathématiques'
        )
        
        self.dispositifs['prog'] = DisposifSoutien(
            id='prog',
            nom='Cours de programmation intensif',
            description='Atelier pratique de programmation (Python/Java) avec '
                       'projets progressifs et mentoring.',
            duree=8,
            frequence=4.0,
            public_cible='Étudiants spécialisés en informatique avec difficultés'
        )
        
        self.dispositifs['tutorat'] = DisposifSoutien(
            id='tutorat',
            nom='Tutorat par pairs',
            description='Sessions de tutorat hebdomadaires avec des étudiants '
                       'plus avancés pour renforcer la compréhension.',
            duree=16,
            frequence=2.0,
            public_cible='Tous les étudiants ayant besoin de soutien personnalisé'
        )
        
        self.dispositifs['accompagnement'] = DisposifSoutien(
            id='accompagnement',
            nom='Accompagnement renforcé',
            description='Suivi intensif avec un mentor dédié incluant orientation '
                       'académique, gestion du temps et soutien psychologique.',
            duree=24,
            frequence=5.0,
            public_cible='Étudiants en difficulté majeure ou à risque d\'abandon'
        )
        
        self.dispositifs['organisation'] = DisposifSoutien(
            id='organisation',
            nom='Aide à l\'organisation et planification',
            description='Ateliers et coaching sur la gestion du temps, l\'organisation '
                       'du travail personnel et les méthodes d\'étude efficaces.',
            duree=6,
            frequence=2.0,
            public_cible='Étudiants avec faible nombre d\'heures d\'étude'
        )
        
        self.dispositifs['participation'] = DisposifSoutien(
            id='participation',
            nom='Programme de leadership académique',
            description='Préparation pour devenir tuteur pair, présentations et '
                       'animation de sessions d\'étude collectives.',
            duree=12,
            frequence=2.0,
            public_cible='Étudiants excellents avec forte participation'
        )
        
        self.dispositifs['personnalise'] = DisposifSoutien(
            id='personnalise',
            nom='Soutien personnalisé adaptatif',
            description='Plans d\'étude individualisés ajustés régulièrement en '
                       'fonction de la progression de l\'étudiant.',
            duree=20,
            frequence=3.0,
            public_cible='Étudiants ayant besoin d\'un parcours sur mesure'
        )
    
    def recommander_soutiens(self, etudiant: Etudiant, 
                           motivation: NiveauMotivation,
                           potentiel: NiveauPotentiel) -> List[DisposifSoutien]:
        """
        Recommande les dispositifs de soutien adaptés au profil de l'étudiant.
        
        Args:
            etudiant: Objet Étudiant
            motivation: Niveau de motivation calculé
            potentiel: Niveau de potentiel académique
            
        Returns:
            Liste de dispositifs recommandés
        """
        recommandations = []
        
        # Recommandations basées sur la filière et les notes
        if etudiant.filiere_souhaitee.lower() == "informatique":
            if etudiant.note_math < 10:
                recommandations.append(self.dispositifs['remise_math'])
            if etudiant.note_info < 10:
                recommandations.append(self.dispositifs['prog'])
        
        # Recommandations basées sur la motivation et le potentiel
        if motivation == NiveauMotivation.FAIBLE or potentiel == NiveauPotentiel.FAIBLE:
            if etudiant.moyenne < 10:
                recommandations.append(self.dispositifs['accompagnement'])
            else:
                recommandations.append(self.dispositifs['personnalise'])
        
        elif motivation == NiveauMotivation.MOYENNE:
            if etudiant.study_hours < 5:
                recommandations.append(self.dispositifs['organisation'])
            recommandations.append(self.dispositifs['tutorat'])
        
        # Recommandations pour étudiants excellents
        if motivation == NiveauMotivation.ELEVEE and etudiant.participation_score >= 4:
            recommandations.append(self.dispositifs['participation'])
        
        # Recommandations basées sur les heures d'étude
        if etudiant.study_hours < 3:
            if self.dispositifs['organisation'] not in recommandations:
                recommandations.append(self.dispositifs['organisation'])
        
        # Éviter les doublons
        recommandations = list(dict.fromkeys(recommandations))
        
        return recommandations
    
    def generer_plan_soutien(self, etudiant: Etudiant,
                           dispositifs: List[DisposifSoutien]) -> str:
        """
        Génère un plan de soutien détaillé pour l'étudiant.
        
        Args:
            etudiant: Objet Étudiant
            dispositifs: Liste des dispositifs recommandés
            
        Returns:
            Une chaîne formatée décrivant le plan de soutien
        """
        plan = f"\n{'='*70}\n"
        plan += f"PLAN DE SOUTIEN PÉDAGOGIQUE - {etudiant.prenom} {etudiant.nom}\n"
        plan += f"{'='*70}\n\n"
        
        if not dispositifs:
            plan += "Aucun soutien particulier n'est nécessaire.\n"
            plan += "L'étudiant est en position favorable pour réussir autonomement.\n"
        else:
            plan += f"Nombre de dispositifs recommandés: {len(dispositifs)}\n"
            plan += f"Charge totale estimée: {sum(d.frequence for d in dispositifs):.1f}h/semaine\n"
            plan += f"Durée totale estimée: {max(d.duree for d in dispositifs)} semaines\n\n"
            
            plan += "DISPOSITIFS RECOMMANDÉS:\n"
            plan += "-" * 70 + "\n\n"
            
            for i, dispositif in enumerate(dispositifs, 1):
                plan += f"{i}. {dispositif.nom.upper()}\n"
                plan += f"   ID: {dispositif.id}\n"
                plan += f"   Description: {dispositif.description}\n"
                plan += f"   Durée: {dispositif.duree} semaines\n"
                plan += f"   Fréquence: {dispositif.frequence} h/semaine\n"
                plan += f"   Public cible: {dispositif.public_cible}\n\n"
        
        plan += "=" * 70 + "\n"
        return plan
    
    def afficher_catalogue_dispositifs(self):
        """Affiche le catalogue complet des dispositifs disponibles."""
        print("\n" + "="*70)
        print("CATALOGUE DES DISPOSITIFS DE SOUTIEN PÉDAGOGIQUE")
        print("="*70 + "\n")
        
        for i, (key, dispositif) in enumerate(self.dispositifs.items(), 1):
            print(f"{i}. {dispositif.nom}")
            print(f"   ID: {dispositif.id}")
            print(f"   Description: {dispositif.description}")
            print(f"   Durée: {dispositif.duree} semaines | Fréquence: {dispositif.frequence} h/semaine")
            print(f"   Public cible: {dispositif.public_cible}\n")
        
        print("=" * 70 + "\n")
