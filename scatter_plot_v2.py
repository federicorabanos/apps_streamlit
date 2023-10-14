import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as path_effects
import matplotlib.font_manager as fm
from highlight_text import fig_text, ax_text
from adjustText import adjust_text
import scipy.stats as stats
from matplotlib.offsetbox import (OffsetImage,AnnotationBbox)
from mplsoccer import FontManager, add_image
from mplsoccer import Pitch
import streamlit as st
import requests

from PIL import Image
import os
import io

st.set_page_config(page_title="Scatter plots - Liga Argentina", page_icon=":bar_chart:", layout="wide")

@st.cache_data
def load_data():
    headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'if-none-match': 'W/"4bebed6144"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    fields = [
    'goals',
    'yellowCards',
    'redCards',
    'groundDuelsWon',
    'groundDuelsWonPercentage',
    'aerialDuelsWon',
    'aerialDuelsWonPercentage',
    'successfulDribbles',
    'successfulDribblesPercentage'
    'tackles',
    'assists',
    'accuratePassesPercentage',
    'totalDuelsWon',
    'totalDuelsWonPercentage',
    'minutesPlayed',
    'wasFouled',
    'fouls',
    'dispossessed',
    'possesionLost',
    'appearances',
    'started',
    'saves',
    'cleanSheets',
    'savedShotsFromInsideTheBox',
    'savedShotsFromOutsideTheBox',
    'goalsConcededInsideTheBox',
    'goalsConcededOutsideTheBox',
    'highClaims',
    'successfulRunsOut',
    'punches',
    'runsOut',
    'accurateFinalThirdPasses',
    'bigChancesCreated',
    'accuratePasses',
    'keyPasses',
    'accurateCrosses',
    'accurateCrossesPercentage',
    'accurateLongBalls',
    'accurateLongBallsPercentage',
    'interceptions',
    'clearances',
    'dribbledPast',
    'bigChancesMissed',
    'totalShots',
    'shotsOnTarget',
    'blockedShots',
    'goalConversionPercentage',
    'hitWoodwork',
    'offsides'
    ]

    traduccion = {
    'goals': 'Goles',
    'yellowCards': 'Tarjetas Amarillas',
    'redCards': 'Tarjetas Rojas',
    'groundDuelsWon': 'Duelos en el suelo ganados',
    'groundDuelsWonPercentage': '% de duelos en el suelo ganados',
    'aerialDuelsWon': 'Duelos aereos ganados',
    'aerialDuelsWonPercentage': '% de duelos aereos ganados',
    'successfulDribbles': 'Amagues completados',
    'successfulDribblesPercentage': '% de amagues completados',
    'tackles': 'Entradas',
    'assists': 'Asistencias',
    'accuratePassesPercentage': '% de pases comp.',
    'totalDuelsWon': 'Duelos totales ganaods',
    'totalDuelsWonPercentage': '% de duelos ganados',
    'wasFouled': 'Faltas recibidas',
    'fouls': 'Faltas cometidas',
    'dispossessed': 'Despojado de la posesión',
    'possesionLost': 'Posesiones perdidas',
    'appearances': 'Partijos jugados',
    'started': 'Partidos como titular',
    'saves': 'Atajadas',
    'cleanSheets': 'Vallas invictas',
    'savedShotsFromInsideTheBox': 'Atajadas desde tiros dentro del area',
    'savedShotsFromOutsideTheBox': 'Atajadas desde tiros fuera del area',
    'goalsConcededInsideTheBox': 'Goles concedidos desde tiros dentro del area',
    'goalsConcededOutsideTheBox': 'Goles concedidos desde tiros fuera del area',
    'highClaims': 'Centros descolgados',
    'successfulRunsOut': 'Salidas completadas',
    'punches': 'Puñetazos',
    'runsOut': 'Salidas',
    'accurateFinalThirdPasses': 'Pases al últ. tercio completados',
    'bigChancesCreated': 'Grandes chances creadas',
    'accuratePasses': 'Pases completados',
    'keyPasses': 'Chances creadas',
    'accurateCrosses': 'Centros completados',
    'accurateCrossesPercentage': '% de centros completados',
    'accurateLongBalls': 'Pases largos completados',
    'accurateLongBallsPercentage': '% de pases largos completados',
    'interceptions': 'Intercepciones',
    'clearances': 'Despejes',
    'dribbledPast': 'Amagado',
    'bigChancesMissed': 'Grandes chances perdidas',
    'totalShots': 'Tiros totales',
    'shotsOnTarget': 'Tiros al arco',
    'blockedShots': 'Tiros bloqueados',
    'goalConversionPercentage': '% de conversión de goles',
    'hitWoodwork': 'Tiros a los palos',
    'offsides': 'Offsides'
    }

    fields_request = "%2C".join(f"{fields[i]}" for i in range(len(fields)))
    offsets = [0,100,200,300,400,500]
    df_total = pd.DataFrame()
    df_90 = pd.DataFrame()

    for offset in offsets:
        response = requests.get(f'https://api.sofascore.com/api/v1/unique-tournament/13475/season/47644/statistics?limit=100&order=-rating&offset={offset}&accumulation=total&fields={fields_request}&filters=appearances.GT.2%2Cposition.in.G~D~M~F', headers=headers)
        df_nuevo = pd.DataFrame(response.json()['results'])
        df_total = pd.concat([df_total, df_nuevo])
        df_total['jugador'] = df_total.player.apply(pd.Series)['name']
        df_total['equipo'] = df_total.team.apply(pd.Series)['name']

    for offset in offsets:
        response = requests.get(f'https://api.sofascore.com/api/v1/unique-tournament/13475/season/47644/statistics?limit=100&order=-rating&offset={offset}&accumulation=per90&fields={fields_request}&filters=appearances.GT.2%2Cposition.in.G~D~M~F', headers=headers)
        df_nuevo = pd.DataFrame(response.json()['results'])
        df_90 = pd.concat([df_90, df_nuevo])
        df_90['jugador'] = df_90.player.apply(pd.Series)['name']
        df_90['equipo'] = df_90.team.apply(pd.Series)['name']
    
    df_90.drop(columns=['minutesPlayed'],inplace=True)
    df_90['minutesPlayed'] = df_total['minutesPlayed']
    df_total = df_total.rename(columns=traduccion)
    df_90 = df_90.rename(columns=traduccion)
    return df_total, df_90

