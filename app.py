import streamlit as st
import textwrap
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
    [data-testid="stSidebar"] .stSlider label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Connexion PostgreSQL ──────────────────────────────────────────────────────
def get_connection():
    try:
        if "postgres" in st.secrets:
            # Connexion via les Secrets Streamlit Cloud (Supabase en ligne)
            return psycopg2.connect(
                host=st.secrets["postgres"]["host"],
                port=st.secrets["postgres"]["port"],
                dbname=st.secrets["postgres"]["dbname"],
                user=st.secrets["postgres"]["user"],
                password=st.secrets["postgres"]["password"]
            )
        else:
            # Connexion locale (développement sur ton PC)
            return psycopg2.connect(
                host="localhost",
                port=5432,
                dbname="sad_hpd",
                user="postgres",
                password="Sanoisbae1234$"
            )
    except Exception:
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
labels_heures = [f"{h}h" for h in heures]

# ── Système de connexion ──────────────────────────────────────────────────────
def verifier_connexion(login, mot_de_passe):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id_user, nom, role FROM utilisateur WHERE login=%s AND mot_de_passe=%s",
            (login, mot_de_passe)
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return {"id": result[0], "nom": result[1], "role": result[2]}
    return None

def creer_compte(nom, login, mot_de_passe):
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
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM utilisateur WHERE login=%s AND role='secretaire'", (login,))
        conn.commit()
        conn.close()

