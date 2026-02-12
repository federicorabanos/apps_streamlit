import streamlit as st
import pandas as pd
import json
import ast
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from sofascore_api import SofaAPI

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scouting System", page_icon="⚽", layout="wide")

def parse_birth_and_age(ts):
    if pd.isna(ts): return pd.Series([pd.NaT, None])
    try:
        birth_date = pd.to_datetime(ts, unit="s")
        age = (pd.Timestamp.now() - birth_date).days // 365
        return pd.Series([birth_date.date(), age])
    except: return pd.Series([pd.NaT, None])

def send_email(subject, body, to_email, csv_path):
    user_email = "federabanos@gmail.com"
    app_password = "kcktfqcsfuzwkuar"
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = user_email, to_email, subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with open(csv_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{csv_path}"')
            msg.attach(part)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user_email, app_password)
            server.send_message(msg)
        return True
    except: return False

@st.cache_data
def load_leagues():
    try:
        # Palabras clave para excluir ligas femeninas
        exclude_keywords = ['women', 'feminines', 'feminino', 'feminina']
        
        with open('sofascore_leagues.json', 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
            
        leagues = {}
        for k, v in data.items():
            # Convertimos la clave a minúsculas para una comparación más segura
            k_lower = k.lower()
            
            # Verificamos si alguna palabra prohibida está en el nombre de la liga
            if any(word in k_lower for word in exclude_keywords):
                continue
                
            seasons = ast.literal_eval(v['seasons'])
            if seasons:
                leagues[k] = {"id": v['id'], "season_id": seasons[0]['id']}
                
        return leagues
    except Exception as e:
        st.error(f"Error cargando JSON: {e}")
        return {}

# --- UI ---
st.title("🚨 Scouting System - Alertas de jugadores")
leagues_config = load_leagues()

LEAGUE_GROUPS = {
    "Escandinavia": ["Norway Eliteserien", "Norway Norwegian 1st Division", "Denmark Danish Superliga", "Denmark Betinia Liga", "Finland Veikkausliiga", "Sweden Allsvenskan"],
    "Sudamerica": ["Argentina Liga Profesional de Fútbol", "Argentina Primera Nacional", "Brazil Brasileirão Betano", "Brazil Brasileirão Série B", "Uruguay Liga AUF Uruguaya", "Colombia Primera A, Apertura", "Chile Liga de Primera", "Ecuador LigaPro Serie A"],
    "Top 5 Europa": ["England Premier League", "Spain La Liga", "Germany Bundesliga", "Italy Serie A", "France Ligue 1"],
    "Fuera top 5": ["Portugal Liga Portugal Betclic", "Netherlands VriendenLoterij Eredivisie", "Belgium Pro League", "Croatia HNL", "Czech Republic Czech First League"]
}

with st.sidebar:
    group_sel = st.multiselect("Grupos de ligas:", list(LEAGUE_GROUPS.keys()))
    sel_leagues = st.multiselect("Ligas:", list(leagues_config.keys()))
    num_fechas = st.number_input("Fechas atrás:", 1, 10, 3)
    age_max = st.slider("Edad Máxima:", 15, 45, 21)
    value_max = st.number_input("Valor de mercado:", 0, 100000000, 1500000)
    min_diff = st.number_input("Rating Diff mín.:", 0.0, 5.0, 0.5)
    pos_filter = st.multiselect("Posiciones:", ["G", "D", "M", "F"], default=["D", "M", "F"])
    target_mail = st.text_input("Enviar a:", "federabanos@gmail.com")

# Partimos de las ligas elegidas manualmente
expanded_leagues = set(sel_leagues)

# Añadimos todas las ligas definidas en los grupos seleccionados
for g in group_sel:
    for liga in LEAGUE_GROUPS[g]:
        # Sólo agregamos si esa liga existe en leagues_config
        if liga in leagues_config:
            expanded_leagues.add(liga)

sel_leagues_expandidas = sorted(expanded_leagues)

if sel_leagues_expandidas:
    st.caption(
        "🔎 **Ligas incluidas en el análisis:** " +
        ", ".join(sel_leagues_expandidas)
    )
else:
    st.caption("No hay ligas seleccionadas todavía.")

if st.button("🚀 Iniciar proceso de scouting"):
    if not sel_leagues_expandidas:
        st.warning("Selecciona ligas.")
    else:
        sofa = SofaAPI()
        df_total = pd.DataFrame()
        
        with st.status("🔍 Procesando...", expanded=True) as status:
            log = st.empty()
            for idx, liga in enumerate(sel_leagues_expandidas):
                info = leagues_config[liga]
                res_fechas = sofa.sofascore_request(f"/unique-tournament/{info['id']}/season/{info['season_id']}/rounds")
                
                if 'currentRound' not in res_fechas: continue
                curr = res_fechas['currentRound']['round']

                for r in range(num_fechas):
                    rd = curr - r
                    if rd <= 0: break
                    
                    data_rd = sofa.sofascore_request(f"/unique-tournament/{info['id']}/season/{info['season_id']}/events/round/{rd}")
                    if 'events' not in data_rd or not data_rd['events']: continue
                    
                    # Fecha del partido
                    f_ts = data_rd['events'][0]['startTimestamp']
                    f_date = pd.to_datetime(f_ts, unit='s').date()
                    log.markdown(f"🏟️ **{liga}** | Ronda {rd} ({f_date})")

                    for ev in data_rd['events']:
                        lineups = sofa.sofascore_request(f"/event/{ev['id']}/lineups")
                        if 'home' not in lineups: continue

                        for side in ['home', 'away']:
                            players = lineups[side]['players']
                            pdf = pd.concat([pd.DataFrame(players), pd.DataFrame(players).player.apply(pd.Series)], axis=1)
                            pdf = pdf.loc[:, ~pdf.columns.duplicated()]
                            
                            if 'statistics' not in pdf.columns: continue
                            
                            pdf['rating'] = pdf['statistics'].apply(lambda x: x.get('rating') if isinstance(x, dict) else None)
                            pdf['rating_diff_team'] = pdf['rating'] - pdf['rating'].mean()
                            pdf['birth_country'] = pdf['country'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
                            pdf[['birth_date', 'age']] = pdf['dateOfBirthTimestamp'].apply(parse_birth_and_age)
                            pdf['fecha_partido'], pdf['id_league'] = f_date, liga
                            df_total = pd.concat([df_total, pdf], axis=0)

            status.update(label="✅ Análisis completo", state="complete", expanded=False)

        if not df_total.empty:
            df_total['value'] = df_total['proposedMarketValueRaw'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)
            filt = df_total[(df_total['age'] <= age_max) & 
                            (df_total['rating_diff_team'] >= min_diff) & 
                            (df_total['position'].isin(pos_filter)) &
                            (df_total['value'] <= value_max)]
            
            if not filt.empty:
                cols = ["fecha_partido", "name", "age", "value","position", "rating", "rating_diff_team", "birth_country","id_league"]
                st.dataframe(filt[cols], use_container_width=True)
                
                filt.to_csv("alerts.csv", index=False)
                if send_email("🚨 Reporte Scouting", f"Detectados {len(filt)} jugadores.", target_mail, "alerts.csv"):
                    st.success("📧 Email enviado.")
            else:
                st.info("Sin resultados para los filtros.")