def scatter_plot(estadisticas, data, minutos, titulo, tag, per90, estadisticas0, estadisticas1):
    columna1 = estadisticas[0]
    columna2 = estadisticas[1]

    min_jugados = None
    min_jugados = int(minutos[0])
    data = data[(data['minutesPlayed'] >= min_jugados)]

    #percentil = 40
    #data = data[(data[columna1] >= np.percentile(data[columna1], percentil)) & (data[columna2] > np.percentile(data[columna2], percentil))]
    data = data[(data[columna1] >= estadisticas0[0]) & (data[columna1] <= estadisticas0[1])]
    data = data[(data[columna2] >= estadisticas1[0]) & (data[columna2] <= estadisticas1[1])]

    tipo_estadisticas = None
    if per90:
        tipo_estadisticas = 'por 90 minutos'
    else:
        tipo_estadisticas = 'totales'

    #if equipo != '':
    #    data = data[data['Squad'] == equipo]

    fig = plt.figure(figsize=(16,9))
    ax = plt.subplot()
    ax.grid(visible=True, ls='--', color='lightgrey')

    data['zscore'] = stats.zscore(data[columna1])*.4 + stats.zscore(data[columna2])*.6
    data['annotated'] = [True if x > data['zscore'].quantile(.8) else False for x in data['zscore']]

    ax.scatter(
        data[columna1], data[columna2], 
        c=data['zscore'], cmap='inferno',
        zorder=3, ec='grey', s=55, alpha=0.8)
        
    texts = []
    annotated_df = data[data['annotated']].reset_index(drop=True)
    for index in range(annotated_df.shape[0]):
        texts += [
            ax.text(
                x=annotated_df[columna1].iloc[index], y=annotated_df[columna2].iloc[index],
                s=f"{annotated_df['jugador'].iloc[index]}",
                path_effects=[path_effects.Stroke(linewidth=2, foreground=fig.get_facecolor()), 
                path_effects.Normal()], color='black',
                family='DM Sans', weight='bold'
            )
        ]

    adjust_text(texts, only_move={'points':'y', 'text':'xy', 'objects':'xy'})

    ax.set_xlabel(f'{columna1}')
    ax.set_ylabel(f'{columna2}')

    if titulo:
        texto_titulo = titulo
    else:
        texto_titulo = f"Estadísticas de {columna1} vs. {columna2}"
    fig_text(
    x = 0.09, y = .99, 
    s = texto_titulo,
    va = "bottom", ha = "left",
    fontsize = 22, color = "black", font = "DM Sans", weight = "bold"
    )

    cant_jugadores = None
    cant_jugadores = data.shape[0]
    if tag:
        tag_extra = f' - {tag} '
    else:
        tag_extra = f" "

    fig_text(
        x = 0.09, y = 0.91, 
        s = f"Se muestran {cant_jugadores} jugadores con más de {min_jugados} minutos jugados. Estadísticas {tipo_estadisticas}.\nSolo se muestran los jugadores que tienen más de {estadisticas0[0]} {columna1} y más de {estadisticas1[0]} {columna2}.\nVisualización por @LanusStats{tag_extra} | Copa de la Liga Argentina 2023",
        va = "bottom", ha = "left",
        fontsize = 13, color = "#5A5A5A", font = "Karla"
    )

    plt.savefig('archivo.png', bbox_inches='tight')

    return fig

