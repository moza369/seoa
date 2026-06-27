"""
Application principale du système expert d'orientation académique.
Interface utilisateur pour l'interaction avec le système.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from models import (
    Etudiant, BaseDeFaits, NiveauCapacite, ResultatOrientation
)
from inference_engine import MoteurInference
from support_system import SystemeDeSoutien


class SystemeExpertOrientationAcademique:
    """
    Classe principale du système expert.
    Orchestre le flux d'exécution du système d'orientation académique.
    """
    
    def __init__(self):
        """Initialise le système expert."""
        self.moteur = MoteurInference()
        self.systeme_soutien = SystemeDeSoutien()
        self.resultats = []
        self.rapport_path = Path("rapports")
        self.rapport_path.mkdir(exist_ok=True)
    
    def analyser_etudiant(self, etudiant: Etudiant) -> ResultatOrientation:
        """
        Analyse un étudiant et génère une recommandation d'orientation.
        
        Args:
            etudiant: Objet Étudiant contenant les données
            
        Returns:
            Objet ResultatOrientation avec la décision du système
        """
        # Créer la base de faits
        base_de_faits = BaseDeFaits(etudiant=etudiant)
        
        # Afficher l'état initial
        print("\n" + "█"*70)
        print("█" + "SYSTÈME EXPERT D'ORIENTATION ACADÉMIQUE".center(68) + "█")
        print("█" + f"Analyse de {etudiant.prenom} {etudiant.nom}".center(68) + "█")
        print("█"*70)
        
        base_de_faits.afficher_etat()
        
        # Effectuer le raisonnement
        resultat = self.moteur.raisonner(base_de_faits)
        
        # Afficher le résultat
        resultat.afficher_resultat()
        
        # Recommander les soutiens
        print("\n" + "="*70)
        print("DISPOSITIFS DE SOUTIEN RECOMMANDÉS")
        print("="*70)
        
        soutiens = self.systeme_soutien.recommander_soutiens(
            etudiant,
            base_de_faits.motivation_calculee,
            base_de_faits.potentiel
        )
        
        plan = self.systeme_soutien.generer_plan_soutien(etudiant, soutiens)
        print(plan)
        
        # Enregistrer le résultat
        self.resultats.append(resultat)
        
        return resultat
    
    def analyser_groupe_etudiants(self, etudiants: List[Etudiant]) -> List[ResultatOrientation]:
        """
        Analyse un groupe d'étudiants.
        
        Args:
            etudiants: Liste d'objets Étudiant
            
        Returns:
            Liste des résultats
        """
        resultats = []
        
        print("\n" + "▓"*70)
        print("▓" + f"ANALYSE D'UN GROUPE DE {len(etudiants)} ÉTUDIANTS".center(68) + "▓")
        print("▓"*70 + "\n")
        
        for i, etudiant in enumerate(etudiants, 1):
            print(f"\n{'─'*70}")
            print(f"ÉTUDIANT {i}/{len(etudiants)}")
            print(f"{'─'*70}")
            
            resultat = self.analyser_etudiant(etudiant)
            resultats.append(resultat)
            
            input("\n➜ Appuyez sur ENTRÉE pour continuer... ")
        
        return resultats
    
    def generer_rapport(self, nom_fichier: str = None) -> str:
        """
        Génère un rapport complet des analyses effectuées.
        
        Args:
            nom_fichier: Nom du fichier de rapport (sans extension)
            
        Returns:
            Chemin du fichier rapport généré
        """
        if not self.resultats:
            print("Aucun résultat à exporter.")
            return None
        
        if nom_fichier is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"rapport_orientation_{timestamp}"
        
        # Générer rapport HTML
        rapport_html = self._generer_rapport_html()
        fichier_html = self.rapport_path / f"{nom_fichier}.html"
        
        with open(fichier_html, 'w', encoding='utf-8') as f:
            f.write(rapport_html)
        
        print(f"\n✓ Rapport HTML généré: {fichier_html}")
        
        # Générer rapport JSON
        rapport_json = self._generer_rapport_json()
        fichier_json = self.rapport_path / f"{nom_fichier}.json"
        
        with open(fichier_json, 'w', encoding='utf-8') as f:
            json.dump(rapport_json, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Rapport JSON généré: {fichier_json}")
        
        # Générer rapport texte
        rapport_texte = self._generer_rapport_texte()
        fichier_texte = self.rapport_path / f"{nom_fichier}.txt"
        
        with open(fichier_texte, 'w', encoding='utf-8') as f:
            f.write(rapport_texte)
        
        print(f"✓ Rapport texte généré: {fichier_texte}")
        
        return str(fichier_html)
    
    def _generer_rapport_html(self) -> str:
        """Génère un rapport au format HTML."""
        html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Orientation Académique</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .timestamp {
            font-size: 0.9em;
            margin-top: 15px;
        }
        .resultat-card {
            background: white;
            border-left: 4px solid #667eea;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .resultat-card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .info-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .info-item {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #764ba2;
        }
        .info-item label {
            font-weight: bold;
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }
        .info-item value {
            font-size: 1.1em;
            color: #333;
        }
        .filiere {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 1.3em;
            text-align: center;
        }
        .soutien {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .confiance {
            margin-top: 15px;
            padding: 15px;
            background: #f0f4ff;
            border-radius: 5px;
        }
        .barre-confiance {
            width: 100%;
            height: 20px;
            background: #ddd;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        .barre-remplissage {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
        }
        @media print {
            body {
                background: white;
            }
            .container {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 Système Expert d'Orientation Académique</h1>
            <p>Rapport de recommandation personnalisée</p>
            <p class="timestamp">Généré le: """ + datetime.now().strftime("%d/%m/%Y à %H:%M:%S") + """</p>
        </header>
"""
        
        # Ajouter chaque résultat
        for resultat in self.resultats:
            html += f"""
        <div class="resultat-card">
            <h2>📋 {resultat.etudiant_nom}</h2>
            <div class="info-group">
                <div class="info-item">
                    <label>ID Étudiant:</label>
                    <value>{resultat.etudiant_id}</value>
                </div>
                <div class="info-item">
                    <label>Motivation Calculée:</label>
                    <value>{resultat.motivation_calculee}</value>
                </div>
                <div class="info-item">
                    <label>Potentiel Académique:</label>
                    <value>{resultat.potentiel}</value>
                </div>
                <div class="info-item">
                    <label>Confiance du Système:</label>
                    <value>{resultat.confiance*100:.1f}%</value>
                </div>
            </div>
            
            <div class="filiere">
                <strong>Filière Recommandée:</strong> {resultat.filiere_recommandee}
            </div>
            
            <h3 style="color: #667eea; margin-top: 20px;">📚 Soutien Principal</h3>
            <div class="soutien">
                {resultat.type_soutien_principal}
            </div>
"""
            
            if resultat.soutiens_complements:
                html += """
            <h3 style="color: #667eea; margin-top: 20px;">🔧 Soutiens Complémentaires</h3>
"""
                for soutien in resultat.soutiens_complements:
                    html += f'            <div class="soutien">{soutien}</div>\n'
            
            html += f"""
            <div class="confiance">
                <label style="font-weight: bold;">Niveau de Confiance:</label>
                <div class="barre-confiance">
                    <div class="barre-remplissage" style="width: {resultat.confiance*100}%"></div>
                </div>
                <p style="margin-top: 10px; color: #667eea;"><strong>{resultat.confiance*100:.1f}%</strong></p>
            </div>
            
            <h3 style="color: #667eea; margin-top: 20px;">💬 Justification</h3>
            <p style="background: #f9f9f9; padding: 15px; border-radius: 5px; line-height: 1.8;">
                {resultat.justification}
            </p>
        </div>
"""
        
        html += """
        <footer>
            <p>© 2026 Système Expert d'Orientation Académique</p>
            <p>Université - Master MIATE</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _generer_rapport_json(self) -> dict:
        """Génère un rapport au format JSON."""
        return {
            'titre': 'Rapport d\'Orientation Académique',
            'date_generation': datetime.now().isoformat(),
            'nombre_etudiants': len(self.resultats),
            'resultats': [r.exporter_json() for r in self.resultats],
            'statistiques': self._calculer_statistiques()
        }
    
    def _generer_rapport_texte(self) -> str:
        """Génère un rapport au format texte."""
        texte = "═" * 80 + "\n"
        texte += "SYSTÈME EXPERT D'ORIENTATION ACADÉMIQUE".center(80) + "\n"
        texte += "RAPPORT COMPLET".center(80) + "\n"
        texte += "═" * 80 + "\n\n"
        
        texte += f"Date de génération: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n"
        texte += f"Nombre d'étudiants analysés: {len(self.resultats)}\n"
        texte += "-" * 80 + "\n\n"
        
        for i, resultat in enumerate(self.resultats, 1):
            texte += f"\n{'─' * 80}\n"
            texte += f"ÉTUDIANT {i}: {resultat.etudiant_nom}\n"
            texte += f"{'─' * 80}\n"
            texte += f"ID: {resultat.etudiant_id}\n"
            texte += f"Motivation: {resultat.motivation_calculee}\n"
            texte += f"Potentiel: {resultat.potentiel}\n"
            texte += f"Filière recommandée: {resultat.filiere_recommandee}\n"
            texte += f"Soutien principal: {resultat.type_soutien_principal}\n"
            
            if resultat.soutiens_complements:
                texte += f"Soutiens complémentaires:\n"
                for soutien in resultat.soutiens_complements:
                    texte += f"  • {soutien}\n"
            
            texte += f"Confiance: {resultat.confiance*100:.1f}%\n"
            texte += f"\nJustification:\n{resultat.justification}\n"
        
        texte += "\n" + "═" * 80 + "\n"
        texte += "FIN DU RAPPORT\n"
        texte += "═" * 80 + "\n"
        
        return texte
    
    def _calculer_statistiques(self) -> dict:
        """Calcule les statistiques globales."""
        if not self.resultats:
            return {}
        
        motivations = {}
        potentiels = {}
        filieres = {}
        soutiens = {}
        
        for resultat in self.resultats:
            # Motivations
            mot = resultat.motivation_calculee
            motivations[mot] = motivations.get(mot, 0) + 1
            
            # Potentiels
            pot = resultat.potentiel
            potentiels[pot] = potentiels.get(pot, 0) + 1
            
            # Filières
            fil = resultat.filiere_recommandee
            filieres[fil] = filieres.get(fil, 0) + 1
            
            # Soutiens
            sout = resultat.type_soutien_principal
            soutiens[sout] = soutiens.get(sout, 0) + 1
        
        confiance_moyenne = sum(r.confiance for r in self.resultats) / len(self.resultats)
        
        return {
            'total_etudiants': len(self.resultats),
            'confiance_moyenne': round(confiance_moyenne * 100, 2),
            'distribution_motivations': motivations,
            'distribution_potentiels': potentiels,
            'distribution_filieres': filieres,
            'distribution_soutiens': soutiens
        }


def creer_etudiants_exemple() -> List[Etudiant]:
    """Crée une liste d'étudiants pour les tests."""
    
    etudiants = [
        # Cas 1: Étudiant performant
        Etudiant(
            id="E001",
            nom="Dupont",
            prenom="Jean",
            moyenne=14.5,
            note_math=15,
            note_info=14,
            filiere_souhaitee="Informatique",
            attendance_rate=95,
            study_hours=12,
            homework_completion=True,
            participation_score=5,
            capacite_travail=NiveauCapacite.ELEVEE,
            disponibilite_soutien=False
        ),
        
        # Cas 2: Étudiant avec potentiel malgré faible moyenne
        Etudiant(
            id="E002",
            nom="Martin",
            prenom="Marie",
            moyenne=11,
            note_math=8,
            note_info=13,
            filiere_souhaitee="Informatique",
            attendance_rate=85,
            study_hours=12,
            homework_completion=True,
            participation_score=4,
            capacite_travail=NiveauCapacite.ELEVEE,
            disponibilite_soutien=True
        ),
        
        # Cas 3: Étudiant moyen
        Etudiant(
            id="E003",
            nom="Bernard",
            prenom="Pierre",
            moyenne=12,
            note_math=11,
            note_info=12,
            filiere_souhaitee="Mathématiques",
            attendance_rate=70,
            study_hours=7,
            homework_completion=True,
            participation_score=3,
            capacite_travail=NiveauCapacite.MOYENNE,
            disponibilite_soutien=True
        ),
        
        # Cas 4: Étudiant en difficulté
        Etudiant(
            id="E004",
            nom="Lambert",
            prenom="Sophie",
            moyenne=8.5,
            note_math=7,
            note_info=8,
            filiere_souhaitee="Informatique",
            attendance_rate=55,
            study_hours=3,
            homework_completion=False,
            participation_score=1,
            capacite_travail=NiveauCapacite.FAIBLE,
            disponibilite_soutien=True
        ),
        
        # Cas 5: Étudiant moyen-bas
        Etudiant(
            id="E005",
            nom="Moreau",
            prenom="Luc",
            moyenne=10,
            note_math=9,
            note_info=11,
            filiere_souhaitee="Informatique",
            attendance_rate=65,
            study_hours=5,
            homework_completion=True,
            participation_score=2,
            capacite_travail=NiveauCapacite.MOYENNE,
            disponibilite_soutien=True
        ),
    ]
    
    return etudiants


