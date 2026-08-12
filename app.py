import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import psycopg2
import psycopg2.extras

# ── Configuration ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAD HPD — Ophtalmologie",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Style CSS Professionnel Médical ───────────────────────────────────────────
st.markdown("""
<style>
    /* Fond général blanc/gris clair */
    .stApp {
        background-color: #F0F2F5;
        color: #1A1A2E;
    }

    /* Sidebar bleu professionnel */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B3A6B 0%, #2563EB 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.95rem;
    }

    /* Header principal */
    .main-header {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .main-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1B3A6B;
        margin: 0;
    }
    .main-subtitle {
        font-size: 0.85rem;
        color: #6B7280;
        margin: 0;
    }

    /* Cartes blanches */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border: 1px solid #F0F0F0;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 4px solid #2563EB;
        margin-bottom: 0.5rem;
    }
    .kpi-card.green { border-left-color: #10B981; }
    .kpi-card.orange { border-left-color: #F59E0B; }
    .kpi-card.red { border-left-color: #EF4444; }
    .kpi-card.blue { border-left-color: #2563EB; }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1B3A6B;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Section titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1B3A6B;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-green { background: #D1FAE5; color: #065F46; }
    .badge-orange { background: #FEF3C7; color: #92400E; }
    .badge-red { background: #FEE2E2; color: #991B1B; }
    .badge-blue { background: #DBEAFE; color: #1E40AF; }
    .badge-purple { background: #EDE9FE; color: #5B21B6; }

    /* Info boxes */
    .info-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        color: #1E40AF;
    }
    .success-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        color: #065F46;
    }
    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        color: #92400E;
    }
    .danger-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        color: #991B1B;
    }

    /* Table style */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
    }

    /* Divider */
    hr { border-color: #E5E7EB; }

    /* Slider */
    .stSlider label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Connexion PostgreSQL ──────────────────────────────────────────────────────
def get_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="sad_hpd",
            user="postgres",
            password="Sanoisbae1234$"
        )
    except:
        return None

def get_medecins():
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM medecin ORDER BY grade, nom", conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_patients():
    conn = get_connection()
    if conn:
        df = pd.read_sql(
            "SELECT * FROM patient ORDER BY date_passage DESC, heure_arrivee",
            conn
        )
        conn.close()
        return df
    return pd.DataFrame()

# ── Fonctions M/M/c ───────────────────────────────────────────────────────────
def erlang_c(c, rho):
    if rho >= 1:
        return 1.0
    a = c * rho
    sum_terms = sum([(a**k) / math.factorial(k) for k in range(c)])
    last_term = (a**c) / (math.factorial(c) * (1 - rho))
    return last_term / (sum_terms + last_term)

def calcul_mmc(lambda_h, mu_h, c):
    if c <= 0 or mu_h <= 0 or lambda_h <= 0:
        return None
    rho = lambda_h / (c * mu_h)
    if rho >= 1:
        return {"stable": False, "rho": rho, "wq": float('inf'), "lq": float('inf')}
    ec = erlang_c(c, rho)
    wq_min = (ec / (c * mu_h * (1 - rho))) * 60
    lq = lambda_h * wq_min / 60
    w_min = wq_min + (60 / mu_h)
    return {"stable": True, "rho": rho, "wq": wq_min, "lq": lq, "w": w_min, "ec": ec}

# ── Données flux horaire ──────────────────────────────────────────────────────
heures = list(range(7, 20))
flux_horaire = [18, 22, 15, 10, 7, 5, 4, 6, 10, 12, 10, 7, 4]
# Heures affichées correctement
labels_heures = [f"{h}h" for h in heures]

# ── Système de connexion ──────────────────────────────────────────────────────
def verifier_connexion(login, mot_de_passe):
    """Vérifie les identifiants — PostgreSQL ou fallback"""
    # Identifiants de secours si PostgreSQL non disponible
    USERS_FALLBACK = {
        "seck": {"mot_de_passe": "Seck2026$", "nom": "Dr Amadou Seck", "role": "admin"},
        "marie": {"mot_de_passe": "Marie2026$", "nom": "Marie", "role": "secretaire"},
    }

    # Essai connexion PostgreSQL
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_user, nom, role FROM utilisateur WHERE login=%s AND mot_de_passe=%s",
                (login, mot_de_passe)
            )
            result = cur.fetchone()
            conn.close()
            if result:
                return {"id": result[0], "nom": result[1], "role": result[2]}
        except:
            conn.close()

    # Fallback sans PostgreSQL
    if login in USERS_FALLBACK:
        user = USERS_FALLBACK[login]
        if user["mot_de_passe"] == mot_de_passe:
            return {"id": 0, "nom": user["nom"], "role": user["role"]}

    return None

def creer_compte(nom, login, mot_de_passe):
    """Crée un nouveau compte secrétaire"""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO utilisateur (nom, login, mot_de_passe, role) VALUES (%s, %s, %s, 'secretaire')",
                (nom, login, mot_de_passe)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    return False

def supprimer_compte(login):
    """Supprime un compte secrétaire"""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM utilisateur WHERE login=%s AND role='secretaire'", (login,))
        conn.commit()
        conn.close()

def get_secretaires():
    """Récupère la liste des secrétaires"""
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT nom, login, role FROM utilisateur ORDER BY role", conn)
        conn.close()
        return df
    return pd.DataFrame()

# ── Initialisation session ────────────────────────────────────────────────────
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.utilisateur = None
    st.session_state.role = None

# ── PAGE DE CONNEXION ─────────────────────────────────────────────────────────
if not st.session_state.connecte:

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
    .stApp {{ background: #F3F2FC !important; }}
    [data-testid="stSidebar"] {{ display: none; }}

    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        padding: 2rem 1rem;
    }
    .login-card {
        display: flex;
        width: 100%;
        max-width: 900px;
        border-radius: 28px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(76,60,240,0.18);
        background: white;
    }

    /* Colonne gauche */
    .login-left {
        background: linear-gradient(135deg, #7C6BF0 0%, #4F5FE0 50%, #3B4CC7 100%);
        padding: 2.5rem 2rem;
        width: 45%;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    .login-left .circle1 {
        position: absolute; width: 220px; height: 220px;
        border-radius: 50%; background: rgba(255,255,255,0.07);
        top: -60px; right: -60px;
    }
    .login-left .circle2 {
        position: absolute; width: 160px; height: 160px;
        border-radius: 50%; background: rgba(255,255,255,0.05);
        bottom: 40px; left: -50px;
    }
    .login-logo { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .login-brand {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem; font-weight: 700;
        color: white; margin-bottom: 0.2rem;
    }
    .login-tagline {
        font-family: 'Poppins', sans-serif;
        font-size: 1rem; font-weight: 600;
        color: rgba(255,255,255,0.9);
        margin: 1.5rem 0 0.5rem 0;
    }
    .login-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem; color: rgba(255,255,255,0.75);
        line-height: 1.6; margin-bottom: 1.5rem;
    }
    .eye-illustration {
        text-align: center; font-size: 4rem;
        margin: 1rem 0; opacity: 0.9;
    }
    .stat-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 0.6rem; margin: 1rem 0;
    }
    .stat-card {
        background: rgba(255,255,255,0.12);
        border-radius: 12px; padding: 0.75rem;
        backdrop-filter: blur(10px);
    }
    .stat-val {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem; font-weight: 700; color: white;
    }
    .stat-lbl {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem; color: rgba(255,255,255,0.7);
        margin-top: 0.15rem;
    }
    .login-address {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem; color: rgba(255,255,255,0.65);
        margin-top: auto; padding-top: 1rem;
    }

    /* Colonne droite */
    .login-right {
        padding: 2.5rem 2rem;
        width: 55%;
        display: flex;
        flex-direction: column;
    }
    .tab-pills {
        display: flex; background: #EAE8FB;
        border-radius: 50px; padding: 4px;
        margin-bottom: 1.5rem;
    }
    .tab-pill {
        flex: 1; text-align: center;
        padding: 0.5rem; border-radius: 50px;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem; font-weight: 500;
        color: #5B5A7A; cursor: pointer;
        transition: all 0.2s;
    }
    .tab-pill.active {
        background: white;
        color: #3B4CC7; font-weight: 600;
        box-shadow: 0 2px 8px rgba(76,60,240,0.15);
    }

    /* Espace patient */
    .wait-card {
        background: #E3FBF4; border-radius: 16px;
        padding: 1.25rem; margin-bottom: 1rem;
        border-left: 4px solid #17C3A2;
    }
    .wait-status {
        font-family: 'Poppins', sans-serif;
        font-size: 1.3rem; font-weight: 700; color: #0E9B7F;
    }
    .wait-msg {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem; color: #5B5A7A; margin-top: 0.3rem;
    }
    .info-item {
        display: flex; align-items: center; gap: 0.75rem;
        margin: 0.6rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem; color: #1C1B3A;
    }
    .info-icon {
        width: 32px; height: 32px;
        background: #EAE8FB; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem; flex-shrink: 0;
    }

    /* Formulaire connexion */
    .form-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem; font-weight: 500;
        color: #1C1B3A; margin-bottom: 0.3rem;
        display: block;
    }
    .form-input {
        width: 100%; padding: 0.75rem 1rem;
        border: 1.5px solid #EAE8FB;
        border-radius: 12px; font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
        color: #1C1B3A; outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
        margin-bottom: 1rem;
    }
    .form-input:focus { border-color: #7C6BF0; }
    .btn-connect {
        width: 100%; padding: 0.875rem;
        background: linear-gradient(135deg, #7C6BF0, #3B4CC7);
        color: white; border: none; border-radius: 14px;
        font-family: 'Poppins', sans-serif;
        font-size: 1rem; font-weight: 600;
        cursor: pointer; margin-top: 0.5rem;
        box-shadow: 0 6px 20px rgba(76,60,240,0.3);
        transition: opacity 0.2s;
    }
    .btn-connect:hover { opacity: 0.92; }
    .form-footer {
        display: flex; justify-content: space-between;
        align-items: center; margin: 0.5rem 0;
        font-family: 'Inter', sans-serif; font-size: 0.8rem;
    }
    .form-footer a { color: #7C6BF0; text-decoration: none; }
    .error-msg {
        background: #FFF0F0; border: 1px solid #F0555F;
        border-radius: 10px; padding: 0.75rem 1rem;
        color: #F0555F; font-family: 'Inter', sans-serif;
        font-size: 0.85rem; margin-top: 0.5rem;
    }

    /* Cacher éléments Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # Calcul temps d'attente public
    r_pub = calcul_mmc(8.0, 2.0, 3)
    wq_pub = r_pub["wq"] if r_pub and r_pub["stable"] else 45
    if wq_pub < 20:
        wait_color = "#17C3A2"; wait_bg = "#E3FBF4"
        wait_icon = "🟢"; wait_msg = "Peu d'attente — Bon moment pour venir !"
    elif wq_pub < 40:
        wait_color = "#F5A623"; wait_bg = "#FFF8EC"
        wait_icon = "🟡"; wait_msg = "Attente modérée — Prévoyez du temps."
    else:
        wait_color = "#F0555F"; wait_bg = "#FFF0F0"
        wait_icon = "🔴"; wait_msg = "Forte affluence — Évitez si possible."

    st.markdown(f"""
    <div class="login-wrapper">
      <div class="login-card">

        <!-- COLONNE GAUCHE -->
        <div class="login-left">
          <div class="circle1"></div>
          <div class="circle2"></div>
          <div class="login-logo">👁️</div>
          <div class="login-brand">SAD — HPD</div>
          <div class="login-tagline">Voir plus loin, soigner mieux</div>
          <div class="login-desc">
            Système d'Aide à la Décision pour le service d'ophtalmologie
            de l'Hôpital Principal de Dakar. Analyse et réduction des
            temps d'attente par modélisation M/M/c.
          </div>
          <div class="eye-illustration">👁️‍🗨️</div>
          <div class="stat-grid">
            <div class="stat-card">
              <div class="stat-val">420</div>
              <div class="stat-lbl">Lits disponibles</div>
            </div>
            <div class="stat-card">
              <div class="stat-val">24h/7j</div>
              <div class="stat-lbl">Service ouvert</div>
            </div>
            <div class="stat-card">
              <div class="stat-val">Niv. 3</div>
              <div class="stat-lbl">Hôpital référence</div>
            </div>
            <div class="stat-card">
              <div class="stat-val">9</div>
              <div class="stat-lbl">Médecins</div>
            </div>
          </div>
          <div class="login-address">📍 1, Avenue Nelson Mandela, Dakar-Plateau</div>
        </div>

        <!-- COLONNE DROITE -->
        <div class="login-right">
          <div class="tab-pills">
            <div class="tab-pill active" id="tab-patient" onclick="showTab('patient')">🏥 Espace Patient</div>
            <div class="tab-pill" id="tab-connect" onclick="showTab('connect')">🔐 Connexion Personnel</div>
          </div>

          <!-- ESPACE PATIENT -->
          <div id="panel-patient">
            <div style="background:{wait_bg}; border-radius:16px; padding:1.25rem;
                 margin-bottom:1rem; border-left:4px solid {wait_color};">
              <div style="font-size:1.5rem;">{wait_icon}</div>
              <div style="font-family:Poppins,sans-serif; font-size:1.3rem;
                   font-weight:700; color:{wait_color};">
                Attente estimée : {wq_pub:.0f} min
              </div>
              <div style="font-family:Inter,sans-serif; font-size:0.82rem;
                   color:#5B5A7A; margin-top:0.3rem;">{wait_msg}</div>
            </div>
            <div class="info-item">
              <div class="info-icon">⏰</div>
              <span><b>Horaires :</b> Lundi – Vendredi · 7h00 – 17h00</span>
            </div>
            <div class="info-item">
              <div class="info-icon">📍</div>
              <span><b>Adresse :</b> 1, Avenue Nelson Mandela, Dakar-Plateau</span>
            </div>
            <div class="info-item">
              <div class="info-icon">📞</div>
              <span><b>Contact :</b> +221 33 839 50 00</span>
            </div>
          </div>

          <!-- ESPACE CONNEXION -->
          <div id="panel-connect" style="display:none;">
            <div style="font-family:Poppins,sans-serif; font-size:1.2rem;
                 font-weight:700; color:#1C1B3A; margin-bottom:0.25rem;">
              Bon retour 👋
            </div>
            <div style="font-family:Inter,sans-serif; font-size:0.85rem;
                 color:#5B5A7A; margin-bottom:1.5rem;">
              Connectez-vous pour accéder au tableau de bord
            </div>
            <form id="loginForm">
              <label class="form-label">Identifiant</label>
              <input class="form-input" type="text" id="loginInput"
                     placeholder="Entrez votre identifiant">
              <label class="form-label">Mot de passe</label>
              <input class="form-input" type="password" id="mdpInput"
                     placeholder="••••••••••">
              <div class="form-footer">
                <label style="display:flex;align-items:center;gap:6px;color:#5B5A7A;">
                  <input type="checkbox" style="accent-color:#7C6BF0;">
                  Se souvenir de moi
                </label>
                <a href="#">Mot de passe oublié ?</a>
              </div>
            </form>
            <div id="error-msg" style="display:none;" class="error-msg">
              ❌ Identifiant ou mot de passe incorrect !
            </div>
          </div>
        </div>
      </div>
    </div>

    <script>
    function showTab(tab) {{
      document.getElementById('panel-patient').style.display = tab === 'patient' ? 'block' : 'none';
      document.getElementById('panel-connect').style.display = tab === 'connect' ? 'block' : 'none';
      document.getElementById('tab-patient').className = 'tab-pill' + (tab === 'patient' ? ' active' : '');
      document.getElementById('tab-connect').className = 'tab-pill' + (tab === 'connect' ? ' active' : '');
    }}
    </script>
    """, unsafe_allow_html=True)

    # Bouton connexion Streamlit (sous le HTML)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_input = st.text_input("", placeholder="Identifiant", label_visibility="collapsed", key="login_key")
        mdp_input = st.text_input("", placeholder="Mot de passe", type="password", label_visibility="collapsed", key="mdp_key")
        if st.button("🔐 Se connecter", type="primary", use_container_width=True):
            if login_input and mdp_input:
                user = verifier_connexion(login_input, mdp_input)
                if user:
                    st.session_state.connecte = True
                    st.session_state.utilisateur = user["nom"]
                    st.session_state.role = user["role"]
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect !")
            else:
                st.warning("⚠️ Remplissez tous les champs !")

    st.stop()

# ── Sidebar (après connexion) ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1.5rem 0 1rem 0;'>
        <div style='font-size:2.5rem;'>👁️</div>
        <div style='font-size:1.1rem; font-weight:800; color:white; margin-top:0.5rem;'>
            SAD — HPD
        </div>
        <div style='font-size:0.75rem; color:rgba(255,255,255,0.7); margin-top:0.25rem;'>
            Service Ophtalmologie
        </div>
        <div style='background:rgba(255,255,255,0.15); border-radius:8px;
             padding:4px 12px; margin-top:0.75rem; display:inline-block;
             font-size:0.7rem; color:white;'>
            👤 {st.session_state.utilisateur}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Menu selon le rôle
    if st.session_state.role == "admin":
        pages_disponibles = ["🏠  Accueil", "📊  Tableau de bord", "👥  Équipe médicale",
                             "⚙️  Simulateur M/M/c", "💡  Recommandations", "👑  Administration"]
    else:
        pages_disponibles = ["🏠  Accueil", "📊  Tableau de bord", "👥  Équipe médicale",
                             "⚙️  Simulateur M/M/c", "💡  Recommandations"]

    page = st.radio(
        "Navigation",
        pages_disponibles,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<div style='color:rgba(255,255,255,0.8); font-size:0.85rem; font-weight:600;'>⚙️ Paramètres</div>",
                unsafe_allow_html=True)
    nb_medecins = st.slider("Médecins en service", 1, 9, 3)

    st.markdown("---")

    # Bouton déconnexion
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.connecte = False
        st.session_state.utilisateur = None
        st.session_state.role = None
        st.rerun()

    st.markdown("""
    <div style='color:rgba(255,255,255,0.5); font-size:0.7rem; text-align:center; margin-top:1rem;'>
        Mémoire fin d'études 2025–2026<br>
        [Nom du Candidat]<br>
        Hôpital Principal de Dakar
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 : ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Accueil":

    # Header
    st.markdown("""
    <div class="main-header">
        <div style='font-size:2.5rem;'>👁️</div>
        <div>
            <p class="main-title">Système d'Aide à la Décision — Service Ophtalmologie</p>
            <p class="main-subtitle">Hôpital Principal de Dakar · 1, Avenue Nelson Mandela · Dakar-Plateau</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs HPD
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card blue">
            <div class="kpi-icon">🏥</div>
            <div class="kpi-value">HPD</div>
            <div class="kpi-label">Hôpital de Référence</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card green">
            <div class="kpi-icon">🛏️</div>
            <div class="kpi-value">420</div>
            <div class="kpi-label">Lits disponibles</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card orange">
            <div class="kpi-icon">⏰</div>
            <div class="kpi-value">24h/7j</div>
            <div class="kpi-label">Service ophtalmologie</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card blue">
            <div class="kpi-icon">👁️</div>
            <div class="kpi-value">Niveau 3</div>
            <div class="kpi-label">Hôpital de référence</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 À propos du projet</div>', unsafe_allow_html=True)
        st.markdown("""
        Ce Système d'Aide à la Décision (SAD) a été développé dans le cadre d'un mémoire
        de fin d'études pour analyser et réduire les temps d'attente au service d'ophtalmologie
        de l'Hôpital Principal de Dakar.

        Il repose sur la **théorie des files d'attente** (modèle M/M/c), une base de données
        **PostgreSQL**, une simulation **Python/SimPy** et une interface web **Streamlit**.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Problèmes identifiés</div>', unsafe_allow_html=True)

        problemes = [
            ("🔴", "Temps d'attente élevés dès 7h le matin"),
            ("🔴", "Gestion manuelle des dossiers patients"),
            ("🟡", "Absence d'outils numériques de suivi"),
            ("🟡", "Patients qui repartent sans consultation (LWBS)"),
            ("🟡", "Affectation intuitive des médecins"),
        ]
        for icon, texte in problemes:
            st.markdown(f"**{icon}** {texte}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Objectifs du SAD</div>', unsafe_allow_html=True)
        objectifs = [
            "📊 Visualiser les flux en temps réel",
            "🧮 Calculer les indicateurs M/M/c",
            "🎯 Simuler des scénarios",
            "💡 Formuler des recommandations",
            "📈 Améliorer la qualité de service",
        ]
        for o in objectifs:
            st.markdown(f"✅ {o}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🛠️ Technologies</div>', unsafe_allow_html=True)
        techs = [
            ("🐍", "Python 3.11", "blue"),
            ("🗄️", "PostgreSQL 16", "green"),
            ("⚙️", "SimPy", "purple"),
            ("🌐", "Streamlit", "orange"),
        ]
        for icon, nom, couleur in techs:
            st.markdown(f'{icon} <span class="badge badge-{couleur}">{nom}</span>',
                        unsafe_allow_html=True)
            st.markdown("")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 : TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Tableau de bord":

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2rem;'>📊</div>
        <div>
            <p class="main-title">Tableau de bord — SAU Ophtalmologie</p>
            <p class="main-subtitle">Indicateurs clés de performance en temps réel</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    lambda_moy = 8.0
    mu_moy = 2.0
    res = calcul_mmc(lambda_moy, mu_moy, nb_medecins)

    wq = res["wq"] if res and res["stable"] else 999
    rho = res["rho"] * 100 if res else 0

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    # Textes lisibles selon les valeurs
    wq_texte = f"{wq:.0f} min" if wq < 999 else "Très élevé"
    wq_couleur = "green" if wq < 20 else "orange" if wq < 40 else "red"

    if rho < 65:
        rho_texte = "Normale 🟢"
        rho_couleur = "green"
    elif rho < 85:
        rho_texte = "Élevée 🟡"
        rho_couleur = "orange"
    else:
        rho_texte = "Critique 🔴"
        rho_couleur = "red"

    lq = res["lq"] if res and res["stable"] else 999
    if lq < 1:
        lq_texte = "Fluide 🟢"
        lq_couleur = "green"
    elif lq < 3:
        lq_texte = "Chargée 🟡"
        lq_couleur = "orange"
    else:
        lq_texte = "Saturée 🔴"
        lq_couleur = "red"

    with col1:
        st.markdown(f"""
        <div class="kpi-card {wq_couleur}">
            <div class="kpi-icon">⏱️</div>
            <div class="kpi-value">{wq_texte}</div>
            <div class="kpi-label">Temps d'attente moyen</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card {rho_couleur}">
            <div class="kpi-icon">👨‍⚕️</div>
            <div class="kpi-value">{rho_texte}</div>
            <div class="kpi-label">Charge des médecins</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card {lq_couleur}">
            <div class="kpi-icon">🚶</div>
            <div class="kpi-value">{lq_texte}</div>
            <div class="kpi-label">File d'attente</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-icon">👨‍⚕️</div>
            <div class="kpi-value">{nb_medecins}</div>
            <div class="kpi-label">Médecins en service</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Flux horaire des patients</div>',
                    unsafe_allow_html=True)
        couleurs_bar = ["#EF4444" if f > 16 else "#F59E0B" if f > 10 else "#10B981"
                        for f in flux_horaire]
        fig = go.Figure(go.Bar(
            x=labels_heures, y=flux_horaire,
            marker_color=couleurs_bar,
            text=flux_horaire, textposition="inside",
            textfont=dict(size=13, color="white", family="Times New Roman")
        ))
        fig.update_layout(
            height=300, showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="#374151", size=11),
            xaxis=dict(
                gridcolor="#F3F4F6",
                tickfont=dict(size=13, color="black", family="Times New Roman")
            ),
            yaxis=dict(
                gridcolor="#F3F4F6", title="Patients/heure",
                tickfont=dict(size=12, color="black", family="Times New Roman")
            ),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⏱️ Temps d\'attente par heure</div>',
                    unsafe_allow_html=True)
        wq_par_heure = []
        for flux in flux_horaire:
            r = calcul_mmc(flux, 2.0, nb_medecins)
            wq_par_heure.append(min(r["wq"], 90) if r and r["stable"] else 90)

        couleurs_line = ["#EF4444" if w > 40 else "#F59E0B" if w > 20 else "#10B981"
                         for w in wq_par_heure]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=labels_heures, y=wq_par_heure,
            mode="lines+markers",
            line=dict(color="#2563EB", width=2.5),
            marker=dict(size=8, color=couleurs_line),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"
        ))
        fig2.add_hline(y=20, line_dash="dash", line_color="#F59E0B",
                       annotation_text="Seuil alerte")
        fig2.add_hline(y=40, line_dash="dash", line_color="#EF4444",
                       annotation_text="Seuil critique")
        fig2.update_layout(
            height=300, showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="#374151", size=11),
            xaxis=dict(
                gridcolor="#F3F4F6",
                tickfont=dict(size=13, color="black", family="Times New Roman")
            ),
            yaxis=dict(
                gridcolor="#F3F4F6", title="Wq (minutes)",
                tickfont=dict(size=12, color="black", family="Times New Roman")
            ),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Légende
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="success-box">🟢 <b>Normal</b> : Wq &lt; 20 min</div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="warning-box">🟡 <b>Vigilance</b> : Wq 20–40 min</div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="danger-box">🔴 <b>Critique</b> : Wq &gt; 40 min</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 : ÉQUIPE MÉDICALE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥  Équipe médicale":

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2rem;'>👥</div>
        <div>
            <p class="main-title">Équipe médicale — Service Ophtalmologie HPD</p>
            <p class="main-subtitle">Personnel médical et paramédical du service</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_med = get_medecins()

    if not df_med.empty:
        # Stats équipe
        col1, col2, col3 = st.columns(3)
        with col1:
            chef = df_med[df_med['grade'] == 'Médecin Chef']
            st.markdown(f"""
            <div class="kpi-card blue">
                <div class="kpi-icon">👨‍⚕️</div>
                <div class="kpi-value">{len(df_med[df_med['grade'] == 'Médecin Chef'])}</div>
                <div class="kpi-label">Médecin Chef</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-icon">🩺</div>
                <div class="kpi-value">{len(df_med[df_med['grade'].isin(['Médecin', 'Interne'])])}</div>
                <div class="kpi-label">Médecins & Internes</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card orange">
                <div class="kpi-icon">🤝</div>
                <div class="kpi-value">{len(df_med[df_med['grade'] == 'Assistant'])}</div>
                <div class="kpi-label">Assistants</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tableau équipe
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Liste du personnel médical</div>',
                    unsafe_allow_html=True)

        # Badges par grade
        def format_grade(grade):
            if grade == "Médecin Chef":
                return f'<span class="badge badge-blue">{grade}</span>'
            elif grade == "Médecin":
                return f'<span class="badge badge-green">{grade}</span>'
            elif grade == "Interne":
                return f'<span class="badge badge-purple">{grade}</span>'
            else:
                return f'<span class="badge badge-orange">{grade}</span>'

        for _, row in df_med.iterrows():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            with col1:
                st.markdown(f"**#{row['id_medecin']}**")
            with col2:
                st.markdown(f"**{row['prenom']} {row['nom']}**")
            with col3:
                st.markdown(f"{row['specialite']}")
            with col4:
                st.markdown(format_grade(row['grade']), unsafe_allow_html=True)
            st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="warning-box">⚠️ Connexion à la base de données non disponible.</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 : SIMULATEUR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️  Simulateur M/M/c":

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2rem;'>⚙️</div>
        <div>
            <p class="main-title">Simulateur M/M/c</p>
            <p class="main-subtitle">Modélisation mathématique des files d'attente</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎛️ Paramètres du modèle</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<p style='color:#1B3A6B; font-weight:600; font-size:0.85rem;'>λ — Patients arrivant par heure</p>", unsafe_allow_html=True)
        lambda_val = st.slider("", 1.0, 20.0, 8.0, 0.5, key="lambda")
        st.caption(f"= {lambda_val/60:.2f} patients/minute")
    with col2:
        st.markdown("<p style='color:#1B3A6B; font-weight:600; font-size:0.85rem;'>μ — Patients consultés par heure par médecin</p>", unsafe_allow_html=True)
        mu_val = st.slider("", 0.5, 4.0, 2.0, 0.5, key="mu")
        st.caption(f"Durée moy. : {60/mu_val:.0f} min/consultation")
    with col3:
        st.markdown("<p style='color:#1B3A6B; font-weight:600; font-size:0.85rem;'>c — Nombre de médecins en service</p>", unsafe_allow_html=True)
        c_val = st.slider("", 1, 9, 3, key="c")

    st.markdown('</div>', unsafe_allow_html=True)

    res = calcul_mmc(lambda_val, mu_val, c_val)

    if not res or not res["stable"]:
        st.markdown(f"""
        <div class="danger-box">
        ❌ <b>Système INSTABLE</b> — ρ = {res['rho']:.2f} ≥ 1<br>
        Le nombre de patients dépasse la capacité de consultation !
        Augmenter le nombre de médecins.
        </div>
        """, unsafe_allow_html=True)
    else:
        rho_pct = res["rho"] * 100
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Wq moyen", f"{res['wq']:.1f} min")
        with col2:
            st.metric("📊 Taux utilisation", f"{rho_pct:.1f}%")
        with col3:
            st.metric("🚶 Patients en file", f"{res['lq']:.2f}")
        with col4:
            st.metric("🕐 Temps passage", f"{res['w']:.0f} min")

        # Jauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rho_pct,
            title={"text": "Taux d'utilisation ρ (%)",
                   "font": {"color": "#1B3A6B", "size": 14}},
            number={"font": {"color": "#2563EB", "size": 40}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2563EB"},
                "steps": [
                    {"range": [0, 65], "color": "#D1FAE5"},
                    {"range": [65, 85], "color": "#FEF3C7"},
                    {"range": [85, 100], "color": "#FEE2E2"}
                ],
                "threshold": {
                    "line": {"color": "#EF4444", "width": 3},
                    "thickness": 0.75, "value": 90
                }
            }
        ))
        fig_gauge.update_layout(
            height=280, paper_bgcolor="white",
            font={"color": "#374151"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        if rho_pct < 65:
            st.markdown('<div class="success-box">✅ Système bien dimensionné.</div>',
                        unsafe_allow_html=True)
        elif rho_pct < 85:
            st.markdown('<div class="warning-box">⚠️ Système sous pression — surveiller les pics.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-box">🔴 Système quasi-saturé — renforcer les effectifs !</div>',
                        unsafe_allow_html=True)

    # Analyse sensibilité
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📉 Analyse de sensibilité</div>',
                unsafe_allow_html=True)

    rows = []
    wq_vals = []
    for nb in range(1, 10):
        r = calcul_mmc(lambda_val, mu_val, nb)
        if r and r["stable"]:
            rho_pct = r["rho"] * 100
            wq = r["wq"]
            if rho_pct >= 85:
                situation = "🔴 Saturé"
            elif rho_pct >= 65:
                situation = "🟡 Acceptable"
            else:
                situation = "🟢 Bon"
            rows.append({
                "Nb médecins": nb,
                "Charge des médecins": f"{rho_pct:.0f}%",
                "Attente moyenne": f"{wq:.0f} min",
                "Situation": situation
            })
            wq_vals.append(min(wq, 120))
        else:
            rows.append({
                "Nb médecins": nb,
                "Charge des médecins": "Trop chargé",
                "Attente moyenne": "File sans fin",
                "Situation": "❌ Impossible"
            })
            wq_vals.append(None)

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(
        x=list(range(1, 10)), y=wq_vals,
        mode="lines+markers",
        line=dict(color="#2563EB", width=2.5),
        marker=dict(size=8, color="#2563EB"),
        connectgaps=False
    ))
    fig_s.add_hline(y=20, line_dash="dash", line_color="#F59E0B",
                    annotation_text="Cible 20 min")
    fig_s.update_layout(
        height=280, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#374151"),
        xaxis=dict(title="Nb médecins", gridcolor="#F3F4F6",
                   tickmode="linear", tick0=1, dtick=1),
        yaxis=dict(title="Wq (min)", gridcolor="#F3F4F6"),
        margin=dict(t=20)
    )
    st.plotly_chart(fig_s, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 : RECOMMANDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💡  Recommandations":

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2rem;'>💡</div>
        <div>
            <p class="main-title">Recommandations</p>
            <p class="main-subtitle">Scénarios d'optimisation pour le service d'ophtalmologie</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Scénarios
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Comparaison des scénarios simulés</div>',
                unsafe_allow_html=True)

    lambda_pic = 12.0
    mu_base = 2.0
    mu_amel = mu_base / 0.85

    configs = [
        ("Situation actuelle", 3, lambda_pic, mu_base),
        ("+ 1 médecin au pic", 4, lambda_pic, mu_base),
        ("+ 2 médecins au pic", 5, lambda_pic, mu_base),
        ("Triage amélioré", 3, lambda_pic, mu_amel),
        ("Scénario optimal", 5, lambda_pic, mu_amel),
    ]

    rows_sc, wq_sc, noms_sc = [], [], []
    for nom, c, lam, mu in configs:
        r = calcul_mmc(lam, mu, c)
        wq_v = r["wq"] if r and r["stable"] else 120
        wq_sc.append(wq_v)
        noms_sc.append(nom)
        rows_sc.append({
            "Scénario": nom,
            "Médecins": c,
            "Wq (min)": f"{wq_v:.1f}",
            "ρ (%)": f"{r['rho']*100:.0f}%" if r and r['stable'] else "—",
            "Évaluation": "🔴 Critique" if wq_v > 40 else
                          "🟡 À améliorer" if wq_v > 20 else "🟢 Bon"
        })

    st.dataframe(pd.DataFrame(rows_sc), use_container_width=True, hide_index=True)

    couleurs_sc = ["#6B7280", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]
    fig_rec = go.Figure(go.Bar(
        x=noms_sc, y=wq_sc, marker_color=couleurs_sc,
        text=[f"{w:.1f} min" for w in wq_sc], textposition="outside"
    ))
    fig_rec.add_hline(y=20, line_dash="dash", line_color="#EF4444",
                      annotation_text="Cible 20 min")
    fig_rec.update_layout(
        height=350, showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#374151"),
        xaxis=dict(gridcolor="#F3F4F6"),
        yaxis=dict(title="Wq (min)", gridcolor="#F3F4F6"),
        margin=dict(t=30)
    )
    st.plotly_chart(fig_rec, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Recommandations
    st.markdown('<div class="section-title">🎯 Recommandations prioritaires</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="success-box">
        <b>✅ Priorité 1 — Renforcement des effectifs dès 7h</b><br>
        Ouvrir des postes supplémentaires dès 7h le matin, heure
        de forte affluence. Applicable par réaménagement des plannings
        sans recrutement supplémentaire.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        <b>ℹ️ Priorité 3 — Filière dédiée cas urgents</b><br>
        Créer un circuit prioritaire pour les urgences ophtalmologiques
        graves, séparé de la file de consultations programmées.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="warning-box">
        <b>⚠️ Priorité 2 — Amélioration du triage</b><br>
        Former le personnel d'accueil à un triage plus rapide.
        Réduire la durée de triage permet de fluidifier
        significativement le circuit patient.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
        <b>💰 Budget estimatif</b><br>
        Total : <b>906 000 – 1 317 000 FCFA</b><br>
        (≈ 1 380 – 2 010 €)<br>
        Solution accessible grâce aux outils open source gratuits.
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE ADMINISTRATION (Admin uniquement)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👑  Administration":

    if st.session_state.role != "admin":
        st.error("❌ Accès refusé — réservé à l'administrateur !")
        st.stop()

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2rem;'>👑</div>
        <div>
            <p class="main-title">Administration du système</p>
            <p class="main-subtitle">Gestion des utilisateurs — Réservé à l'administrateur</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Liste des utilisateurs
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👥 Utilisateurs enregistrés</div>',
                unsafe_allow_html=True)

    df_users = get_secretaires()
    if not df_users.empty:
        for _, row in df_users.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.markdown(f"**{row['nom']}**")
            with col2:
                st.markdown(f"`{row['login']}`")
            with col3:
                badge = "badge-blue" if row['role'] == 'admin' else "badge-green"
                st.markdown(f'<span class="badge {badge}">{row["role"]}</span>',
                            unsafe_allow_html=True)
            with col4:
                if row['role'] != 'admin':
                    if st.button("🗑️", key=f"del_{row['login']}"):
                        supprimer_compte(row['login'])
                        st.success(f"✅ Compte {row['login']} supprimé !")
                        st.rerun()
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    # Créer un nouveau compte
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ Créer un nouveau compte secrétaire</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        new_nom = st.text_input("Nom complet", placeholder="Ex: Fatou Diallo")
    with col2:
        new_login = st.text_input("Identifiant", placeholder="Ex: fatou")
    with col3:
        new_mdp = st.text_input("Mot de passe", placeholder="Ex: Fatou2026$")

    if st.button("➕ Créer le compte", type="primary", use_container_width=True):
        if new_nom and new_login and new_mdp:
            if creer_compte(new_nom, new_login, new_mdp):
                st.success(f"✅ Compte créé pour {new_nom} !")
                st.rerun()
            else:
                st.error("❌ Cet identifiant existe déjà !")
        else:
            st.warning("⚠️ Remplissez tous les champs !")

    st.markdown('</div>', unsafe_allow_html=True)