font_path = "scatter_plot/assets/fonts"
for x in os.listdir(font_path):
    for y in os.listdir(f"{font_path}/{x}"):
        if y.split(".")[-1] == "ttf":
            fm.fontManager.addfont(f"{font_path}/{x}/{y}")
            try:
                fm.FontProperties(weight=y.split("-")[-1].split(".")[0].lower(), fname=y.split("-")[0])
            except Exception:
                continue

plt.style.use("scatter_plot/soc_base.mplstyle")
plt.rcParams['font.family'] = 'Karla'

df_total, df_90 = load_data()

st.title(":bar_chart: Arma tu propio scatter plot de la Copa de la Liga 2023. Por: @LanusStats")
st.markdown("##")
st.link_button("Revisa todo mi contenido! Twitter, YouTube y mucho más.", "https://linktr.ee/lanusstats")


st.sidebar.header("Filtros que quieras para tu gráfico:")

per90 = st.sidebar.checkbox('Estadísticas por 90 minutos?')

if per90:
    data = df_90
    #minutos=(0,100000000)
else:
    data = df_total
    #minutos = st.sidebar.slider(
    #'Filtra por minutos jugados:',
    #data['minutesPlayed'].min(), data['minutesPlayed'].max(), (int(data['minutesPlayed'].min()), int(data['minutesPlayed'].max())))

estadisticas = None
estadisticas = st.sidebar.multiselect(
    "Elegí 2 (solo toma las primeras dos)\nestadísticas para visualizar:",
    options=data.keys(),
    default=list(data.keys())[0:2]
    )

try:
    estadisticas0 = st.sidebar.slider(
        f'Filtra por {estadisticas[0]}:',
        float(data[estadisticas[0]].min()), float(data[estadisticas[0]].max()), (float(data[estadisticas[0]].min()), float(data[estadisticas[0]].max())))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')

try:
    estadisticas1 = st.sidebar.slider(
        f'Filtra por {estadisticas[1]}:',
        float(data[estadisticas[1]].min()), float(data[estadisticas[1]].max()), (float(data[estadisticas[1]].min()), float(data[estadisticas[1]].max())))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')
minutos = None
minutos = st.sidebar.slider(
    'Filtra por minutos jugados:',
    int(data['minutesPlayed'].min()), int(data['minutesPlayed'].max()), (int(data['minutesPlayed'].min()), int(data['minutesPlayed'].max())))

titulo = None
titulo = st.sidebar.text_input(
        "Cambia el título 👇",
        placeholder="Elegí tu título",
    )

tag = st.sidebar.text_input(
        "Agrega tu @ o nombre 👇",
        placeholder="Agrega el crédito",
    )

try:
    st.pyplot(scatter_plot(estadisticas[0:2], data, minutos, titulo, tag, per90, estadisticas0, estadisticas1))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')
except np.core._exceptions.UFuncTypeError as e:
    st.error('Elegí una estadística que sea númerica (Squad, Position y esas no son númericas).')
except NameError:
    st.error('Dale, selecciona 2. :point_left:')

img = io.BytesIO()
plt.savefig(img, format='png', bbox_inches='tight')

btn = st.download_button(
        label="Descarga imagen",
        data=img,
        file_name="imagen.png",
        mime="image/png "
      )

plt.close()
