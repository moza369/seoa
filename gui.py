"""
Interface graphique (GUI) du système expert d'orientation académique.
Construit avec Tkinter — interface professionnelle avec diagnostic CS.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import (
    Etudiant, BaseDeFaits, NiveauCapacite, ProfilInformatique, ResultatOrientation
)
from inference_engine import MoteurInference
from main import SystemeExpertOrientationAcademique

# Fichier de sauvegarde automatique de la session
FICHIER_SESSION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_resultats.json")


# ─── Thèmes ───────────────────────────────────────────────────────────────────
DARK_PALETTE = {
    "FOND": "#1e1e2e",
    "SURFACE": "#2a2a3e",
    "CARD": "#313147",
    "CARD2": "#393960",
    "ACCENT": "#7c6af5",
    "ACCENT2": "#56cfad",
    "DANGER": "#f55a5a",
    "AVERT": "#f5a623",
    "TEXTE": "#e0e0f0",
    "TEXTE_DIM": "#8888aa",
    "ENTREE": "#252538",
    "BORDURE": "#44445a",
}

LIGHT_PALETTE = {
    "FOND": "#ffffff",
    "SURFACE": "#f8f9fa",
    "CARD": "#f0f2f5",
    "CARD2": "#e8eaed",
    "ACCENT": "#2563eb",
    "ACCENT2": "#059669",
    "DANGER": "#dc2626",
    "AVERT": "#f59e0b",
    "TEXTE": "#1f2937",
    "TEXTE_DIM": "#6b7280",
    "ENTREE": "#ffffff",
    "BORDURE": "#e5e7eb",
}

# Thème par défaut (light pour meilleure lisibilité des données)
CURRENT_PALETTE = LIGHT_PALETTE.copy()
FOND        = CURRENT_PALETTE["FOND"]
SURFACE     = CURRENT_PALETTE["SURFACE"]
CARD        = CURRENT_PALETTE["CARD"]
CARD2       = CURRENT_PALETTE["CARD2"]
ACCENT      = CURRENT_PALETTE["ACCENT"]
ACCENT2     = CURRENT_PALETTE["ACCENT2"]
DANGER      = CURRENT_PALETTE["DANGER"]
AVERT       = CURRENT_PALETTE["AVERT"]
TEXTE       = CURRENT_PALETTE["TEXTE"]
TEXTE_DIM   = CURRENT_PALETTE["TEXTE_DIM"]
ENTREE      = CURRENT_PALETTE["ENTREE"]
BORDURE     = CURRENT_PALETTE["BORDURE"]

F_TITRE  = ("Segoe UI", 18, "bold")
F_SOUS   = ("Segoe UI", 13, "bold")
F_CORPS  = ("Segoe UI", 12)
F_PETIT  = ("Segoe UI", 11)
F_MONO   = ("Consolas", 10)
F_GRAND  = ("Segoe UI", 26, "bold")

BADGE_BON   = "#1e4d3a"
BADGE_MOY   = "#4d3b1e"
BADGE_FAIB  = "#4d1e1e"
TXT_BON     = ACCENT2
TXT_MOY     = AVERT
TXT_FAIB    = DANGER


# ─── Widgets réutilisables ────────────────────────────────────────────────────

class CarteKV(tk.Frame):
    def __init__(self, parent, titre, valeur, couleur=ACCENT, **kw):
        super().__init__(parent, bg=CARD, bd=0, padx=18, pady=14, **kw)
        tk.Label(self, text=titre, font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=TEXTE_DIM).pack(anchor="w")
        tk.Label(self, text=valeur, font=("Segoe UI", 13, "bold"),
                 bg=CARD, fg=couleur, wraplength=180).pack(anchor="w", pady=(2, 0))


class BarreConfiance(tk.Frame):
    def __init__(self, parent, valeur: float, **kw):
        super().__init__(parent, bg=CARD, padx=18, pady=12, **kw)
        couleur = ACCENT2 if valeur >= 0.9 else AVERT if valeur >= 0.75 else DANGER
        tk.Label(self, text=f"Confiance du système : {valeur*100:.0f} %",
                 font=F_SOUS, bg=CARD, fg=couleur).pack(anchor="w")
        fond = tk.Frame(self, bg=SURFACE, height=10)
        fond.pack(fill="x", pady=(6, 0))
        tk.Frame(fond, bg=couleur, height=10,
                 width=int(500 * valeur)).place(x=0, y=0)


# ─── Application principale ───────────────────────────────────────────────────

class ApplicationSEOA(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("SÉOA — Système Expert d'Orientation Académique | MIATE 2025/2026")
        self.configure(bg=FOND)
        try:
            self.attributes("-zoomed", True)
        except Exception:
            self.state("zoomed")

        self.systeme = SystemeExpertOrientationAcademique()
        self._champs = {}
        self._profil_vars = {}
        self._section_profil = None
        self.current_theme = "light"  # Thème actuel

        self._creer_style()
        # Créer conteneur principal avec sidebar
        self._conteneur_principal = tk.Frame(self, bg=FOND)
        self._conteneur_principal.pack(fill="both", expand=True)
        self._creer_sidebar()
        self._creer_contenu()
        self._afficher_onglet("saisie")
        self._charger_session()

    def _creer_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=FOND, borderwidth=0)
        s.configure("TNotebook.Tab", background=SURFACE, foreground=TEXTE_DIM,
                    padding=[18, 8], font=F_CORPS)
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])
        s.configure("TCombobox", fieldbackground=ENTREE,
                    background=ENTREE, foreground=TEXTE,
                    selectbackground=ACCENT)
        s.configure("Vertical.TScrollbar", background=SURFACE, troughcolor=FOND)
        s.configure("Treeview", background=CARD, foreground=TEXTE,
                    rowheight=28, fieldbackground=CARD, font=F_CORPS)
        s.configure("Treeview.Heading", background=SURFACE,
                    foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", ACCENT)])

    def _creer_sidebar(self):
        """Crée la barre latérale gauche avec navigation et thème."""
        sidebar = tk.Frame(self._conteneur_principal, bg=SURFACE, width=220)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)
        
        # Titre application
        titre_frame = tk.Frame(sidebar, bg=SURFACE)
        titre_frame.pack(fill="x", pady=(20, 30), padx=15)
        tk.Label(titre_frame, text="🎓 SÉOA", font=("Segoe UI", 16, "bold"),
                 bg=SURFACE, fg=ACCENT, wraplength=190, justify="center").pack()
        tk.Label(titre_frame, text="Orientation Académique", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXTE_DIM, wraplength=190, justify="center").pack(pady=(5, 0))
        
        # Séparateur
        tk.Frame(sidebar, bg=BORDURE, height=1).pack(fill="x", padx=10, pady=(0, 20))
        
        # Navigation buttons
        self._boutons_nav = {}
        onglets = [
            ("saisie",    "📝  Saisie"),
            ("regles",    "📋  Règles"),
            ("resultats", "📊  Résultats"),
            ("rapport",   "📄  Rapport"),
        ]
        
        nav_frame = tk.Frame(sidebar, bg=SURFACE)
        nav_frame.pack(fill="x", padx=10, pady=(0, 30))
        
        for cle, texte in onglets:
            btn = tk.Button(nav_frame, text=texte, font=("Segoe UI", 11),
                            bg=SURFACE, fg=TEXTE, relief="flat",
                            bd=0, padx=12, pady=14, cursor="hand2",
                            justify="left", anchor="w",
                            command=lambda c=cle: self._afficher_onglet(c))
            btn.pack(fill="x", pady=(0, 8))
            self._boutons_nav[cle] = btn
        
        # Séparateur avant thème
        tk.Frame(sidebar, bg=BORDURE, height=1).pack(fill="x", padx=10, pady=20)
        
        # Theme button
        theme_frame = tk.Frame(sidebar, bg=SURFACE)
        theme_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.btn_theme = tk.Button(theme_frame, text="☀️ Light Theme", font=("Segoe UI", 10),
                                   bg=ACCENT, fg="#ffffff", relief="flat",
                                   bd=0, padx=12, pady=12, cursor="hand2",
                                   wraplength=190, justify="center",
                                   command=self._changer_theme)
        self.btn_theme.pack(fill="x")


    def _creer_contenu(self):
        self._cadre_contenu = tk.Frame(self._conteneur_principal, bg=FOND)
        self._cadre_contenu.pack(fill="both", expand=True, side="right")
        constructeurs = {
            "saisie":    self._page_saisie,
            "regles":    self._page_regles,
            "resultats": self._page_resultats,
            "rapport":   self._page_rapport,
        }
        self._frames = {}
        for cle, fn in constructeurs.items():
            f = tk.Frame(self._cadre_contenu, bg=FOND)
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            fn(f)
            self._frames[cle] = f

    def _afficher_onglet(self, cle):
        for c, btn in self._boutons_nav.items():
            btn.configure(bg=ACCENT if c == cle else SURFACE,
                          fg="#ffffff" if c == cle else TEXTE_DIM)
        self._frames[cle].lift()
    
    def _changer_theme(self):
        """Bascule entre les thèmes light et dark"""
        global FOND, SURFACE, CARD, CARD2, ACCENT, ACCENT2, DANGER, AVERT, TEXTE, TEXTE_DIM, ENTREE, BORDURE, CURRENT_PALETTE
        
        if self.current_theme == "light":
            self.current_theme = "dark"
            new_palette = DARK_PALETTE.copy()
            self.btn_theme.configure(text="🌙 Dark Theme")
        else:
            self.current_theme = "light"
            new_palette = LIGHT_PALETTE.copy()
            self.btn_theme.configure(text="☀️ Light Theme")
        
        # Mettre à jour le dictionnaire global
        CURRENT_PALETTE.clear()
        CURRENT_PALETTE.update(new_palette)
        
        # Mettre à jour les variables globales du module
        import gui as gui_module
        gui_module.FOND = CURRENT_PALETTE["FOND"]
        gui_module.SURFACE = CURRENT_PALETTE["SURFACE"]
        gui_module.CARD = CURRENT_PALETTE["CARD"]
        gui_module.CARD2 = CURRENT_PALETTE["CARD2"]
        gui_module.ACCENT = CURRENT_PALETTE["ACCENT"]
        gui_module.ACCENT2 = CURRENT_PALETTE["ACCENT2"]
        gui_module.DANGER = CURRENT_PALETTE["DANGER"]
        gui_module.AVERT = CURRENT_PALETTE["AVERT"]
        gui_module.TEXTE = CURRENT_PALETTE["TEXTE"]
        gui_module.TEXTE_DIM = CURRENT_PALETTE["TEXTE_DIM"]
        gui_module.ENTREE = CURRENT_PALETTE["ENTREE"]
        gui_module.BORDURE = CURRENT_PALETTE["BORDURE"]
        
        FOND = CURRENT_PALETTE["FOND"]
        SURFACE = CURRENT_PALETTE["SURFACE"]
        CARD = CURRENT_PALETTE["CARD"]
        CARD2 = CURRENT_PALETTE["CARD2"]
        ACCENT = CURRENT_PALETTE["ACCENT"]
        ACCENT2 = CURRENT_PALETTE["ACCENT2"]
        DANGER = CURRENT_PALETTE["DANGER"]
        AVERT = CURRENT_PALETTE["AVERT"]
        TEXTE = CURRENT_PALETTE["TEXTE"]
        TEXTE_DIM = CURRENT_PALETTE["TEXTE_DIM"]
        ENTREE = CURRENT_PALETTE["ENTREE"]
        BORDURE = CURRENT_PALETTE["BORDURE"]
        
        # Mettre à jour l'interface - refaire les frames et widgets
        self._rafraichir_theme()
    
    def _rafraichir_theme(self):
        """Rafraîchit tous les éléments visuels avec le nouveau thème"""
        # Mettre à jour le style ttk
        self._creer_style()
        
        # Mettre à jour les couleurs des widgets
        self.configure(bg=CURRENT_PALETTE["FOND"])
        self._cadre_contenu.configure(bg=CURRENT_PALETTE["FOND"])
        
        # Parcourir tous les widgets et mettre à jour les couleurs
        self._update_all_widgets(self)
    
    def _update_all_widgets(self, parent):
        """Met à jour les couleurs de tous les widgets récursivement"""
        for widget in parent.winfo_children():
            try:
                if isinstance(widget, tk.Frame):
                    if widget.cget('bg') in [DARK_PALETTE["FOND"], LIGHT_PALETTE["FOND"]]:
                        widget.configure(bg=CURRENT_PALETTE["FOND"])
                    elif widget.cget('bg') in [DARK_PALETTE["SURFACE"], LIGHT_PALETTE["SURFACE"]]:
                        widget.configure(bg=CURRENT_PALETTE["SURFACE"])
                    elif widget.cget('bg') in [DARK_PALETTE["CARD"], LIGHT_PALETTE["CARD"]]:
                        widget.configure(bg=CURRENT_PALETTE["CARD"])
                    elif widget.cget('bg') in [DARK_PALETTE["CARD2"], LIGHT_PALETTE["CARD2"]]:
                        widget.configure(bg=CURRENT_PALETTE["CARD2"])
                    self._update_all_widgets(widget)
                    
                elif isinstance(widget, tk.Label):
                    bg = widget.cget('bg')
                    fg = widget.cget('fg')
                    if bg in [DARK_PALETTE["FOND"], LIGHT_PALETTE["FOND"]]:
                        widget.configure(bg=CURRENT_PALETTE["FOND"])
                    elif bg in [DARK_PALETTE["SURFACE"], LIGHT_PALETTE["SURFACE"]]:
                        widget.configure(bg=CURRENT_PALETTE["SURFACE"])
                    elif bg in [DARK_PALETTE["CARD"], LIGHT_PALETTE["CARD"]]:
                        widget.configure(bg=CURRENT_PALETTE["CARD"])
                    
                    if fg in [DARK_PALETTE["TEXTE"], LIGHT_PALETTE["TEXTE"]]:
                        widget.configure(fg=CURRENT_PALETTE["TEXTE"])
                    elif fg in [DARK_PALETTE["TEXTE_DIM"], LIGHT_PALETTE["TEXTE_DIM"]]:
                        widget.configure(fg=CURRENT_PALETTE["TEXTE_DIM"])
                    elif fg in [DARK_PALETTE["ACCENT"], LIGHT_PALETTE["ACCENT"]]:
                        widget.configure(fg=CURRENT_PALETTE["ACCENT"])
                
                elif isinstance(widget, tk.Button):
                    bg = widget.cget('bg')
                    fg = widget.cget('fg')
                    if bg in [DARK_PALETTE["SURFACE"], LIGHT_PALETTE["SURFACE"]]:
                        widget.configure(bg=CURRENT_PALETTE["SURFACE"])
                    elif bg in [DARK_PALETTE["ACCENT"], LIGHT_PALETTE["ACCENT"]]:
                        widget.configure(bg=CURRENT_PALETTE["ACCENT"])
                    
                    if fg in [DARK_PALETTE["TEXTE_DIM"], LIGHT_PALETTE["TEXTE_DIM"]]:
                        widget.configure(fg=CURRENT_PALETTE["TEXTE_DIM"])
                    elif fg == "#ffffff":
                        pass  # Garder le blanc
                        
                elif isinstance(widget, tk.Canvas):
                    if widget.cget('bg') in [DARK_PALETTE["FOND"], LIGHT_PALETTE["FOND"]]:
                        widget.configure(bg=CURRENT_PALETTE["FOND"])
                    self._update_all_widgets(widget)
            except:
                pass

    # ═════════════════ PAGE SAISIE ═══════════════════════════════════════════

    def _page_saisie(self, parent):
        eh = tk.Frame(parent, bg=FOND)
        eh.pack(fill="x", padx=30, pady=(22, 5))
        tk.Label(eh, text="📋 Saisie des données étudiant",
                 font=("Segoe UI", 22, "bold"), bg=FOND, fg=ACCENT).pack(side="left")
        tk.Label(eh, text="Remplissez les champs ci-dessous",
                 font=("Segoe UI", 10), bg=FOND, fg=TEXTE_DIM).pack(side="left", padx=(20, 0))

        canevas = tk.Canvas(parent, bg=FOND, highlightthickness=0)
        barre_v = ttk.Scrollbar(parent, orient="vertical", command=canevas.yview)
        cadre = tk.Frame(canevas, bg=FOND)
        cadre.bind("<Configure>",
                   lambda e: canevas.configure(scrollregion=canevas.bbox("all")))
        canevas.create_window((0, 0), window=cadre, anchor="nw")
        canevas.configure(yscrollcommand=barre_v.set)
        canevas.pack(side="left", fill="both", expand=True, padx=(30, 0))
        barre_v.pack(side="right", fill="y", padx=(0, 10))
        canevas.bind_all("<MouseWheel>",
                         lambda e: canevas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Identité — Section colorée
        self._titre_section(cadre, "👤  Identité de l'étudiant")
        card_identite = tk.Frame(cadre, bg=CARD2, relief="flat", bd=0)
        card_identite.pack(fill="x", pady=(8, 15), padx=(0, 10))
        
        g = tk.Frame(card_identite, bg=CARD2)
        g.pack(fill="x", padx=16, pady=16)
        for label, cle, defaut, c in [
            ("ID", "id", "E001", 0),
            ("Nom", "nom", "Martin", 1),
            ("Prénom", "prenom", "Marie", 2),
        ]:
            self._champ(g, label, cle, defaut, 0, c)

        tk.Label(g, text="Filière souhaitée", font=F_CORPS,
                 bg=CARD2, fg=TEXTE_DIM).grid(row=0, column=3, sticky="w", padx=(0, 30))
        self._champs['filiere_souhaitee'] = tk.StringVar(value="Informatique")
        cb = ttk.Combobox(g, textvariable=self._champs['filiere_souhaitee'],
                          values=["Informatique", "Mathématiques", "Physique",
                                  "Économie", "Autre", "Filière moins exigeante"],
                          state="readonly", width=22, font=F_CORPS)
        cb.grid(row=1, column=3, sticky="w", padx=(0, 30), pady=(2, 5))
        cb.bind("<<ComboboxSelected>>", lambda e: self._toggle_profil_info())

        # Notes — Section colorée
        self._titre_section(cadre, "📚  Notes académiques (0 – 20)")
        card_notes = tk.Frame(cadre, bg="#e8f5e9", relief="flat", bd=0)
        card_notes.pack(fill="x", pady=(8, 15), padx=(0, 10))
        
        gn = tk.Frame(card_notes, bg="#e8f5e9")
        gn.pack(fill="x", padx=16, pady=16)
        for label, cle, defaut, c in [
            ("Moyenne générale", "moyenne", "11", 0),
            ("Note Mathématiques", "note_math", "8", 1),
            ("Note Informatique", "note_info", "13", 2),
        ]:
            self._champ(gn, label, cle, defaut, 0, c)

        # Comportement — Section colorée
        self._titre_section(cadre, "📈  Indicateurs comportementaux")
        card_comport = tk.Frame(cadre, bg="#fff3e0", relief="flat", bd=0)
        card_comport.pack(fill="x", pady=(8, 15), padx=(0, 10))
        
        gc = tk.Frame(card_comport, bg="#fff3e0")
        gc.pack(fill="x", padx=16, pady=16)
        for label, cle, defaut, c in [
            ("Présence (%)", "attendance_rate", "85", 0),
            ("Étude (h/semaine)", "study_hours", "12", 1),
            ("Participation (1–5)", "participation_score", "4", 2),
        ]:
            self._champ(gc, label, cle, defaut, 0, c)

        # Sélecteurs — Section colorée
        self._titre_section(cadre, "✅  Critères additionnels")
        card_selec = tk.Frame(cadre, bg="#f3e5f5", relief="flat", bd=0)
        card_selec.pack(fill="x", pady=(8, 15), padx=(0, 10))
        
        gs = tk.Frame(card_selec, bg="#f3e5f5")
        gs.pack(fill="x", padx=16, pady=16)
        for label, cle, vals, defaut, col in [
            ("Devoirs complétés",        "homework_completion",    ["Oui","Non"],               "Oui",    0),
            ("Capacité de travail",      "capacite_travail",       ["élevée","moyenne","faible"],"élevée", 1),
            ("Disponible pour soutien",  "disponibilite_soutien",  ["Oui","Non"],               "Oui",    2),
        ]:
            tk.Label(gs, text=label, font=("Segoe UI", 12, "bold"),
                     bg="#f3e5f5", fg="#6200ea").grid(row=0, column=col, sticky="w",
                                                  padx=(0, 30), pady=(8, 2))
            self._champs[cle] = tk.StringVar(value=defaut)
            cb2 = ttk.Combobox(gs, textvariable=self._champs[cle],
                               values=vals, state="readonly", width=22, font=("Segoe UI", 12))
            cb2.grid(row=1, column=col, sticky="ew", padx=(0, 30), pady=(2, 10))

        # Section Profil Informatique — Carte colorée
        self._section_profil = tk.Frame(cadre, bg=FOND)
        self._section_profil.pack(fill="x", pady=(0, 5))
        self._construire_profil_info(self._section_profil)
        self._toggle_profil_info()

        # Boutons d'action — Section colorée
        card_buttons = tk.Frame(cadre, bg=CARD2, relief="flat", bd=0)
        card_buttons.pack(fill="x", pady=(20, 15), padx=(0, 10))
        
        cb_act = tk.Frame(card_buttons, bg=CARD2)
        cb_act.pack(pady=20)
        tk.Button(cb_act, text="🚀  Lancer l'analyse",
                  font=("Segoe UI", 13, "bold"),
                  bg=ACCENT2, fg="white", relief="flat",
                  padx=36, pady=16, cursor="hand2",
                  command=self._analyser).pack(side="left", padx=12)
        tk.Button(cb_act, text="📂  Charger exemple",
                  font=("Segoe UI", 12), bg="#e3f2fd", fg=ACCENT,
                  relief="flat", padx=28, pady=16, cursor="hand2",
                  command=self._charger_exemple).pack(side="left", padx=12)
        tk.Button(cb_act, text="🗑  Effacer",
                  font=("Segoe UI", 12), bg="#ffebee", fg=DANGER,
                  relief="flat", padx=28, pady=16, cursor="hand2",
                  command=self._effacer).pack(side="left", padx=12)

        self._lbl_statut = tk.Label(cadre, text="", font=("Segoe UI", 11),
                                     bg=FOND, fg=ACCENT2)
        self._lbl_statut.pack(pady=8)

    def _construire_profil_info(self, parent):
        self._titre_section(parent,
            "🖥️  Profil Informatique — Diagnostic détaillé (optionnel)")
        tk.Label(parent,
                 text="Renseignez les notes par sous-domaine pour un diagnostic ciblé. Laissez vide pour ignorer.",
                 font=("Segoe UI", 11), bg=FOND, fg=TEXTE_DIM, justify="left").pack(
                 anchor="w", padx=4, pady=(0, 8))
        gi = tk.Frame(parent, bg=FOND)
        gi.pack(fill="x", pady=(0, 10))
        sous_comps = [
            ("Algorithmique / Logique",  "note_algo"),
            ("Écriture de code",         "note_programmation"),
            ("Lecture / Compréhension",  "note_lecture_code"),
            ("Structures de données",    "note_structures"),
            ("Bases de données / SQL",   "note_bdd"),
            ("Réseaux / Systèmes",       "note_reseau"),
        ]
        for idx, (label, cle) in enumerate(sous_comps):
            r, c = divmod(idx, 3)
            tk.Label(gi, text=label, font=("Segoe UI", 11, "bold"),
                     bg=FOND, fg=TEXTE_DIM).grid(
                     row=r*2, column=c, sticky="w", padx=(0, 30), pady=(8, 2))
            var = tk.StringVar(value="")
            e = tk.Entry(gi, textvariable=var, font=("Segoe UI", 13),
                         bg=ENTREE, fg=TEXTE, insertbackground=ACCENT,
                         relief="flat", bd=0,
                         highlightbackground=BORDURE, highlightthickness=2, width=24)
            e.grid(row=r*2+1, column=c, sticky="ew", padx=(0, 30), pady=(2, 10), ipady=6)
            self._profil_vars[cle] = var

    def _toggle_profil_info(self):
        if self._section_profil is None:
            return
        filiere = self._champs.get('filiere_souhaitee')
        if filiere and filiere.get().lower() == "informatique":
            self._section_profil.pack(fill="x", pady=(0, 5))
        else:
            self._section_profil.pack_forget()

    def _titre_section(self, parent, texte):
        c = tk.Frame(parent, bg=FOND)
        c.pack(fill="x", pady=(14, 8))
        # Couleur de la barre selon le titre
        if "Identité" in texte:
            couleur_barre = ACCENT
        elif "Notes" in texte:
            couleur_barre = "#4caf50"
        elif "Indicateurs" in texte:
            couleur_barre = "#ff9800"
        elif "Critères" in texte:
            couleur_barre = "#9c27b0"
        elif "Profil" in texte:
            couleur_barre = "#00bcd4"
        else:
            couleur_barre = ACCENT
            
        tk.Frame(c, bg=couleur_barre, width=4, height=24).pack(side="left")
        tk.Label(c, text=f"  {texte}", font=F_SOUS,
                 bg=FOND, fg=TEXTE).pack(side="left", padx=(2, 0))

    def _champ(self, parent, label, cle, defaut, row, col):
        # Label avec couleur selon le contexte du parent
        parent_bg = parent.cget("bg")
        if parent_bg == "#e8f5e9":  # Notes (vert clair)
            label_fg = "#2e7d32"
        elif parent_bg == "#fff3e0":  # Comportement (orange clair)
            label_fg = "#e65100"
        elif parent_bg == "#f3e5f5":  # Critères (violet clair)
            label_fg = "#6200ea"
        else:  # Identité (par défaut)
            label_fg = TEXTE_DIM
            
        tk.Label(parent, text=label, font=("Segoe UI", 12, "bold"),
                 bg=parent_bg, fg=label_fg).grid(
                 row=row*2, column=col, sticky="w", padx=(0, 30), pady=(12, 2))
        var = tk.StringVar(value=defaut)
        e = tk.Entry(parent, textvariable=var, font=("Segoe UI", 14),
                     bg=ENTREE, fg=TEXTE, insertbackground=ACCENT,
                     relief="flat", bd=0,
                     highlightbackground=BORDURE, highlightthickness=2, width=28)
        e.grid(row=row*2+1, column=col, sticky="ew", padx=(0, 30), pady=(2, 10), ipady=8)
        self._champs[cle] = var

    # ═════════════════ PAGE RÈGLES ════════════════════════════════════════════

    def _page_regles(self, parent):
        tk.Label(parent, text="Base de règles SI – ALORS",
                 font=F_TITRE, bg=FOND, fg=TEXTE).pack(
                 anchor="w", padx=30, pady=(22, 2))
        tk.Label(parent,
                 text="Chaînage avant | 4 phases : Motivation → Potentiel → Orientation → Diagnostic CS",
                 font=F_CORPS, bg=FOND, fg=TEXTE_DIM).pack(
                 anchor="w", padx=30, pady=(0, 12))

        cols = ("ID", "Phase", "Condition (SI)", "Conclusion (ALORS)")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=24)
        tv.heading("ID",    text="ID",    anchor="center")
        tv.heading("Phase", text="Phase", anchor="center")
        tv.heading("Condition (SI)",     text="Condition (SI)",     anchor="w")
        tv.heading("Conclusion (ALORS)", text="Conclusion (ALORS)", anchor="w")
        tv.column("ID",    width=55,  anchor="center")
        tv.column("Phase", width=170, anchor="center")
        tv.column("Condition (SI)",     width=480, anchor="w")
        tv.column("Conclusion (ALORS)", width=370, anchor="w")

        REGLES = [
            ("R1",   "1 – Motivation",  "attendance_rate ≥ 80 ET study_hours ≥ 10 ET homework = oui",                          "motivation = élevée"),
            ("R2",   "1 – Motivation",  "attendance_rate ∈ [60,79] OU study_hours ∈ [5,9]",                                    "motivation = moyenne"),
            ("R3",   "1 – Motivation",  "attendance_rate < 60 OU homework = non",                                               "motivation = faible"),
            ("R4",   "2 – Potentiel",   "motivation=élevée ET (capacité=élevée OU note_math≥12 OU note_info≥12)",              "potentiel = élevé"),
            ("R5",   "2 – Potentiel",   "motivation=moyenne OU (10≤moy<12 ET participation≥2)",                                 "potentiel = moyen"),
            ("R6",   "2 – Potentiel",   "moy<8 OU (motivation=faible ET capacité=faible)",                                      "potentiel = faible"),
            ("R7",   "3 – Orientation", "moy ≥ 14",                                                                             "filière=souhaitée, soutien=non nécessaire"),
            ("R8",   "3 – Orientation", "12≤moy<14 OU (moy<12 ET potentiel=élevé ET dispo=oui)",                               "filière=souhaitée, soutien=facultatif/obligatoire"),
            ("R9",   "3 – Orientation", "potentiel=moyen ET 10≤moy<12",                                                        "filière=souhaitée, soutien=personnalisé"),
            ("R10",  "3 – Orientation", "filière=Info ET note_math<10",                                                         "soutien += remise à niveau mathématiques"),
            ("R10b", "3 – Orientation", "filière=Info ET note_info<10",                                                         "soutien += cours de programmation intensif"),
            ("R10c", "3 – Orientation", "moy<10 ET potentiel=faible",                                                           "filière moins exigeante, soutien=accompagnement renforcé"),
            ("R11",  "4 – Diag. Info",  "filière=Info ET note_algo<10 ET note_prog<10",                                        "remise à niveau complète (algo + prog)"),
            ("R12",  "4 – Diag. Info",  "filière=Info ET note_lecture_code≥10 ET note_prog<10",                                "comprend le code mais ne sait pas l'écrire → atelier syntaxe"),
            ("R13",  "4 – Diag. Info",  "filière=Info ET note_prog≥10 ET note_algo<10",                                        "sait coder mais logique insuffisante → cours algorithmique"),
            ("R14",  "4 – Diag. Info",  "filière=Info ET note_structures<10",                                                   "lacune en structures de données"),
            ("R15",  "4 – Diag. Info",  "filière=Info ET note_bdd<10",                                                         "lacune en bases de données → atelier SQL"),
            ("R16",  "4 – Diag. Info",  "filière=Info ET toutes notes ≥ 12",                                                   "profil solide, aucun soutien spécifique requis"),
        ]
        TAGS = {
            "1 – Motivation":  ("#1e2d5a", TEXTE),
            "2 – Potentiel":   ("#1e4d38", TEXTE),
            "3 – Orientation": ("#4d2e1e", TEXTE),
            "4 – Diag. Info":  ("#3a1e5a", "#c8b0ff"),
        }
        for row in REGLES:
            tv.insert("", "end", values=row, tags=(row[1],))
        for phase, (bg, fg) in TAGS.items():
            tv.tag_configure(phase, background=bg, foreground=fg)

        barre = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=barre.set)
        tv.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        barre.pack(side="right", fill="y", padx=(0, 10), pady=(0, 20))

    # ═════════════════ PAGE RÉSULTATS ═════════════════════════════════════════

    def _page_resultats(self, parent):
        self._res_cadre = tk.Frame(parent, bg=FOND)
        self._res_cadre.pack(fill="both", expand=True)
        self._placeholder_resultats()

    def _placeholder_resultats(self):
        for w in self._res_cadre.winfo_children():
            w.destroy()
        tk.Label(self._res_cadre, text="Aucune analyse effectuée",
                 font=F_GRAND, bg=FOND, fg=TEXTE_DIM).pack(expand=True)
        tk.Label(self._res_cadre,
                 text="Saisissez les données d'un étudiant puis lancez l'analyse",
                 font=F_CORPS, bg=FOND, fg=TEXTE_DIM).pack()

    def _afficher_resultats(self, etudiant, bdf, resultat):
        for w in self._res_cadre.winfo_children():
            w.destroy()

        canevas = tk.Canvas(self._res_cadre, bg=FOND, highlightthickness=0)
        barre_v = ttk.Scrollbar(self._res_cadre, orient="vertical",
                                command=canevas.yview)
        corps = tk.Frame(canevas, bg=FOND)
        corps.bind("<Configure>",
                   lambda e: canevas.configure(scrollregion=canevas.bbox("all")))
        canevas.create_window((0, 0), window=corps, anchor="nw")
        canevas.configure(yscrollcommand=barre_v.set)
        canevas.pack(side="left", fill="both", expand=True, padx=30)
        barre_v.pack(side="right", fill="y", padx=(0, 10))
        canevas.bind_all("<MouseWheel>",
                         lambda e: canevas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # En-tête
        eh = tk.Frame(corps, bg=FOND)
        eh.pack(fill="x", pady=(20, 14))
        tk.Label(eh, text="Résultat — Orientation Académique",
                 font=F_TITRE, bg=FOND, fg=TEXTE).pack(side="left")
        tk.Label(eh, text=f"   {etudiant.prenom} {etudiant.nom}  (ID : {etudiant.id})",
                 font=("Segoe UI", 12), bg=FOND, fg=ACCENT).pack(side="left")

        # Cartes KV
        def c_mot(m):
            return ACCENT2 if m=="élevée" else AVERT if m=="moyenne" else DANGER
        def c_pot(p):
            return ACCENT2 if p=="élevé" else AVERT if p=="moyen" else DANGER

        cc = tk.Frame(corps, bg=FOND)
        cc.pack(fill="x", pady=(0, 14))
        for titre, val, coul in [
            ("🎯 Filière recommandée",  resultat.filiere_recommandee,      ACCENT),
            ("⚡ Motivation",           resultat.motivation_calculee,       c_mot(resultat.motivation_calculee)),
            ("💡 Potentiel",            resultat.potentiel,                 c_pot(resultat.potentiel)),
            ("📚 Soutien principal",    resultat.type_soutien_principal,    AVERT),
        ]:
            CarteKV(cc, titre, val, coul).pack(side="left", padx=(0, 12), pady=4, fill="y")

        BarreConfiance(corps, resultat.confiance).pack(fill="x", pady=(0, 14))

        # Soutiens complémentaires
        if resultat.soutiens_complements:
            cs = tk.Frame(corps, bg=CARD, padx=20, pady=14)
            cs.pack(fill="x", pady=(0, 14))
            tk.Label(cs, text="🔧  Soutiens complémentaires",
                     font=F_SOUS, bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0, 6))
            for s in resultat.soutiens_complements:
                tk.Label(cs, text=f"  •  {s}", font=F_CORPS,
                         bg=CARD, fg=TEXTE).pack(anchor="w")

        # Diagnostic CS
        if etudiant.filiere_souhaitee.lower() == "informatique":
            cd = tk.Frame(corps, bg=CARD2, padx=20, pady=14)
            cd.pack(fill="x", pady=(0, 14))
            tk.Label(cd, text="🖥️  Diagnostic Informatique Détaillé",
                     font=F_SOUS, bg=CARD2, fg="#c8b0ff").pack(anchor="w", pady=(0, 10))

            pi = etudiant.profil_info
            noms = {
                "note_algo":          "Algorithmique",
                "note_programmation": "Programmation",
                "note_lecture_code":  "Lecture code",
                "note_structures":    "Structures données",
                "note_bdd":           "Bases de données",
                "note_reseau":        "Réseaux/Systèmes",
            }
            badges_cadre = tk.Frame(cd, bg=CARD2)
            badges_cadre.pack(fill="x", pady=(0, 10))
            for idx, (attr, nom) in enumerate(noms.items()):
                val = getattr(pi, attr, None)
                if val is not None:
                    r, c = divmod(idx, 3)
                    if val >= 12:
                        bg, fg, icone = BADGE_BON, TXT_BON, "✅"
                    elif val >= 8:
                        bg, fg, icone = BADGE_MOY, TXT_MOY, "⚠️"
                    else:
                        bg, fg, icone = BADGE_FAIB, TXT_FAIB, "🔴"
                    cell = tk.Frame(badges_cadre, bg=bg, padx=10, pady=6)
                    cell.grid(row=r, column=c, padx=6, pady=4, sticky="nsew")
                    tk.Label(cell, text=f"{icone} {nom}", font=("Segoe UI", 9, "bold"),
                             bg=bg, fg=fg).pack(anchor="w")
                    tk.Label(cell, text=f"Note : {val:.1f}/20", font=F_PETIT,
                             bg=bg, fg=fg).pack(anchor="w")

            if resultat.diagnostic_info:
                tk.Label(cd, text="Recommandations ciblées :",
                         font=("Segoe UI", 10, "bold"),
                         bg=CARD2, fg=TEXTE).pack(anchor="w", pady=(8, 4))
                for msg in resultat.diagnostic_info:
                    tk.Label(cd, text=f"  {msg}", font=F_CORPS,
                             bg=CARD2, fg=TEXTE, wraplength=860,
                             justify="left").pack(anchor="w", pady=2)
            else:
                has_data = any(getattr(pi, a, None) is not None for a in noms)
                if not has_data:
                    tk.Label(cd,
                             text="ℹ️  Aucune sous-compétence renseignée — "
                                  "remplissez le Profil Informatique pour un diagnostic détaillé.",
                             font=F_CORPS, bg=CARD2, fg=TEXTE_DIM).pack(anchor="w")
                else:
                    tk.Label(cd,
                             text="✅ Aucune lacune détectée — profil informatique équilibré",
                             font=F_CORPS, bg=CARD2, fg=TXT_BON).pack(anchor="w")

        # Trace du raisonnement
        ct = tk.Frame(corps, bg=CARD, padx=20, pady=14)
        ct.pack(fill="x", pady=(0, 14))
        tk.Label(ct, text="🔍  Trace du raisonnement (chaînage avant)",
                 font=F_SOUS, bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0, 6))
        zt = tk.Text(ct, height=6, font=F_MONO, bg=ENTREE, fg=TEXTE_DIM,
                     relief="flat", state="disabled", wrap="word")
        zt.pack(fill="x")
        zt.configure(state="normal")
        moteur = self.systeme.moteur
        for i, h in enumerate(moteur.historique_inferences, 1):
            zt.insert("end",
                f"[{i}] {h['regle_id']} → "
                f"Motivation={h['motivation'].value if h['motivation'] else '—'}  "
                f"Potentiel={h['potentiel'].value if h['potentiel'] else '—'}  "
                f"Orientation={h['orientation'] or '—'}  "
                f"Soutien={h['type_soutien'].value if h['type_soutien'] else '—'}\n")
        zt.configure(state="disabled")

        # Justification
        cj = tk.Frame(corps, bg=CARD, padx=20, pady=14)
        cj.pack(fill="x", pady=(0, 20))
        tk.Label(cj, text="💬  Justification de la décision",
                 font=F_SOUS, bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0, 6))
        tk.Label(cj, text=resultat.justification, font=F_CORPS,
                 bg=CARD, fg=TEXTE, wraplength=920, justify="left").pack(anchor="w")

    # ═════════════════ PAGE RAPPORT ═══════════════════════════════════════════

    def _page_rapport(self, parent):
        tk.Label(parent, text="Génération de rapport",
                 font=F_TITRE, bg=FOND, fg=TEXTE).pack(
                 anchor="w", padx=30, pady=(22, 5))
        cadre = tk.Frame(parent, bg=FOND)
        cadre.pack(padx=30, pady=10, fill="both", expand=True)

        self._cadre_stats = tk.Frame(cadre, bg=CARD, padx=25, pady=18)
        self._cadre_stats.pack(fill="x", pady=(0, 18))
        tk.Label(self._cadre_stats, text="📊  Statistiques de la session",
                 font=F_SOUS, bg=CARD, fg=ACCENT).pack(anchor="w")
        self._lbl_stats = tk.Label(self._cadre_stats,
                                    text="Aucune analyse effectuée.",
                                    font=F_CORPS, bg=CARD, fg=TEXTE_DIM)
        self._lbl_stats.pack(anchor="w", pady=(4, 0))
        self._lbl_session = tk.Label(self._cadre_stats, text="",
                                      font=F_PETIT, bg=CARD, fg=TEXTE_DIM)
        self._lbl_session.pack(anchor="w", pady=(2, 0))

        ce = tk.Frame(cadre, bg=FOND)
        ce.pack(fill="x")
        for texte, fmt, bg in [
            ("🌐  Exporter HTML", "html", ACCENT),
            ("📄  Exporter TXT",  "txt",  CARD),
            ("📦  Exporter JSON", "json", CARD),
        ]:
            tk.Button(ce, text=texte,
                      font=("Segoe UI", 10, "bold") if bg == ACCENT else F_CORPS,
                      bg=bg, fg="white" if bg == ACCENT else TEXTE,
                      relief="flat", padx=20, pady=12, cursor="hand2",
                      command=lambda f=fmt: self._exporter(f)).pack(side="left", padx=(0, 12))
        tk.Button(ce, text="🗑  Effacer l'historique",
                  font=F_CORPS, bg=CARD, fg=DANGER,
                  relief="flat", padx=20, pady=12, cursor="hand2",
                  command=self._effacer_historique).pack(side="left", padx=(20, 0))

        tk.Label(cadre, text="📋  Historique des étudiants analysés",
                 font=F_SOUS, bg=FOND, fg=TEXTE).pack(anchor="w", pady=(22, 6))
        cols = ("ID", "Nom", "Filière", "Motivation", "Potentiel", "Soutien", "Confiance")
        self._tbl_hist = ttk.Treeview(cadre, columns=cols, show="headings", height=10)
        for col in cols:
            self._tbl_hist.heading(col, text=col)
            self._tbl_hist.column(col, width=130, anchor="center")
        self._tbl_hist.pack(fill="both", expand=True)

    # ═════════════════ ACTIONS ════════════════════════════════════════════════

    # ── Sauvegarde / chargement de session ───────────────────────────────────

    def _sauvegarder_session(self):
        """Sauvegarde tous les résultats dans un fichier JSON local."""
        try:
            donnees = [r.exporter_json() for r in self.systeme.resultats]
            with open(FICHIER_SESSION, 'w', encoding='utf-8') as f:
                json.dump(donnees, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Session] Erreur de sauvegarde : {e}")

    def _charger_session(self):
        """Charge les résultats sauvegardés au démarrage de l'application."""
        if not os.path.exists(FICHIER_SESSION):
            return
        try:
            with open(FICHIER_SESSION, 'r', encoding='utf-8') as f:
                donnees = json.load(f)
            if not donnees:
                return
            for d in donnees:
                r = ResultatOrientation(
                    etudiant_id=d.get('etudiant_id', '—'),
                    etudiant_nom=d.get('etudiant_nom', '—'),
                    filiere_recommandee=d.get('filiere_recommandee', '—'),
                    type_soutien_principal=d.get('type_soutien_principal', '—'),
                    soutiens_complements=d.get('soutiens_complements', []),
                    diagnostic_info=d.get('diagnostic_info', []),
                    justification=d.get('justification', ''),
                    motivation_calculee=d.get('motivation_calculee', '—'),
                    potentiel=d.get('potentiel', '—'),
                    confiance=d.get('confiance', 0.0),
                )
                self.systeme.resultats.append(r)
                self._maj_historique(r)
            self._maj_stats()
            n = len(donnees)
            self._lbl_session.configure(
                text=f"💾  Session restaurée — {n} analyse(s) chargée(s) depuis la dernière utilisation.",
                fg=ACCENT2
            )
        except Exception as e:
            print(f"[Session] Erreur de chargement : {e}")

    def _effacer_historique(self):
        """Efface l'historique en mémoire et supprime le fichier de session."""
        if not self.systeme.resultats:
            messagebox.showinfo("Historique vide", "Il n'y a aucun résultat à effacer.")
            return
        confirmer = messagebox.askyesno(
            "Effacer l'historique",
            f"Voulez-vous supprimer les {len(self.systeme.resultats)} analyse(s) sauvegardée(s) ?\n"
            "Cette action est irréversible."
        )
        if not confirmer:
            return
        self.systeme.resultats.clear()
        for item in self._tbl_hist.get_children():
            self._tbl_hist.delete(item)
        self._lbl_stats.configure(
            text="Aucune analyse effectuée.", fg=TEXTE_DIM)
        self._lbl_session.configure(text="", fg=TEXTE_DIM)
        try:
            if os.path.exists(FICHIER_SESSION):
                os.remove(FICHIER_SESSION)
        except Exception as e:
            print(f"[Session] Erreur suppression : {e}")

    # ── helpers de validation ─────────────────────────────────────────────────
    @staticmethod
    def _lire_float(var: tk.StringVar, nom: str,
                    defaut: float, vmin: float, vmax: float) -> float:
        """
        Lit un float depuis une StringVar.
        - Si vide → retourne `defaut`.
        - Si non-numérique → lève ValueError avec un message clair.
        - Si hors [vmin, vmax] → lève ValueError avec les bornes.
        """
        raw = var.get().strip()
        if not raw:
            return defaut
        try:
            val = float(raw)
        except ValueError:
            raise ValueError(f"« {nom} » : entrez un nombre (valeur reçue : «{raw}»).")
        if not (vmin <= val <= vmax):
            raise ValueError(
                f"« {nom} » : la valeur {val} est hors de la plage [{vmin} – {vmax}]."
            )
        return val

    @staticmethod
    def _lire_int(var: tk.StringVar, nom: str,
                  defaut: int, vmin: int, vmax: int) -> int:
        raw = var.get().strip()
        if not raw:
            return defaut
        try:
            val = int(float(raw))   # accepte "4.0" aussi
        except ValueError:
            raise ValueError(f"« {nom} » : entrez un entier (valeur reçue : «{raw}»).")
        if not (vmin <= val <= vmax):
            raise ValueError(
                f"« {nom} » : la valeur {val} est hors de la plage [{vmin} – {vmax}]."
            )
        return val

    def _analyser(self):
        try:
            # ── Sous-compétences informatiques ────────────────────────────────
            profil = ProfilInformatique()
            NOMS_PROFIL = {
                'note_algo':          'Algorithmique',
                'note_programmation': 'Programmation',
                'note_lecture_code':  'Lecture / Compréhension',
                'note_structures':    'Structures de données',
                'note_bdd':           'Bases de données / SQL',
                'note_reseau':        'Réseaux / Systèmes',
            }
            if self._champs.get('filiere_souhaitee', tk.StringVar()).get().lower() == "informatique":
                for attr, var in self._profil_vars.items():
                    raw = var.get().strip()
                    if raw:
                        val = self._lire_float(var, NOMS_PROFIL.get(attr, attr),
                                               defaut=None, vmin=0, vmax=20)
                        setattr(profil, attr, val)

            # ── Champs obligatoires ───────────────────────────────────────────
            moyenne      = self._lire_float(self._champs['moyenne'],
                                            'Moyenne générale', defaut=None, vmin=0, vmax=20)
            note_math    = self._lire_float(self._champs['note_math'],
                                            'Note Mathématiques', defaut=None, vmin=0, vmax=20)
            note_info    = self._lire_float(self._champs['note_info'],
                                            'Note Informatique', defaut=None, vmin=0, vmax=20)
            attendance   = self._lire_float(self._champs['attendance_rate'],
                                            'Taux de présence', defaut=None, vmin=0, vmax=100)
            study_hours  = self._lire_float(self._champs['study_hours'],
                                            'Heures d\'étude', defaut=None, vmin=0, vmax=168)
            participation = self._lire_int(self._champs['participation_score'],
                                           'Score de participation', defaut=None, vmin=1, vmax=5)

            # Vérifier que les champs obligatoires ne sont pas vides
            manquants = []
            if moyenne     is None: manquants.append('Moyenne générale')
            if note_math   is None: manquants.append('Note Mathématiques')
            if note_info   is None: manquants.append('Note Informatique')
            if attendance  is None: manquants.append('Taux de présence')
            if study_hours is None: manquants.append('Heures d\'étude')
            if participation is None: manquants.append('Score de participation')
            if manquants:
                messagebox.showerror(
                    "Champs manquants",
                    "Veuillez remplir les champs suivants :\n\n"
                    + "\n".join(f"  •  {m}" for m in manquants)
                )
                return

            etudiant = Etudiant(
                id=self._champs['id'].get().strip() or "E001",
                nom=self._champs['nom'].get().strip() or "Inconnu",
                prenom=self._champs['prenom'].get().strip() or "Étudiant",
                moyenne=moyenne,
                note_math=note_math,
                note_info=note_info,
                filiere_souhaitee=self._champs['filiere_souhaitee'].get().strip() or "Informatique",
                attendance_rate=attendance,
                study_hours=study_hours,
                homework_completion=self._champs['homework_completion'].get() == "Oui",
                participation_score=participation,
                capacite_travail=NiveauCapacite(self._champs['capacite_travail'].get()),
                disponibilite_soutien=self._champs['disponibilite_soutien'].get() == "Oui",
                profil_info=profil,
            )
        except ValueError as e:
            messagebox.showerror("Erreur de saisie", str(e))
            return

        bdf = BaseDeFaits(etudiant=etudiant)
        moteur = MoteurInference()
        resultat = moteur.raisonner(bdf)

        self.systeme.moteur = moteur
        self.systeme.resultats.append(resultat)

        self._afficher_resultats(etudiant, bdf, resultat)
        self._maj_historique(resultat)
        self._maj_stats()
        self._sauvegarder_session()

        diag_info = (f" | {len(resultat.diagnostic_info)} diagnostic(s) CS"
                     if resultat.diagnostic_info else "")
        self._lbl_statut.configure(
            text=(f"✓ Analyse terminée — Orientation : {resultat.filiere_recommandee}"
                  f" | Soutien : {resultat.type_soutien_principal}{diag_info}"),
            fg=ACCENT2
        )
        self._afficher_onglet("resultats")

    def _charger_exemple(self):
        """Exemple : étudiant Info qui lit le code mais ne peut pas l'écrire."""
        ex = {
            'id': 'E001', 'nom': 'Bensalem', 'prenom': 'Amira',
            'moyenne': '11', 'note_math': '8', 'note_info': '10',
            'filiere_souhaitee': 'Informatique',
            'attendance_rate': '85', 'study_hours': '12',
            'participation_score': '4',
            'homework_completion': 'Oui',
            'capacite_travail': 'élevée',
            'disponibilite_soutien': 'Oui',
        }
        for cle, val in ex.items():
            if cle in self._champs:
                self._champs[cle].set(val)
        pi_ex = {
            'note_algo':          '6',
            'note_programmation': '7',
            'note_lecture_code':  '13',
            'note_structures':    '8',
            'note_bdd':           '7',
            'note_reseau':        '',
        }
        for cle, val in pi_ex.items():
            if cle in self._profil_vars:
                self._profil_vars[cle].set(val)
        self._toggle_profil_info()
        self._lbl_statut.configure(
            text="Exemple chargé — lancez l'analyse pour voir le diagnostic CS",
            fg=AVERT)

    def _effacer(self):
        for var in self._champs.values():
            if hasattr(var, 'set'):
                var.set("")
        for var in self._profil_vars.values():
            var.set("")
        self._lbl_statut.configure(text="", fg=TEXTE)

    def _maj_historique(self, resultat):
        self._tbl_hist.insert("", "end", values=(
            resultat.etudiant_id,
            resultat.etudiant_nom,
            resultat.filiere_recommandee,
            resultat.motivation_calculee,
            resultat.potentiel,
            resultat.type_soutien_principal,
            f"{resultat.confiance*100:.0f}%"
        ))

    def _maj_stats(self):
        n = len(self.systeme.resultats)
        if n == 0:
            return
        moy = sum(r.confiance for r in self.systeme.resultats) / n * 100
        self._lbl_stats.configure(
            text=f"Étudiants analysés : {n}  |  Confiance moyenne : {moy:.1f}%",
            fg=TEXTE
        )
        self._lbl_session.configure(
            text=f"💾  Sauvegarde automatique activée — fichier : session_resultats.json",
            fg=TEXTE_DIM
        )

    def _exporter(self, fmt: str):
        if not self.systeme.resultats:
            messagebox.showwarning("Aucun résultat",
                                   "Effectuez d'abord au moins une analyse.")
            return
        ext = {"html": "*.html", "txt": "*.txt", "json": "*.json"}
        fich = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(), ext[fmt])],
            title=f"Enregistrer le rapport {fmt.upper()}"
        )
        if fich:
            if fmt == "html":
                contenu = self.systeme._generer_rapport_html()
            elif fmt == "txt":
                contenu = self.systeme._generer_rapport_texte()
            else:
                contenu = json.dumps(self.systeme._generer_rapport_json(),
                                     ensure_ascii=False, indent=2)
            with open(fich, 'w', encoding='utf-8') as f:
                f.write(contenu)
            messagebox.showinfo("Export réussi", f"Rapport enregistré :\n{fich}")


def main():
    app = ApplicationSEOA()
    app.mainloop()


if __name__ == "__main__":
    main()
