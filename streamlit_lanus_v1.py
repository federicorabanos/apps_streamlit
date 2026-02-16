import streamlit as st
import pandas as pd

# CONFIGURACIÓN CORRECTA
st.set_page_config(page_title="Scouting Proyecciones", layout="wide")

st.title("⚽ Proyector de Métricas y KPI")

# --- VALORES INICIALES (COEFICIENTES) ---
default_ligas = {
    'Torneo Clausura': 1.0,
    'Primera Nacional 2025': 0.5,
    'Liga de Primera 2025': 0.7,
    'Liga AUF Uruguaya 2025': 0.7,
    'Primera A, Clausura 2025': 0.9,
    'Primera A, Apertura 2025': 0.9,
    'Primera Division 2025': 0.5,
    'Brasileiro Serie A 2025': 1.0,
    'Brasileiro Serie B 2025': 0.6,
    'Liga 1 2025': 0.6
}

default_pos = {'D': 0.8, 'M': 0.9, 'F': 1.0}

# --- SIDEBAR: CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración")

# 1. Filtros de Jugadores
st.sidebar.subheader("Filtros de Jugadores")
min_minutos = st.sidebar.number_input("Minutos mínimos jugados", value=300, step=50)

# 2. Edición de Coeficientes
with st.sidebar.expander("Ajustar Coeficientes de Ligas"):
    edit_ligas = {}
    for liga, val in default_ligas.items():
        edit_ligas[liga] = st.number_input(f"{liga}", value=val, step=0.1)

with st.sidebar.expander("Ajustar Coeficientes de Posición"):
    edit_pos = {}
    for pos, val in default_pos.items():
        edit_pos[pos] = st.number_input(f"Posición {pos}", value=val, step=0.1)

# --- FUNCIÓN CORE ---
def proyectar_metricas_y_devolver_proyecciones(df, metricas, liga_destino, c_ligas, c_pos, minutos_corte):
    df = df.copy()
    
    # Aplicamos el filtro de minutos ingresado por el usuario
    df = df[(df['position'] != 'G') & (df['minutesPlayed'] >= minutos_corte)]

    for metrica in metricas:
        p90_col = f'{metrica}_p90'
        liga_med_col = f'{metrica}_p90_liga_prom'
        ratio_col = f'{metrica}_ratio_vs_liga'
        ratio_neutral_col = f'{metrica}_ratio_neutral'
        proj_col = f'{metrica}_proj_p90_en_{liga_destino}'

        # Cálculo p90
        df[p90_col] = df[metrica] / df['minutesPlayed'] * 90

        # Mediana por liga
        promedios = df.groupby('league')[p90_col].median().reset_index()
        promedios.columns = ['league', liga_med_col]
        df = df.merge(promedios, on='league')

        # Coeficientes
        df['coef_liga'] = df['league'].map(c_ligas).fillna(1)
        df['coef_pos'] = df['position'].map(c_pos).fillna(1)

        # Ratio
        df[ratio_col] = df[p90_col] / df[liga_med_col]
        df[ratio_neutral_col] = df[ratio_col] * df['coef_liga']

        # Proyección
        df_dest = df[df['league'] == liga_destino]
        if df_dest.empty:
            return pd.DataFrame()

        median_dest = df_dest.groupby('position')[p90_col].median().to_dict()

        def proyectar_fila(row):
            if row['league'] == liga_destino:
                return row[p90_col]
            med = median_dest.get(row['position'])
            if med is None: return 0
            return (row[ratio_neutral_col] / c_ligas.get(liga_destino, 1)) * med

        df[proj_col] = df.apply(proyectar_fila, axis=1)

    cols_proj = [f'{m}_proj_p90_en_{liga_destino}' for m in metricas]
    return df[['name', 'league', 'position', 'minutesPlayed'] + cols_proj]

# --- CARGA Y PROCESAMIENTO ---
uploaded_file = st.file_uploader("Cargar dataset de jugadores (CSV o Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)

    st.write("### Configuración de la Proyección")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        liga_dest = st.selectbox("Liga de Destino", df_raw['league'].unique())
    
    with col2:
        posiciones_disponibles = df_raw['position'].unique().tolist()
        if 'G' in posiciones_disponibles: posiciones_disponibles.remove('G')
        filtro_pos = st.multiselect("Filtrar por Posición", posiciones_disponibles, default=posiciones_disponibles)
    
    with col3:
        metricas_seleccionadas = st.multiselect(
            "Métricas a proyectar", 
            [c for c in df_raw.columns if c not in ['name', 'league', 'position', 'minutesPlayed']],
            default=None
        )

    if st.button("🚀 Generar Ranking KPI"):
        if not metricas_seleccionadas:
            st.warning("Selecciona al menos una métrica.")
        else:
            # Filtrar por posición antes de proyectar
            df_filtered = df_raw[df_raw['position'].isin(filtro_pos)]
            
            # Ejecutar proyección
            df_proyectado = proyectar_metricas_y_devolver_proyecciones(
                df_filtered, metricas_seleccionadas, liga_dest, edit_ligas, edit_pos, min_minutos
            )

            if not df_proyectado.empty:
                # Calcular Percentiles y KPI
                cols_proj = [f'{m}_proj_p90_en_{liga_dest}' for m in metricas_seleccionadas]
                
                for col in cols_proj:
                    df_proyectado[f'perc_{col}'] = df_proyectado[col].rank(pct=True) * 100
                
                df_proyectado['KPI_Final'] = df_proyectado[[f'perc_{c}' for c in cols_proj]].mean(axis=1)
                df_proyectado = df_proyectado.sort_values('KPI_Final', ascending=False)
                
                # Reordenar columnas: name, league, position, minutesPlayed, KPI_Final, resto
                columnas_base = ['name', 'league', 'position', 'minutesPlayed', 'KPI_Final']
                columnas_restantes = [col for col in df_proyectado.columns if col not in columnas_base]
                df_proyectado = df_proyectado[columnas_base + columnas_restantes]

                # Mostrar Tabla
                st.subheader(f"Top Jugadores Proyectados a {liga_dest}")
                st.dataframe(df_proyectado, use_container_width=True)

                # Botón de Descarga
                csv_data = df_proyectado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Tabla en CSV",
                    data=csv_data,
                    file_name=f"ranking_{liga_dest}.csv",
                    mime='text/csv'
                )
            else:
                st.error("No hay suficientes datos con los filtros aplicados para realizar la proyección.")