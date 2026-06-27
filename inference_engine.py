"""
Moteur d'inférence pour le système expert.
Implémente le chaînage avant pour le raisonnement automatisé.
"""

from typing import List, Set
from models import BaseDeFaits, ResultatOrientation, TypeSoutien, NiveauMotivation
from rules import BaseDeRegles, Regle


class MoteurInference:
    """
    Moteur d'inférence utilisant le chaînage avant (forward chaining).
    
    Applique itérativement les règles jusqu'à ce qu'aucune nouvelle
    conclusion ne soit générée (point fixe).
    """
    
    def __init__(self):
        """Initialise le moteur d'inférence."""
        self.base_regles = BaseDeRegles()
        self.historique_inferences = []
        self.regles_appliquees = []
    
    def raisonner(self, base_de_faits: BaseDeFaits) -> ResultatOrientation:
        """
        Effectue le raisonnement en chaînage avant.
        
        Args:
            base_de_faits: La base de faits initiale avec les données de l'étudiant
            
        Returns:
            Un objet ResultatOrientation contenant les conclusions
        """
        self.historique_inferences = []
        self.regles_appliquees = []
        
        print("\n" + "="*70)
        print("DÉBUT DU RAISONNEMENT - CHAÎNAGE AVANT")
        print("="*70)
        
        # Phase 1: Calcul de la motivation
        print("\n🔵 PHASE 1: CALCUL DE LA MOTIVATION")
        print("-" * 70)
        self._appliquer_phase(base_de_faits, 1)
        
        # Phase 2: Calcul du potentiel
        print("\n🟢 PHASE 2: CALCUL DU POTENTIEL")
        print("-" * 70)
        self._appliquer_phase(base_de_faits, 2)
        
        # Phase 3: Orientation académique
        print("\n🔴 PHASE 3: ORIENTATION ACADÉMIQUE")
        print("-" * 70)
        self._appliquer_phase(base_de_faits, 3)

        # Phase 4: Diagnostic CS (uniquement pour les étudiants Informatique)
        if base_de_faits.etudiant.filiere_souhaitee.lower() == "informatique":
            has_data = any(
                v is not None
                for v in base_de_faits.etudiant.profil_info.as_dict().values()
            )
            if has_data:
                print("\n🟣 PHASE 4: DIAGNOSTIC INFORMATIQUE")
                print("-" * 70)
                self._appliquer_phase(base_de_faits, 4)
        
        # Génération du résultat
        print("\n" + "="*70)
        print("GÉNÉRATION DU RÉSULTAT FINAL")
        print("="*70)
        
        resultat = self._generer_resultat(base_de_faits)
        
        return resultat
    
    def _appliquer_phase(self, base_de_faits: BaseDeFaits, num_phase: int):
        """
        Applique toutes les règles d'une phase en chaînage avant.
        Chaque règle ne peut être déclenchée qu'une seule fois (point fixe).
        
        Args:
            base_de_faits: La base de faits courante
            num_phase: Le numéro de la phase à appliquer
        """
        regles_phase = self.base_regles.obtenir_regles_phase(num_phase)
        regles_phase = sorted(regles_phase, key=lambda r: -r.priorite)
        
        regles_deja_appliquees: Set[str] = set()
        
        while True:
            nouvelle_regle_appliquee = False
            
            for regle in regles_phase:
                # Une règle ne peut se déclencher qu'une seule fois
                if regle.id in regles_deja_appliquees:
                    continue
                
                try:
                    if regle.condition(base_de_faits):
                        regle.action(base_de_faits)
                        regles_deja_appliquees.add(regle.id)
                        self.regles_appliquees.append(regle.id)
                        nouvelle_regle_appliquee = True
                        print(f"  ✓ {regle.id} appliquée: {regle.description}")
                        self._log_inference(regle, base_de_faits)
                except Exception as e:
                    print(f"  ⚠ Erreur lors de l'application de {regle.id}: {e}")
            
            # Point fixe atteint : aucune nouvelle règle déclenchée
            if not nouvelle_regle_appliquee:
                print(f"  → Point fixe atteint ({len(regles_deja_appliquees)} règle(s) appliquée(s))")
                break
        
        # Affichage de l'état après la phase
        if num_phase == 1:
            val = base_de_faits.motivation_calculee.value if base_de_faits.motivation_calculee else 'Non déterminée'
            print(f"  📊 Résultat Phase 1 → Motivation = {val}")
        elif num_phase == 2:
            val = base_de_faits.potentiel.value if base_de_faits.potentiel else 'Non déterminé'
            print(f"  📊 Résultat Phase 2 → Potentiel = {val}")
        elif num_phase == 3:
            o = base_de_faits.orientation or 'Non déterminée'
            s = base_de_faits.type_soutien.value if base_de_faits.type_soutien else 'Non déterminé'
            print(f"  📊 Résultat Phase 3 → Orientation = {o}")
            print(f"  📊 Soutien principal = {s}")
        elif num_phase == 4:
            n = len(base_de_faits.diagnostic_info)
            print(f"  📊 Résultat Phase 4 → {n} diagnostic(s) généré(s)")
    
    def _log_inference(self, regle: Regle, base_de_faits: BaseDeFaits):
        """Enregistre une inférence dans l'historique."""
        self.historique_inferences.append({
            'regle_id': regle.id,
            'description': regle.description,
            'motivation': base_de_faits.motivation_calculee,
            'potentiel': base_de_faits.potentiel,
            'orientation': base_de_faits.orientation,
            'type_soutien': base_de_faits.type_soutien
        })
    
    def _generer_resultat(self, base_de_faits: BaseDeFaits) -> ResultatOrientation:
        """
        Génère le résultat final de l'orientation.
        
        Args:
            base_de_faits: La base de faits avec toutes les conclusions
            
        Returns:
            Un objet ResultatOrientation
        """
        # Déterminer la confiance du système (basée sur la complétude des conclusions)
        confiance = 0.8  # Base
        
        if base_de_faits.motivation_calculee and base_de_faits.potentiel and base_de_faits.orientation:
            confiance = 0.95
        elif base_de_faits.motivation_calculee and base_de_faits.orientation:
            confiance = 0.85
        else:
            confiance = 0.7
        
        # Générer la justification
        justification = self._generer_justification(base_de_faits)
        
        # Déterminer les soutiens complémentaires
        soutiens = []
        if base_de_faits.soutiens_complements:
            soutiens = base_de_faits.soutiens_complements
        
        # Type de soutien principal
        type_soutien = (base_de_faits.type_soutien.value 
                       if base_de_faits.type_soutien 
                       else "À déterminer")
        
        resultat = ResultatOrientation(
            etudiant_id=base_de_faits.etudiant.id,
            etudiant_nom=f"{base_de_faits.etudiant.prenom} {base_de_faits.etudiant.nom}",
            filiere_recommandee=base_de_faits.orientation or "À déterminer",
            type_soutien_principal=type_soutien,
            soutiens_complements=soutiens,
            diagnostic_info=base_de_faits.diagnostic_info,
            justification=justification,
            motivation_calculee=base_de_faits.motivation_calculee.value if base_de_faits.motivation_calculee else "Non déterminée",
            potentiel=base_de_faits.potentiel.value if base_de_faits.potentiel else "Non déterminé",
            confiance=confiance
        )
        
        return resultat
    
    def _generer_justification(self, base_de_faits: BaseDeFaits) -> str:
        """
        Génère une justification textuelle de la décision.
        
        Args:
            base_de_faits: La base de faits avec les conclusions
            
        Returns:
            Une chaîne de caractères justifiant la décision
        """
        justification = []
        etudiant = base_de_faits.etudiant
        
        # Analyse de la motivation
        if base_de_faits.motivation_calculee:
            if base_de_faits.motivation_calculee == NiveauMotivation.ELEVEE:
                justification.append(
                    f"L'étudiant démontre une motivation élevée: taux de "
                    f"présence de {etudiant.attendance_rate}%, {etudiant.study_hours}h d'étude/semaine, "
                    f"et une bonne complétude des devoirs."
                )
            elif base_de_faits.motivation_calculee == NiveauMotivation.MOYENNE:
                justification.append(
                    f"L'étudiant montre une motivation moyenne: taux de présence "
                    f"de {etudiant.attendance_rate}%, {etudiant.study_hours}h d'étude/semaine."
                )
            else:
                justification.append(
                    f"La motivation de l'étudiant est faible: taux de présence "
                    f"de {etudiant.attendance_rate}%, seulement {etudiant.study_hours}h d'étude/semaine."
                )
        
        # Analyse du potentiel
        if base_de_faits.potentiel:
            justification.append(
                f"Son potentiel académique est évalué comme {base_de_faits.potentiel.value}, "
                f"basé sur sa motivation et sa capacité de travail ({etudiant.capacite_travail.value})."
            )
        
        # Analyse de la moyenne
        justification.append(
            f"Avec une moyenne générale de {etudiant.moyenne}/20 "
            f"(Math: {etudiant.note_math}, Info: {etudiant.note_info}), "
        )
        
        # Recommandation
        if base_de_faits.orientation:
            justification.append(
                f"l'étudiant est orienté vers {base_de_faits.orientation}."
            )
        
        # Soutien
        if base_de_faits.type_soutien:
            justification.append(
                f"Un soutien {base_de_faits.type_soutien.value} est recommandé."
            )
        
        # Soutiens complémentaires
        if base_de_faits.soutiens_complements:
            supports = ", ".join(base_de_faits.soutiens_complements)
            justification.append(f"Soutiens complémentaires: {supports}.")

        # Diagnostic CS
        if base_de_faits.diagnostic_info:
            justification.append(
                f"Diagnostic informatique ({len(base_de_faits.diagnostic_info)} point(s)): "
                + " | ".join(base_de_faits.diagnostic_info)
            )

        return " ".join(justification)
    
    def afficher_historique(self):
        """Affiche l'historique complet du raisonnement."""
        print("\n" + "="*70)
        print("HISTORIQUE COMPLET DU RAISONNEMENT")
        print("="*70)
        
        for i, inference in enumerate(self.historique_inferences, 1):
            print(f"\nÉtape {i}: {inference['regle_id']}")
            print(f"  Motivation: {inference['motivation'].value if inference['motivation'] else 'N/A'}")
            print(f"  Potentiel: {inference['potentiel'].value if inference['potentiel'] else 'N/A'}")
            print(f"  Orientation: {inference['orientation'] or 'N/A'}")
            print(f"  Soutien: {inference['type_soutien'].value if inference['type_soutien'] else 'N/A'}")
        
        print("\n" + "="*70)
        print(f"RÈGLES APPLIQUÉES: {', '.join(self.regles_appliquees)}")
        print("="*70 + "\n")