def main():
    """Fonction principale - Interface du système."""
    print("\n" + "█"*70)
    print("█" + "SYSTÈME EXPERT D'ORIENTATION ACADÉMIQUE".center(68) + "█")
    print("█" + "Bienvenue dans le système d'aide à la décision".center(68) + "█")
    print("█"*70 + "\n")
    
    # Initialiser le système
    systeme = SystemeExpertOrientationAcademique()
    
    # Menu principal
    while True:
        print("\n" + "="*70)
        print("MENU PRINCIPAL")
        print("="*70)
        print("1. Analyser un étudiant unique")
        print("2. Analyser le groupe d'étudiants d'exemple")
        print("3. Afficher le catalogue des dispositifs de soutien")
        print("4. Générer un rapport")
        print("5. Quitter")
        print("="*70)
        
        choix = input("\n➜ Choisissez une option (1-5): ").strip()
        
        if choix == "1":
            # Analyser un étudiant unique
            print("\n" + "-"*70)
            print("ANALYSE D'UN ÉTUDIANT UNIQUE")
            print("-"*70)
            
            try:
                etudiant = Etudiant(
                    id=input("ID de l'étudiant: "),
                    nom=input("Nom: "),
                    prenom=input("Prénom: "),
                    moyenne=float(input("Moyenne générale (0-20): ")),
                    note_math=float(input("Note en mathématiques (0-20): ")),
                    note_info=float(input("Note en informatique (0-20): ")),
                    filiere_souhaitee=input("Filière souhaitée: "),
                    attendance_rate=float(input("Taux de présence (%): ")),
                    study_hours=float(input("Heures d'étude par semaine: ")),
                    homework_completion=input("Devoirs complétés? (oui/non): ").lower() == "oui",
                    participation_score=int(input("Score de participation (1-5): ")),
                    capacite_travail=NiveauCapacite(input("Capacité de travail (élevée/moyenne/faible): ")),
                    disponibilite_soutien=input("Disponible pour soutien? (oui/non): ").lower() == "oui"
                )
                
                systeme.analyser_etudiant(etudiant)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        elif choix == "2":
            # Analyser le groupe d'exemple
            etudiants = creer_etudiants_exemple()
            systeme.analyser_groupe_etudiants(etudiants)
        
        elif choix == "3":
            # Afficher le catalogue
            systeme.systeme_soutien.afficher_catalogue_dispositifs()
        
        elif choix == "4":
            # Générer un rapport
            if systeme.resultats:
                nom = input("Nom du rapport (optionnel, appuyez sur ENTRÉE pour auto-généré): ").strip()
                systeme.generer_rapport(nom if nom else None)
            else:
                print("❌ Aucun résultat à exporter. Veuillez d'abord analyser des étudiants.")
        
        elif choix == "5":
            print("\n👋 Merci d'avoir utilisé le système expert. Au revoir!\n")
            break
        
        else:
            print("❌ Option invalide. Veuillez choisir 1-5.")


if __name__ == "__main__":
    main()