def get_secretaires():
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

    # CSS spécifique à la page de connexion (palette violette "Clinik")
    st.markdown(textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    .stApp { background:#F3F2FC !important; }
    [data-testid="stSidebar"] { display:none !important; }
    [data-testid="stHeader"] { background:transparent !important; }
    #MainMenu, footer { visibility:hidden; }

    .block-container { padding-top:2.2rem; padding-bottom:1rem; max-width:1000px; }

    html, body, [class*="css"] { font-family:'Inter', sans-serif; }

    /* -- PANNEAU GAUCHE (dégradé violet) -- */
    div[class*="st-key-sad_left"] {
        background:linear-gradient(135deg,#7C6BF0 0%,#4F5FE0 55%,#3B4CC7 100%);
        border-radius:28px;
        padding:2.1rem 1.9rem;
        position:relative;
        overflow:hidden;
        min-height:560px;
        box-shadow:0 25px 60px rgba(59,76,199,0.30);
    }
    div[class*="st-key-sad_left"]::before {
        content:"";
        position:absolute; width:230px; height:230px; border-radius:50%;
        background:rgba(255,255,255,0.08);
        top:-70px; right:-70px;
    }
    div[class*="st-key-sad_left"]::after {
        content:"";
        position:absolute; width:260px; height:260px; border-radius:50%;
        background:rgba(255,255,255,0.06);
        bottom:-110px; left:-90px;
    }

    /* -- PANNEAU DROIT (blanc) -- */
    div[class*="st-key-sad_right"] {
        background:white;
        border-radius:28px;
        padding:2.1rem 2.3rem;
        min-height:560px;
        box-shadow:0 25px 60px rgba(79,95,224,0.10);
    }

    /* Onglets -> pilules (Streamlit récent = react-aria-components) */
    div[class*="st-key-sad_right"] [data-testid="stTabs"] [role="tablist"],
    div[class*="st-key-sad_right"] .react-aria-TabList,
    div[class*="st-key-sad_right"] [data-baseweb="tab-list"] {
        background:#EAE8FB !important; border-radius:999px !important; padding:4px !important;
        gap:2px !important; display:inline-flex !important; border:none !important;
        width:fit-content !important;
    }
    div[class*="st-key-sad_right"] [role="tab"],
    div[class*="st-key-sad_right"] .react-aria-Tab,
    div[class*="st-key-sad_right"] [data-baseweb="tab"] {
        border-radius:999px !important; padding:8px 18px !important;
        color:#5B5A7A !important; font-weight:600 !important; font-size:0.85rem !important;
        border:none !important; background:transparent !important; box-shadow:none !important;
    }
    div[class*="st-key-sad_right"] [role="tab"][aria-selected="true"],
    div[class*="st-key-sad_right"] [role="tab"][data-selected],
    div[class*="st-key-sad_right"] .react-aria-Tab[data-selected],
    div[class*="st-key-sad_right"] [aria-selected="true"] {
        background:white !important; color:#4F5FE0 !important;
        box-shadow:0 2px 8px rgba(79,95,224,0.18) !important;
    }
    div[class*="st-key-sad_right"] [data-baseweb="tab-highlight"],
    div[class*="st-key-sad_right"] [data-baseweb="tab-border"] { display:none !important; }

    /* Champs de saisie */
    div[class*="st-key-sad_right"] .stTextInput input {
        background:#F3F2FC; border:1.5px solid #EAE8FB !important; border-radius:12px;
        padding:0.6rem 0.9rem; color:#1C1B3A;
    }
    div[class*="st-key-sad_right"] .stTextInput input:focus {
        border-color:#7C6BF0 !important; box-shadow:0 0 0 3px rgba(124,107,240,0.15);
    }
    div[class*="st-key-sad_right"] .stTextInput label p {
        color:#1C1B3A !important; font-weight:600 !important; font-size:0.85rem;
    }
    div[class*="st-key-sad_right"] .stCheckbox label p {
        color:#5B5A7A !important; font-size:0.8rem;
    }

    /* Bouton "Se connecter" */
    div[class*="st-key-sad_right"] .stButton button {
        background:linear-gradient(90deg,#7C6BF0,#4F5FE0);
        color:white; border:none; border-radius:12px; font-weight:700;
        padding:0.7rem 0; box-shadow:0 12px 28px rgba(79,95,224,0.35);
    }
    div[class*="st-key-sad_right"] .stButton button:hover { opacity:0.92; color:white; }
    div[class*="st-key-sad_right"] .stButton button p { color:white; }
    </style>
    """), unsafe_allow_html=True)

    col_out_l, col_center, col_out_r = st.columns([0.15, 3.7, 0.15])

    with col_center:
        col_left, col_right = st.columns([0.85, 1.15], gap="small")

        # ── PANNEAU GAUCHE ───────────────────────────────────────────────────
        with col_left:
            with st.container(key="sad_left"):
                left_html = (
'<div style="position:relative;z-index:2;">'
'<div style="display:flex;align-items:center;gap:0.6rem;">'
'<div style="width:44px;height:44px;border-radius:14px;background:rgba(255,255,255,0.18);'
'display:flex;align-items:center;justify-content:center;font-size:1.3rem;">👁️</div>'
'<div>'
'<div style="color:white;font-weight:700;font-size:1.1rem;font-family:\'Poppins\',sans-serif;">SAD — HPD</div>'
'<div style="color:rgba(255,255,255,0.75);font-size:0.75rem;">Service Ophtalmologie</div>'
'</div>'
'</div>'
'<div style="color:rgba(255,255,255,0.65);font-size:0.68rem;letter-spacing:1.2px;'
'margin-top:1.7rem;font-weight:600;">HÔPITAL PRINCIPAL DE DAKAR</div>'
'<div style="color:white;font-size:1.55rem;font-weight:700;line-height:1.25;'
'font-family:\'Poppins\',sans-serif;margin-top:0.35rem;">Voir plus loin,<br>soigner mieux.</div>'
'<div style="color:rgba(255,255,255,0.82);font-size:0.85rem;margin-top:0.6rem;line-height:1.5;">'
'Système d\'aide à la décision pour le suivi et la coordination du service d\'ophtalmologie.</div>'
'<div style="display:flex;justify-content:center;margin:1.9rem 0;">'
'<svg width="120" height="76" viewBox="0 0 120 76" fill="none">'
'<path d="M5 38C22 10 98 10 115 38C98 66 22 66 5 38Z" stroke="rgba(255,255,255,0.55)" stroke-width="2.5"/>'
'<circle cx="60" cy="38" r="15" stroke="rgba(255,255,255,0.7)" stroke-width="2.5"/>'
'<circle cx="60" cy="38" r="5.5" fill="rgba(255,255,255,0.9)"/>'
'</svg>'
'</div>'
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">'
'<div style="background:rgba(255,255,255,0.14);border-radius:12px;padding:0.7rem 0.8rem;">'
'<div style="color:white;font-weight:700;font-size:1.05rem;">420</div>'
'<div style="color:rgba(255,255,255,0.72);font-size:0.7rem;">Lits disponibles</div></div>'
'<div style="background:rgba(255,255,255,0.14);border-radius:12px;padding:0.7rem 0.8rem;">'
'<div style="color:white;font-weight:700;font-size:1.05rem;">24h/7j</div>'
'<div style="color:rgba(255,255,255,0.72);font-size:0.7rem;">Service ouvert</div></div>'
'<div style="background:rgba(255,255,255,0.14);border-radius:12px;padding:0.7rem 0.8rem;">'
'<div style="color:white;font-weight:700;font-size:1.05rem;">Niveau 3</div>'
'<div style="color:rgba(255,255,255,0.72);font-size:0.7rem;">Hôpital de référence</div></div>'
'<div style="background:rgba(255,255,255,0.14);border-radius:12px;padding:0.7rem 0.8rem;">'
'<div style="color:white;font-weight:700;font-size:1.05rem;">03</div>'
'<div style="color:rgba(255,255,255,0.72);font-size:0.7rem;">Médecins en service</div></div>'
'</div>'
'<div style="color:rgba(255,255,255,0.75);font-size:0.75rem;margin-top:1.6rem;">'
'📍 1, Avenue Nelson Mandela — Dakar-Plateau</div>'
'</div>'
                )
                st.markdown(left_html, unsafe_allow_html=True)

        # ── PANNEAU DROIT ────────────────────────────────────────────────────
        with col_right:
            with st.container(key="sad_right"):
                tab1, tab2 = st.tabs(["🧑 Espace Patient", "🔒 Connexion Personnel"])

                # -- Espace Patient --
                with tab1:
                    intro_html = (
'<div style="margin-top:0.7rem;">'
'<div style="font-family:\'Poppins\',sans-serif;font-weight:700;font-size:1.3rem;color:#1C1B3A;">Bienvenue</div>'
'<div style="color:#5B5A7A;font-size:0.85rem;margin-top:0.2rem;">'
'Suivez le temps d\'attente et les informations du service en temps réel.</div>'
'</div>'
                    )
                    st.markdown(intro_html, unsafe_allow_html=True)

                    r_public = calcul_mmc(5.0, 2.0, 3)
                    if r_public and r_public["stable"]:
                        wq_public = r_public["wq"]
                        if wq_public < 20:
                            bg, fg, label = "#E3FBF4", "#17C3A2", "Fluide"
                        elif wq_public < 40:
                            bg, fg, label = "#FFF6E5", "#F5A623", "Modéré"
                        else:
                            bg, fg, label = "#FDECEC", "#F0555F", "Chargé"

                        wait_html = (
f'<div style="background:{bg};border-radius:16px;padding:1.1rem 1.3rem;'
f'display:flex;justify-content:space-between;align-items:center;margin:1rem 0;">'
f'<div><div style="color:{fg};font-size:0.75rem;font-weight:600;">Temps d\'attente estimé</div>'
f'<div style="color:#1C1B3A;font-size:1.5rem;font-weight:700;font-family:\'Poppins\',sans-serif;">{wq_public:.0f} min</div></div>'
f'<div style="background:white;border-radius:999px;padding:0.3rem 0.8rem;display:flex;align-items:center;gap:0.4rem;">'
f'<span style="width:8px;height:8px;border-radius:50%;background:{fg};display:inline-block;"></span>'
f'<span style="color:{fg};font-size:0.8rem;font-weight:600;">{label}</span></div></div>'
                        )
                        st.markdown(wait_html, unsafe_allow_html=True)
                    else:
                        st.markdown(
'<div style="background:#FDECEC;border-radius:16px;padding:1.1rem 1.3rem;margin:1rem 0;">'
'<div style="color:#B32C36;font-size:0.85rem;font-weight:600;">'
'🔴 File actuellement saturée — affluence exceptionnelle.</div></div>',
                            unsafe_allow_html=True
                        )

                    infos = [
                        ("🕐", "Horaires du service", "Ouvert 24h/24, 7j/7"),
                        ("📍", "Adresse", "1, Avenue Nelson Mandela, Dakar-Plateau"),
                        ("📞", "Téléphone", "+221 33 839 50 00"),
                    ]
                    rows_html = ""
                    for icon, label, value in infos:
                        rows_html += (
f'<div style="display:flex;align-items:center;gap:0.8rem;padding:0.7rem 0;border-bottom:1px solid #F0EFFB;">'
f'<div style="width:34px;height:34px;border-radius:10px;background:#EAE8FB;'
f'display:flex;align-items:center;justify-content:center;font-size:0.95rem;">{icon}</div>'
f'<div><div style="color:#8E8CAE;font-size:0.7rem;">{label}</div>'
f'<div style="color:#1C1B3A;font-size:0.85rem;font-weight:600;">{value}</div></div></div>'
                        )
                    st.markdown(rows_html, unsafe_allow_html=True)

                # -- Connexion Personnel --
                with tab2:
                    login_intro_html = (
'<div style="margin-top:0.7rem;">'
'<div style="font-family:\'Poppins\',sans-serif;font-weight:700;font-size:1.3rem;color:#1C1B3A;">Connexion Personnel</div>'
'<div style="color:#5B5A7A;font-size:0.85rem;margin-top:0.2rem;">'
'Réservé au personnel soignant et administratif du service.</div>'
'</div>'
                    )
                    st.markdown(login_intro_html, unsafe_allow_html=True)

                    st.write("")
                    login_input = st.text_input("Identifiant", placeholder="ex. seck", key="login_in")
                    mdp_input = st.text_input("Mot de passe", type="password",
                                               placeholder="••••••••", key="mdp_in")

                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        st.checkbox("Se souvenir de moi", key="remember_me")
                    with col_b:
                        st.markdown(
'<div style="text-align:right;padding-top:0.55rem;">'
'<a href="#" style="color:#4F5FE0;font-size:0.8rem;text-decoration:none;font-weight:500;">'
'Mot de passe oublié ?</a></div>',
                            unsafe_allow_html=True
                        )

                    st.write("")
                    if st.button("Se connecter", type="primary", use_container_width=True):
                        if login_input and mdp_input:
                            user = verifier_connexion(login_input, mdp_input)
                            if user:
                                st.session_state.connecte = True
                                st.session_state.utilisateur = user["nom"]
                                st.session_state.role = user["role"]
                                st.success(f"✅ Bienvenue {user['nom']} !")
                                st.rerun()
                            else:
                                st.error("❌ Identifiant ou mot de passe incorrect !")
                        else:
                            st.warning("⚠️ Veuillez remplir tous les champs !")

        st.markdown(
'<div style="text-align:center;color:#8E8CAE;font-size:0.75rem;margin-top:1.2rem;">'
'SAD — HPD © 2026 · Hôpital Principal de Dakar</div>',
            unsafe_allow_html=True
        )

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

    st.markdown("""
    <div class="main-header">
        <div style='font-size:2.5rem;'>👁️</div>
        <div>
            <p class="main-title">Système d'Aide à la Décision — Service Ophtalmologie</p>
            <p class="main-subtitle">Hôpital Principal de Dakar · 1, Avenue Nelson Mandela · Dakar-Plateau</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    col1, col2, col3, col4 = st.columns(4)

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
            text=flux_horaire, textposition="outside"
        ))
        fig.update_layout(
            height=300, showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="#374151", size=11),
            xaxis=dict(gridcolor="#F3F4F6", tickfont=dict(color="#1A1A2E")),
            yaxis=dict(gridcolor="#F3F4F6", title="Patients/heure", tickfont=dict(color="#1A1A2E")),
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
            xaxis=dict(gridcolor="#F3F4F6", tickfont=dict(color="#1A1A2E")),
            yaxis=dict(gridcolor="#F3F4F6", title="Wq (minutes)", tickfont=dict(color="#1A1A2E")),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Liste du personnel médical</div>',
                    unsafe_allow_html=True)

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
        lambda_val = st.slider("λ — Arrivées (patients/heure)", 1.0, 20.0, 8.0, 0.5)
        st.caption(f"= {lambda_val/60:.2f} patients/minute")
    with col2:
        mu_val = st.slider("μ — Consultations (patients/heure/médecin)", 0.5, 4.0, 2.0, 0.5)
        st.caption(f"Durée moy. : {60/mu_val:.0f} min/consultation")
    with col3:
        c_val = st.slider("c — Nombre de médecins", 1, 9, 3)

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
                   tickmode="linear", tick0=1, dtick=1, tickfont=dict(color="#1A1A2E")),
        yaxis=dict(title="Wq (min)", gridcolor="#F3F4F6", tickfont=dict(color="#1A1A2E")),
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
