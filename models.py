"""
Modèles de données pour le système expert d'orientation académique.
Définit les structures et classes pour les étudiants, enseignants et résultats.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class NiveauMotivation(Enum):
    ELEVEE = "élevée"
    MOYENNE = "moyenne"
    FAIBLE = "faible"


class NiveauPotentiel(Enum):
    ELEVE = "élevé"
    MOYEN = "moyen"
    FAIBLE = "faible"


class TypeSoutien(Enum):
    NON_NECESSAIRE    = "non nécessaire"
    FACULTATIF        = "facultatif"
    OBLIGATOIRE       = "obligatoire"
    ACCOMPAGNEMENT_RENFORCE = "accompagnement renforcé"
    SOUTIEN_PERSONNALISE    = "soutien personnalisé"


class NiveauCapacite(Enum):
    ELEVEE  = "élevée"
    MOYENNE = "moyenne"
    FAIBLE  = "faible"


# ─── Sous-compétences informatique ───────────────────────────────────────────
class NiveauSousComp(Enum):
    """Niveau dans une sous-compétence spécifique (0-20 converti en niveau)."""
    BON     = "bon"       # >= 12
    MOYEN   = "moyen"     # 8-11
    FAIBLE  = "faible"    # < 8


@dataclass
class ProfilInformatique:
    """
    Profil détaillé des sous-compétences en informatique.
    Permet un diagnostic précis de la lacune de l'étudiant.

    Chaque note est sur 20. Si la filière n'est pas Informatique,
    tous les champs peuvent rester à None.
    
    Sous-compétences:
        note_algo        : Algorithmique (conception, pseudo-code, logique)
        note_programmation: Écriture de code (syntaxe, débogage, implémentation)
        note_lecture_code : Lecture et compréhension de code existant
        note_structures   : Structures de données (listes, piles, arbres…)
        note_bdd          : Bases de données / SQL
        note_reseau       : Réseaux / systèmes
    """
    note_algo:         Optional[float] = None
    note_programmation:Optional[float] = None
    note_lecture_code: Optional[float] = None
    note_structures:   Optional[float] = None
    note_bdd:          Optional[float] = None
    note_reseau:       Optional[float] = None

    def niveau(self, note: Optional[float]) -> Optional[NiveauSousComp]:
        if note is None:
            return None
        if note >= 12:
            return NiveauSousComp.BON
        if note >= 8:
            return NiveauSousComp.MOYEN
        return NiveauSousComp.FAIBLE

    @property
    def lacunes(self) -> List[str]:
        """Retourne la liste des sous-compétences en difficulté (note < 10)."""
        champs = {
            "Algorithmique":              self.note_algo,
            "Programmation (écriture)":   self.note_programmation,
            "Lecture de code":            self.note_lecture_code,
            "Structures de données":      self.note_structures,
            "Bases de données":           self.note_bdd,
            "Réseaux / Systèmes":         self.note_reseau,
        }
        return [nom for nom, note in champs.items() if note is not None and note < 10]

    @property
    def points_forts(self) -> List[str]:
        """Retourne les sous-compétences maîtrisées (note >= 12)."""
        champs = {
            "Algorithmique":              self.note_algo,
            "Programmation (écriture)":   self.note_programmation,
            "Lecture de code":            self.note_lecture_code,
            "Structures de données":      self.note_structures,
            "Bases de données":           self.note_bdd,
            "Réseaux / Systèmes":         self.note_reseau,
        }
        return [nom for nom, note in champs.items() if note is not None and note >= 12]

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "Algorithmique":            self.note_algo,
            "Programmation":            self.note_programmation,
            "Lecture de code":          self.note_lecture_code,
            "Structures de données":    self.note_structures,
            "Bases de données":         self.note_bdd,
            "Réseaux / Systèmes":       self.note_reseau,
        }


@dataclass
class Etudiant:
    """
    Classe représentant un étudiant avec ses données académiques,
    comportementales et ses sous-compétences en informatique.
    """
    id:                  str
    nom:                 str
    prenom:              str
    moyenne:             float
    note_math:           float
    note_info:           float
    filiere_souhaitee:   str
    attendance_rate:     float
    study_hours:         float
    homework_completion: bool
    participation_score: int
    capacite_travail:    NiveauCapacite
    disponibilite_soutien: bool
    # Profil détaillé info (optionnel, renseigné si filière = Informatique)
    profil_info: ProfilInformatique = field(default_factory=ProfilInformatique)

    def __repr__(self):
        return f"Étudiant({self.prenom} {self.nom}, moyenne={self.moyenne})"


@dataclass
class BaseDeFaits:
    """Base de faits du moteur d'inférence."""
    etudiant: Etudiant

    motivation_calculee:  Optional[NiveauMotivation] = None
    potentiel:            Optional[NiveauPotentiel]  = None
    orientation:          Optional[str]              = None
    type_soutien:         Optional[TypeSoutien]      = None
    soutiens_complements: List[str]                  = field(default_factory=list)
    # Diagnostic détaillé par sous-compétence (Phase 4)
    diagnostic_info:      List[str]                  = field(default_factory=list)

    def ajouter_fait(self, key: str, value):
        setattr(self, key, value)

    def obtenir_fait(self, key: str):
        return getattr(self, key, None)

    def afficher_etat(self):
        print("\n" + "="*60)
        print("ÉTAT ACTUEL DE LA BASE DE FAITS")
        print("="*60)
        e = self.etudiant
        print(f"Étudiant : {e.prenom} {e.nom}")
        print(f"  Moyenne: {e.moyenne}  |  Math: {e.note_math}  |  Info: {e.note_info}")
        print(f"  Présence: {e.attendance_rate}%  |  Étude: {e.study_hours}h/sem")
        print(f"  Devoirs: {e.homework_completion}  |  Participation: {e.participation_score}/5")
        print(f"  Capacité: {e.capacite_travail.value}")
        if e.profil_info:
            d = e.profil_info.as_dict()
            renseignees = {k: v for k, v in d.items() if v is not None}
            if renseignees:
                print("\n  Sous-compétences info:")
                for k, v in renseignees.items():
                    print(f"    {k}: {v}/20")
        print("\nFaits calculés:")
        print(f"  Motivation : {self.motivation_calculee.value if self.motivation_calculee else '—'}")
        print(f"  Potentiel  : {self.potentiel.value if self.potentiel else '—'}")
        print(f"  Orientation: {self.orientation or '—'}")
        print(f"  Soutien    : {self.type_soutien.value if self.type_soutien else '—'}")
        if self.soutiens_complements:
            for s in self.soutiens_complements:
                print(f"    • {s}")
        if self.diagnostic_info:
            print("\n  Diagnostic info:")
            for d in self.diagnostic_info:
                print(f"    • {d}")
        print("="*60 + "\n")


