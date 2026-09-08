# SAD — HPD : Système d'Aide à la Décision

Projet d'analyse et d'optimisation des temps d'attente au **Service d'Ophtalmologie de l'Hôpital Principal de Dakar (HPD)**.

---

## Presentation du projet

Ce systeme a ete developpe dans le cadre d'un projet de fin d'etudes en Statistique et Informatique Decisionnelle. Il permet d'analyser les flux de patients et de simuler des scenarios d'organisation pour reduire l'attente aux consultations.

Le travail s'appuie sur :
- Une enquete de satisfaction menée auprès de 100 patients
- Des entretiens avec le personnel medical du service
- Une modelisation mathematique basée sur la theorie des files d'attente (modele M/M/c)
- Une application web interactive sous Streamlit

---

## Fonctionnalités

- **Espace Patient** : consultation du temps d'attente estime en temps réel
- **Tableau de bord** : suivi des indicateurs clés (temps d'attente moyen, taux d'occupation, flux horaire)
- **Simulateur M/M/c** : test de scénarios d'affectation des médecins
- **Analyse de sensibilité** : evaluation de l'impact des variations d'effectif
- **Recommandations** : pistes d'amélioration organisationnelle

---

## Stack technique

- **Langage** : Python 3.11
- **Interface** : Streamlit
- **Base de données** : PostgreSQL (Supabase)
- **Modélisation** : Théorie des files d'attente (Erlang C)
- **Visualisation** : Plotly
- **Hébergement** : Streamlit Community Cloud

---

## Aperçu de l'application

### Espace Patient & Connexion
![Connexion](screenshots/login.png)

### Tableau de bord principal
![Tableau de bord](screenshots/tableaubord.png)

### Analyse du flux horaire
![Flux horaire](screenshots/flux.png)

### Taux d'utilisation
![Jauge d'utilisation](screenshots/jauge.png)

### Analyse de sensibilité
![Analyse de sensibilite](screenshots/analyse.png)

### Simulateur de files d'attente
![Simulateur](screenshots/simulateur.png)

---

## Installation locale

```bash
git clone [https://github.com/Maty725/sad-hpd.git](https://github.com/Maty725/sad-hpd.git)
cd sad-hpd
pip install -r requirements.txt
streamlit run app.py


## Structure du projet

sad-hpd/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── screenshots/
├── login.png
├── tableaubord.png
├── flux.png
├── jauge.png
├── analyse.png
└── simulateur.png


Auteure
Maty MBAYE