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
from functools import lru_cache

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scouting Alerts", page_icon="⚽", layout="wide")

# --- FUNCIONES DE APOYO (HELPERS) ---
def parse_birth_and_age(ts):
    if pd.isna(ts):
        return pd.Series([pd.NaT, None])
    try:
        birth_date = pd.to_datetime(ts, unit="s", errors="coerce")
        if pd.isna(birth_date):
            return pd.Series([pd.NaT, None])
        today = pd.Timestamp("today").normalize()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        return pd.Series([birth_date, age])
    except Exception:
        return pd.Series([pd.NaT, None])

def send_email_with_attachment(subject, body, to_email, csv_path, user_email, app_password):
    msg = MIMEMultipart()
    msg["From"] = user_email
    msg["To"] = to_email
    msg["Subject"] = subject
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
    except Exception as e:
        st.error(f"Error al enviar el email: {e}")
        return False

@st.cache_data
def load_league_data():
    # 1. Verificar nombre exacto del archivo
    file_name = 'sofascore_leagues.json'
    
    try:
        # Abrimos con utf-8 para evitar el error de charmap (0x9d) que mencionaste antes
        with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
            data = json.load(f)
        
        processed_leagues = {}
        
        for league_name, info in data.items():
            try:
                # El campo 'seasons' viene como string: "[{'id': 1, ...}]"
                # ast.literal_eval es sensible a valores como 'null' o 'true' de JS.
                # Como tu string viene de un dump de Python, debería tener 'False' o 'None'.
                
                raw_seasons = info.get('seasons', '[]')
                
                # Limpieza de seguridad por si hay caracteres raros
                clean_seasons = raw_seasons.replace('\xa0', ' ').strip()
                
                seasons_list = ast.literal_eval(clean_seasons)
                
                if isinstance(seasons_list, list) and len(seasons_list) > 0:
                    first_season = seasons_list[0]
                    processed_leagues[league_name] = {
                        "id_liga": info.get('id'),
                        "id_temporada": first_season.get('id'),
                        "year": first_season.get('year')
                    }
            except Exception as e_inner:
                # Si una liga falla, que siga con las demás
                continue
                
        if not processed_leagues:
            st.error("El archivo se leyó pero no se pudo procesar ninguna liga. Revisa el formato interno.")
            
        return processed_leagues

    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: {file_name}. Asegúrate de que esté subido a GitHub en la raíz.")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"❌ Error de formato JSON: El archivo tiene una coma o paréntesis mal puesto. Detalle: {e}")
        return {}
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return {}
# --- INTERFAZ DE USUARIO ---
st.title("🚨 Alertas de Jugadores")

leagues_config = load_league_data()

with st.sidebar:
    st.header("1. Configuración")
    seleccionadas = st.multiselect("Ligas a analizar:", options=list(leagues_config.keys()))
    num_rondas = st.number_input("Cantidad de fechas a analizar (hacia atrás):", min_value=1, max_value=10, value=3)
    
    st.divider()
    st.header("2. Filtros de Scouting")
    age_limit = st.slider("Edad Máxima", 15, 40, 21)
    rating_diff_limit = st.number_input("Rating Diff Team mín.", 0.0, 5.0, 0.5, step=0.1)
    posiciones_filtro = st.multiselect("Filtrar por Posición:", options=["G", "D", "M", "F"], default=["G", "D", "M", "F"])
    
    st.divider()
    st.header("3. Destinatario")
    target_email = st.text_input("Email de destino", "federabanos@gmail.com")

