"""
Base de règles pour le système expert d'orientation académique.
Implémente l'ensemble des règles SI-ALORS pour le raisonnement.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List
from models import (
    NiveauMotivation, NiveauPotentiel, TypeSoutien, NiveauSousComp,
    BaseDeFaits, Etudiant
)


@dataclass
class Regle:
    """
    Classe représentant une règle SI-ALORS.
    
    Attributes:
        id: Identifiant unique de la règle
        description: Description en langage naturel
        condition: Fonction qui évalue la condition (prend BaseDeFaits en argument)
        action: Fonction qui exécute l'action (modifie BaseDeFaits)
        phase: Phase d'exécution (1: motivation, 2: potentiel, 3: orientation)
        priorite: Priorité d'exécution (plus élevé = plus prioritaire)
    """
    id: str
    description: str
    condition: Callable[[BaseDeFaits], bool]
    action: Callable[[BaseDeFaits], None]
    phase: int
    priorite: int = 0


class BaseDeRegles:
    """
    Classe gérant la base de règles du système expert.
    """
    
    def __init__(self):
        """Initialise la base de règles."""
        self.regles: List[Regle] = []
        self._initialiser_regles()
        self._initialiser_regles_phase4()
    
    def _initialiser_regles(self):
        """Initialise les 10 règles essentielles du système."""
        
        # ============================================
        # PHASE 1 : CALCUL DE LA MOTIVATION (R1-R3)
        # ============================================
        
        # R1: Motivation élevée
        self.regles.append(Regle(
            id="R1",
            description="SI attendance_rate >= 80 ET study_hours >= 10 ET homework_completion = oui ALORS motivation = élevée",
            condition=lambda bdf: (
                bdf.etudiant.attendance_rate >= 80
                and bdf.etudiant.study_hours >= 10
                and bdf.etudiant.homework_completion == True
            ),
            action=lambda bdf: bdf.ajouter_fait('motivation_calculee', NiveauMotivation.ELEVEE),
            phase=1,
            priorite=3
        ))
        
        # R2: Motivation moyenne
        self.regles.append(Regle(
            id="R2",
            description="SI attendance_rate entre 60-79 OU study_hours entre 5-9 ALORS motivation = moyenne",
            condition=lambda bdf: (
                (60 <= bdf.etudiant.attendance_rate <= 79)
                or (5 <= bdf.etudiant.study_hours <= 9)
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('motivation_calculee', NiveauMotivation.MOYENNE)
                if bdf.motivation_calculee is None else None
            ),
            phase=1,
            priorite=2
        ))
        
        # R3: Motivation faible
        self.regles.append(Regle(
            id="R3",
            description="SI attendance_rate < 60 OU homework_completion = non ALORS motivation = faible",
            condition=lambda bdf: (
                bdf.etudiant.attendance_rate < 60
                or bdf.etudiant.homework_completion == False
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('motivation_calculee', NiveauMotivation.FAIBLE)
                if bdf.motivation_calculee is None else None
            ),
            phase=1,
            priorite=2
        ))
        
        # ============================================
        # PHASE 2 : CALCUL DU POTENTIEL (R4-R6)
        # ============================================
        
        # R4: Potentiel élevé
        self.regles.append(Regle(
            id="R4",
            description="SI motivation = élevée ET (capacité_travail = élevée OU note_math >= 12 OU note_info >= 12) ALORS potentiel = élevé",
            condition=lambda bdf: (
                bdf.motivation_calculee == NiveauMotivation.ELEVEE
                and (str(bdf.etudiant.capacite_travail.value).lower() == "élevée"
                     or bdf.etudiant.note_math >= 12
                     or bdf.etudiant.note_info >= 12)
            ),
            action=lambda bdf: bdf.ajouter_fait('potentiel', NiveauPotentiel.ELEVE),
            phase=2,
            priorite=3
        ))
        
        # R5: Potentiel moyen
        self.regles.append(Regle(
            id="R5",
            description="SI motivation = moyenne OU (10 <= moyenne < 12 ET participation_score >= 2) ALORS potentiel = moyen",
            condition=lambda bdf: (
                bdf.motivation_calculee == NiveauMotivation.MOYENNE
                or (10 <= bdf.etudiant.moyenne < 12
                    and bdf.etudiant.participation_score >= 2)
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('potentiel', NiveauPotentiel.MOYEN)
                if bdf.potentiel is None else None
            ),
            phase=2,
            priorite=2
        ))
        
        # R6: Potentiel faible
        self.regles.append(Regle(
            id="R6",
            description="SI moyenne < 8 OU (motivation = faible ET capacité_travail = faible) ALORS potentiel = faible",
            condition=lambda bdf: (
                bdf.etudiant.moyenne < 8
                or (bdf.motivation_calculee == NiveauMotivation.FAIBLE
                    and str(bdf.etudiant.capacite_travail.value).lower() == "faible")
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('potentiel', NiveauPotentiel.FAIBLE)
                if bdf.potentiel is None else None
            ),
            phase=2,
            priorite=3
        ))
        
        # ============================================
        # PHASE 3 : ORIENTATION ACADÉMIQUE (R7-R10)
        # ============================================
        
        # R7: Excellente moyenne - filière souhaitée sans soutien
        self.regles.append(Regle(
            id="R7",
            description="SI moyenne >= 14 ALORS orientation = filière_souhaitée ET soutien = non nécessaire",
            condition=lambda bdf: bdf.etudiant.moyenne >= 14,
            action=lambda bdf: (
                bdf.ajouter_fait('orientation', bdf.etudiant.filiere_souhaitee),
                bdf.ajouter_fait('type_soutien', TypeSoutien.NON_NECESSAIRE)
            ),
            phase=3,
            priorite=3
        ))
        
        # R8: Bonne moyenne ou potentiel élevé - filière souhaitée avec soutien
        self.regles.append(Regle(
            id="R8",
            description="SI (12 <= moyenne < 14) OU (moyenne < 12 ET potentiel = élevé ET disponibilité_soutien = oui) ALORS orientation = filière_souhaitée",
            condition=lambda bdf: (
                (12 <= bdf.etudiant.moyenne < 14)
                or (bdf.etudiant.moyenne < 12
                    and bdf.potentiel == NiveauPotentiel.ELEVE
                    and bdf.etudiant.disponibilite_soutien == True)
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('orientation', bdf.etudiant.filiere_souhaitee),
                bdf.ajouter_fait('type_soutien', TypeSoutien.OBLIGATOIRE if bdf.etudiant.moyenne < 12 else TypeSoutien.FACULTATIF)
            ),
            phase=3,
            priorite=3
        ))
        
        # R9: Potentiel moyen - soutien personnalisé
        self.regles.append(Regle(
            id="R9",
            description="SI potentiel = moyen ET 10 <= moyenne < 12 ALORS orientation = filière_souhaitée ET soutien = personnalisé",
            condition=lambda bdf: (
                bdf.potentiel == NiveauPotentiel.MOYEN
                and 10 <= bdf.etudiant.moyenne < 12
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('orientation', bdf.etudiant.filiere_souhaitee),
                bdf.ajouter_fait('type_soutien', TypeSoutien.SOUTIEN_PERSONNALISE)
            ),
            phase=3,
            priorite=2
        ))
        
        # R10: Soutiens spécifiques selon la filière et les lacunes
        # R10a: Informatique + faible math → remise à niveau math
        self.regles.append(Regle(
            id="R10",
            description="SI filière = Informatique ET note_math < 10 ALORS soutien += remise à niveau en mathématiques",
            condition=lambda bdf: (
                bdf.etudiant.filiere_souhaitee.lower() == "informatique"
                and bdf.etudiant.note_math < 10
            ),
            action=lambda bdf: (
                bdf.soutiens_complements.append("Remise à niveau en mathématiques")
                if "Remise à niveau en mathématiques" not in bdf.soutiens_complements else None
            ),
            phase=3,
            priorite=2
        ))
        
        # R10b: Informatique + faible info → cours de programmation
        self.regles.append(Regle(
            id="R10b",
            description="SI filière = Informatique ET note_info < 10 ALORS soutien += cours de programmation",
            condition=lambda bdf: (
                bdf.etudiant.filiere_souhaitee.lower() == "informatique"
                and bdf.etudiant.note_info < 10
            ),
            action=lambda bdf: (
                bdf.soutiens_complements.append("Cours de programmation intensif")
                if "Cours de programmation intensif" not in bdf.soutiens_complements else None
            ),
            phase=3,
            priorite=2
        ))
        
        # R10c: Potentiel faible + moyenne < 10 → filière moins exigeante
        self.regles.append(Regle(
            id="R10c",
            description="SI moyenne < 10 ET potentiel = faible ALORS orientation = filière moins exigeante ET soutien = accompagnement renforcé",
            condition=lambda bdf: (
                bdf.etudiant.moyenne < 10
                and bdf.potentiel == NiveauPotentiel.FAIBLE
            ),
            action=lambda bdf: (
                bdf.ajouter_fait('orientation', "Filière moins exigeante"),
                bdf.ajouter_fait('type_soutien', TypeSoutien.ACCOMPAGNEMENT_RENFORCE)
            ),
            phase=3,
            priorite=3
        ))
    
    def _initialiser_regles_phase4(self):
        """
        Phase 4 — Diagnostic détaillé des sous-compétences informatiques.
        Règles R11-R16 : activées quand filière = Informatique ET note_info < 12.
        Chaque règle identifie précisément le type de lacune et ajoute un
        conseil ciblé dans bdf.diagnostic_info.
        """

        def _is_info(bdf):
            return bdf.etudiant.filiere_souhaitee.lower() == "informatique"

        def _pi(bdf):
            return bdf.etudiant.profil_info

        # ------------------------------------------------------------------ #
        # R11 — Lacune en logique algorithmique (et ne peut pas coder non plus)
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R11",
            description=(
                "SI filière=Informatique ET note_algo < 10 ET note_programmation < 10 "
                "ALORS diagnostic: lacune profonde en algorithmique et programmation "
                "→ remise à niveau fondamentaux"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and _pi(bdf).note_algo is not None
                and _pi(bdf).note_programmation is not None
                and _pi(bdf).note_algo < 10
                and _pi(bdf).note_programmation < 10
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "🔴 Ni la logique algorithmique ni l'écriture de code ne sont maîtrisées "
                    "→ Parcours de remise à niveau complet (algorithmique + programmation)"
                )
                if "R11" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=5
        ))

        # ------------------------------------------------------------------ #
        # R12 — Comprend le code mais ne peut pas écrire (syntaxe / débogage)
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R12",
            description=(
                "SI filière=Informatique ET note_lecture_code >= 10 ET note_programmation < 10 "
                "ALORS diagnostic: comprend le code mais lacune en écriture "
                "→ atelier syntaxe et débogage"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and _pi(bdf).note_lecture_code is not None
                and _pi(bdf).note_programmation is not None
                and _pi(bdf).note_lecture_code >= 10
                and _pi(bdf).note_programmation < 10
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "🟠 L'étudiant comprend le code existant mais ne sait pas l'écrire "
                    "→ Atelier pratique : syntaxe, débogage et écriture autonome"
                )
                if "R12" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=4
        ))

        # ------------------------------------------------------------------ #
        # R13 — Peut écrire du code mais logique algorithmique insuffisante
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R13",
            description=(
                "SI filière=Informatique ET note_programmation >= 10 ET note_algo < 10 "
                "ALORS diagnostic: sait coder mais la logique de conception manque "
                "→ renforcement algorithmique"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and _pi(bdf).note_programmation is not None
                and _pi(bdf).note_algo is not None
                and _pi(bdf).note_programmation >= 10
                and _pi(bdf).note_algo < 10
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "🟠 L'étudiant sait écrire du code mais manque de logique algorithmique "
                    "→ Cours de conception algorithmique et résolution de problèmes"
                )
                if "R13" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=4
        ))

        # ------------------------------------------------------------------ #
        # R14 — Lacune en structures de données
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R14",
            description=(
                "SI filière=Informatique ET note_structures < 10 "
                "ALORS diagnostic: structures de données insuffisantes "
                "→ cours dédié (listes, piles, arbres, graphes)"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and _pi(bdf).note_structures is not None
                and _pi(bdf).note_structures < 10
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "🟡 Lacune en structures de données "
                    "→ Cours : listes chaînées, piles, files, arbres, graphes"
                )
                if "R14" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=3
        ))

        # ------------------------------------------------------------------ #
        # R15 — Lacune en bases de données / SQL
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R15",
            description=(
                "SI filière=Informatique ET note_bdd < 10 "
                "ALORS diagnostic: lacune bases de données → initiation SQL et modélisation"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and _pi(bdf).note_bdd is not None
                and _pi(bdf).note_bdd < 10
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "🟡 Lacune en bases de données "
                    "→ Atelier SQL et modélisation relationnelle"
                )
                if "R15" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=3
        ))

        # ------------------------------------------------------------------ #
        # R16 — Toutes les sous-compétences évaluées sont bonnes → profil solide
        # ------------------------------------------------------------------ #
        self.regles.append(Regle(
            id="R16",
            description=(
                "SI filière=Informatique ET toutes notes sous-compétences >= 12 "
                "ALORS diagnostic: profil informatique solide, pas de soutien spécifique requis"
            ),
            condition=lambda bdf: (
                _is_info(bdf)
                and all(
                    v >= 12
                    for v in _pi(bdf).as_dict().values()
                    if v is not None
                )
                and any(v is not None for v in _pi(bdf).as_dict().values())
            ),
            action=lambda bdf: (
                bdf.diagnostic_info.append(
                    "✅ Profil informatique solide : toutes les sous-compétences évaluées "
                    "sont satisfaisantes — aucun soutien spécifique requis"
                )
                if "R16" not in [d[:3] for d in bdf.diagnostic_info] else None
            ),
            phase=4,
            priorite=2
        ))

    def obtenir_regles_phase(self, phase: int) -> List[Regle]:
        return [r for r in self.regles if r.phase == phase]
    
    def obtenir_regles_triees(self) -> List[Regle]:
        """Retourne toutes les règles triées par priorité et phase."""
        return sorted(self.regles, key=lambda r: (r.phase, -r.priorite))
    
    def afficher_regles(self, phase: int = None):
        """Affiche les règles."""
        if phase:
            regles = self.obtenir_regles_phase(phase)
            print(f"\n📋 RÈGLES DE PHASE {phase}:")
        else:
            regles = self.regles
            print(f"\n📋 TOUTES LES RÈGLES ({len(regles)} total):")
        
        for regle in regles:
            print(f"\n  {regle.id}: {regle.description}")
            print(f"      Phase: {regle.phase}, Priorité: {regle.priorite}")
