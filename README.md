# SAD — HPD : Système d'Aide à la Décision

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📋 Description

Système d'Aide à la Décision (SAD) développé dans le cadre d'un projet professionnel de fin d'études, visant à analyser et réduire les temps d'attente au **Service d'Ophtalmologie de l'Hôpital Principal de Dakar (HPD)**.

Le projet combine :
- Une **enquête de satisfaction** auprès de 100 patients
- Un **entretien avec le personnel médical** du service
- Une **modélisation mathématique** basée sur la théorie des files d'attente (modèle M/M/c, formule d'Erlang C)
- Une **application web interactive** pour visualiser les indicateurs et simuler des scénarios

## 🎯 Fonctionnalités

- **Espace Patient** : consultation du temps d'attente estimé en temps réel, sans connexion
- **Tableau de bord** : indicateurs clés de performance (temps d'attente moyen, taux d'utilisation des médecins, flux horaire)
- **Équipe médicale** : gestion et visualisation du personnel médical
- **Simulateur M/M/c** : test interactif de scénarios (nombre de médecins, taux d'arrivée, durée de consultation)
- **Recommandations** : pistes d'amélioration organisationnelle chiffrées
- **Administration** : gestion des comptes utilisateurs (réservé aux administrateurs)

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.11 |
| Interface web | Streamlit |
| Base de données | PostgreSQL (hébergée sur Supabase) |
| Modélisation | Théorie des files d'attente (Erlang, Kendall) |
| Visualisation | Plotly |
| Hébergement | Streamlit Community Cloud |

## 📊 Modèle mathématique

Le système utilise le modèle **M/M/c** pour calculer :
- **λ** (lambda) : taux d'arrivée des patients (patients/heure)
- **μ** (mu) : taux de service par médecin (consultations/heure)
- **c** : nombre de médecins disponibles
- **ρ** (rho) : taux d'utilisation = λ / (c × μ)
- **Wq** : temps d'attente moyen (formule d'Erlang C)

## 📸 Aperçu de l'application

### Espace Patient
![Espace patient](screenshots/login.png)

### Tableau de bord
![Tableau de bord](screenshots/tableaubord.png)

### Simulateur M/M/c
![Simulateur](screenshots/simulateur.png)

## 🚀 Installation locale

```bash
git clone https://github.com/Maty725/sad-hpd.git
cd sad-hpd
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Structure du projet


sad-hpd/
├── app.py # Application principale Streamlit
├── requirements.txt # Dépendances Python
├── screenshots/ # Captures d'écran de l'application
└── README.md


## 🌐 Démo en ligne

L'application est accessible à l'adresse : [sad-hpd-ophtalmologie.streamlit.app](https://sad-hpd-ophtalmologie.streamlit.app)

## 👤 Auteure

**Maty Mbaye** — Bachelor Statistique et Informatique Décisionnelle
Projet encadré par M. Khalidou Sy — BEM Dakar

## 📄 Licence

Projet académique — Hôpital Principal de Dakar, 2026