# --- EJECUCIÓN ---
if st.button("🚀 Iniciar Proceso de Scouting"):
    if not seleccionadas:
        st.warning("Selecciona al menos una liga.")
    else:
        sofa = SofaAPI()
        df_total = pd.DataFrame()
        
        with st.status("🔍 Corriendo el proceso...", expanded=True) as status:
            progreso = st.progress(0)
            log_ejecucion = st.empty()

            for idx, nombre_liga in enumerate(seleccionadas):
                liga_info = leagues_config[nombre_liga]
                id_liga = liga_info['id_liga']
                id_temporada = liga_info['id_temporada']
                
                try:
                    fechas = sofa.sofascore_request(f"/unique-tournament/{id_liga}/season/{id_temporada}/rounds")
                    fecha_actual = fechas['currentRound']['round']
                except:
                    st.toast(f"Error en liga {nombre_liga}", icon="⚠️")
                    continue

                for r in range(0, num_rondas):
                    ronda_a_procesar = fecha_actual - r
                    if ronda_a_procesar <= 0: break
                    
                    log_ejecucion.markdown(f"⚽ **Liga:** {nombre_liga} | 📅 **Ronda:** {ronda_a_procesar}")
                    
                    data_fecha = sofa.sofascore_request(f"/unique-tournament/{id_liga}/season/{id_temporada}/events/round/{ronda_a_procesar}")
                    if not data_fecha or not data_fecha.get("events"): continue

                    ids_partidos = [e['id'] for e in data_fecha['events']]
                    fecha_timestamp = data_fecha['events'][0]['startTimestamp']
                    fecha_legible = pd.to_datetime(fecha_timestamp, unit='s').date()

                    for partido in ids_partidos:
                        data_partido = sofa.sofascore_request(f"/event/{partido}/lineups")
                        if not data_partido or "error" in data_partido: continue

                        for side in ['home', 'away']:
                            try:
                                players_raw = data_partido[side]['players']
                                side_df = pd.concat([
                                    pd.DataFrame(players_raw),
                                    pd.DataFrame(players_raw).player.apply(pd.Series)
                                ], axis=1)

                                if "statistics" not in side_df.columns: continue

                                side_df["rating"] = side_df["statistics"].apply(lambda x: x.get("rating") if isinstance(x, dict) else None)
                                side_df['rating_diff_team'] = side_df['rating'] - side_df['rating'].mean()
                                side_df = side_df.loc[:, ~side_df.columns.duplicated()]
                                
                                # Columnas adicionales pedidas
                                side_df["birth_country"] = side_df["country"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
                                side_df[["birth_date", "age"]] = side_df["dateOfBirthTimestamp"].apply(parse_birth_and_age)
                                side_df['id_league'] = nombre_liga
                                side_df['fecha_partido'] = fecha_legible
                                
                                df_total = pd.concat([df_total, side_df], axis=0)
                            except:
                                continue

                progreso.progress((idx + 1) / len(seleccionadas))
            status.update(label="✅ Extracción finalizada", state="complete", expanded=False)

        # --- FILTRADO FINAL ---
        if not df_total.empty:
            # Filtro por edad, rating y posiciones elegidas
            alerts_df = df_total[
                (df_total["age"] < age_limit) & 
                (df_total["rating_diff_team"] > rating_diff_limit) &
                (df_total["position"].isin(posiciones_filtro))
            ].drop_duplicates(subset=['id'])

            if not alerts_df.empty:
                st.subheader(f"📊 Prospectos Encontrados ({len(alerts_df)})")
                
                # Definimos columnas a mostrar
                cols_to_show = ["name", "age", "position", "fecha_partido", "rating", "rating_diff_team", "birth_country", "id_league"]
                st.dataframe(alerts_df[cols_to_show], use_container_width=True)

                with st.spinner("📧 Enviando reporte..."):
                    csv_path = "alerts_scouting.csv"
                    alerts_df.to_csv(csv_path, index=False)
                    send_email_with_attachment(
                        "🚨 Reporte Scouting U21",
                        f"Se adjuntan los {len(alerts_df)} jugadores filtrados.",
                        target_email,
                        csv_path,
                        st.secrets["EMAIL_USER"],
                        st.secrets["EMAIL_PASS"]
                    )
                st.success(f"Reporte enviado a {target_email}")
            else:
                st.info("No hay jugadores que coincidan con los filtros de búsqueda.")
        else:
            st.error("No se pudo obtener data de las ligas seleccionadas.")
