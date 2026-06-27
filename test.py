# Tests simples du système
from models import Etudiant, BaseDeFaits
from inference_engine import MoteurInference


def test_etudiant_excellent():
    print("\n=== TEST 1: Excellent étudiant ===")
    
    etudiant = Etudiant(
        id="E001",
        nom="Ali",
        prenom="Ahmed",
        moyenne=17,
        note_math=18,
        note_info=19,
        filiere="Informatique",
        attendance=95,
        study_hours=15,
        devoirs=True,
        participation=5
    )
    
    bdf = BaseDeFaits(etudiant)
    moteur = MoteurInference()
    resultat = moteur.raisonner(bdf)
    resultat.afficher()


def test_etudiant_moyen():
    print("\n=== TEST 2: Étudiant moyen ===")
    
    etudiant = Etudiant(
        id="E002",
        nom="Fatima",
        prenom="Benali",
        moyenne=11,
        note_math=10,
        note_info=12,
        filiere="Informatique",
        attendance=70,
        study_hours=8,
        devoirs=True,
        participation=3
    )
    
    bdf = BaseDeFaits(etudiant)
    moteur = MoteurInference()
    resultat = moteur.raisonner(bdf)
    resultat.afficher()


def test_etudiant_faible():
    print("\n=== TEST 3: Étudiant faible ===")
    
    etudiant = Etudiant(
        id="E003",
        nom="Mohamed",
        prenom="Hassan",
        moyenne=7,
        note_math=6,
        note_info=8,
        filiere="Informatique",
        attendance=50,
        study_hours=3,
        devoirs=False,
        participation=1
    )
    
    bdf = BaseDeFaits(etudiant)
    moteur = MoteurInference()
    resultat = moteur.raisonner(bdf)
    resultat.afficher()


if __name__ == "__main__":
    test_etudiant_excellent()
    test_etudiant_moyen()
    test_etudiant_faible()