@dataclass
class ResultatOrientation:
    """Résultat final de l'orientation académique."""
    etudiant_id:           str
    etudiant_nom:          str
    filiere_recommandee:   str
    type_soutien_principal:str
    soutiens_complements:  List[str]
    diagnostic_info:       List[str]
    justification:         str
    motivation_calculee:   str
    potentiel:             str
    confiance:             float

    def afficher_resultat(self):
        print("\n" + "█"*70)
        print("█" + "RÉSULTAT FINAL DE L'ORIENTATION ACADÉMIQUE".center(68) + "█")
        print("█"*70)
        print(f"\n  Étudiant : {self.etudiant_nom}  (ID: {self.etudiant_id})")
        print(f"  Filière  : {self.filiere_recommandee}")
        print(f"  Motivation: {self.motivation_calculee}  |  Potentiel: {self.potentiel}")
        print(f"  Confiance : {self.confiance*100:.1f}%")
        print(f"\n  Soutien principal: {self.type_soutien_principal}")
        if self.soutiens_complements:
            for s in self.soutiens_complements:
                print(f"    • {s}")
        if self.diagnostic_info:
            print("\n  Diagnostic détaillé:")
            for d in self.diagnostic_info:
                print(f"    → {d}")
        print(f"\n  Justification: {self.justification}")
        print("█"*70 + "\n")

    def exporter_json(self):
        return {
            'etudiant_id':            self.etudiant_id,
            'etudiant_nom':           self.etudiant_nom,
            'filiere_recommandee':    self.filiere_recommandee,
            'type_soutien_principal': self.type_soutien_principal,
            'soutiens_complements':   self.soutiens_complements,
            'diagnostic_info':        self.diagnostic_info,
            'justification':          self.justification,
            'motivation_calculee':    self.motivation_calculee,
            'potentiel':              self.potentiel,
            'confiance':              self.confiance,
        }
