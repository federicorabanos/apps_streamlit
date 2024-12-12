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

st.set_page_config(page_title="Scatter plots - La Liga 2", page_icon=":bar_chart:", layout="wide")

@st.cache_data(persist = True)
def load_data():
    df = pd.read_csv("La Liga 2 - misc - player stats - 2024-12-11.csv")
    df_90 = pd.read_csv("La Liga 2 per 90.csv")
    return df, df_90

@st.cache_data(persist = True)
def scatter_plot(estadisticas, data, minutos, titulo,  per90, estadisticas0, estadisticas1, jugadores, posiciones):
    columna1 = estadisticas[0]
    columna2 = estadisticas[1]

    min_jugados = None
    min_jugados = int(minutos[0])
    data = data[(data['stats_Min'] >= min_jugados)]
    data = data[(data['stats_Pos'].isin(posiciones))]

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
    if jugadores:
        annotated_df = data[data['Player'].isin(jugadores)].reset_index(drop=True)
    else:
        annotated_df = data[data['annotated']].reset_index(drop=True)
    for index in range(annotated_df.shape[0]):
        texts += [
            ax.text(
                x=annotated_df[columna1].iloc[index], y=annotated_df[columna2].iloc[index],
                s=f"{annotated_df['Player'].iloc[index]}",
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

    fig_text(
        x = 0.09, y = 0.91, 
        s = f"Se muestran {cant_jugadores} jugadores con más de {min_jugados} minutos jugados. Estadísticas {tipo_estadisticas}.\nSolo se muestran los jugadores que tienen más de {estadisticas0[0]} {columna1} y más de {estadisticas1[0]} {columna2}.\n | La Liga 2",
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

df, df_90 = load_data()

st.title(":bar_chart: Plots La Liga 2")

st.sidebar.header("Filtros que quieras para tu gráfico:")

per90 = st.sidebar.checkbox('Estadísticas por 90 minutos?')
print(df_90)

if per90:
    data = df_90
    data.stats_Min = data.stats_Min.str.replace(',', '').astype(int)
    #minutos=(0,100000000)
else:
    data = df
    data.stats_Min = data.stats_Min.str.replace(',', '').astype(int)
    #minutos = st.sidebar.slider(
    #'Filtra por minutos jugados:',
    #data['stats_MP'].min(), data['stats_MP'].max(), (int(data['stats_MP'].min()), int(data['stats_MP'].max())))

try:
    columnas_grafico = data.drop(columns=['Unnamed: 0',
        'Player','stats_Pos', 'stats_Squad', 'stats_Comp', 'stats_Age', 'stats_Born',
        'shooting_Pos', 'shooting_Squad', 'shooting_Comp', 'shooting_Age', 'shooting_Born',
        'passing_Pos', 'passing_Squad', 'passing_Comp', 'passing_Age', 'passing_Born',
        'passing_types_Pos', 'passing_types_Squad', 'passing_types_Comp', 'passing_types_Age', 'passing_types_Born',
        'gca_Pos', 'gca_Squad', 'gca_Comp', 'gca_Age', 'gca_Born',
        'defense_Pos', 'defense_Squad', 'defense_Comp', 'defense_Age', 'defense_Born',
        'possession_Pos', 'possession_Squad', 'possession_Comp', 'possession_Age', 'possession_Born',
        'playingtime_Pos', 'playingtime_Squad', 'playingtime_Comp', 'playingtime_Age', 'playingtime_Born',
        'misc_Pos', 'misc_Squad', 'misc_Comp', 'misc_Age', 'misc_Born', 'stats_Nation',
        'shooting_Nation', 'passing_Nation', 'passing_types_Nation', 'gca_Nation', 'defense_Nation', 'possession_Nation', 'playingtime_Nation', 'misc_Nation'
    ]
    )
except KeyError:
    columnas_grafico = data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.3', 'Unnamed: 0.2',
        'Player','stats_Pos', 'stats_Squad', 'stats_Comp', 'stats_Age', 'stats_Born', 'stats_Nation'
    ]
    )

print(columnas_grafico)

estadisticas = None
estadisticas = st.sidebar.multiselect(
    "Elegí 2 (solo toma las primeras dos)\nestadísticas para visualizar:",
    options=columnas_grafico.keys(),
    default=list(columnas_grafico.keys())[0:2]
    )

jugadores = st.sidebar.multiselect(
    "Elegí jugadores\npara visualizar:",
    options=data.Player.unique(),
    default=list(data.Player.unique())[0:2]
    )

posiciones = st.sidebar.multiselect(
    "Elegí 1 o más posiciones:",
    options=data.stats_Pos.unique(),
    default=list(data.stats_Pos.unique())[0:1]
    )

print(estadisticas)

try:
    estadisticas0 = st.sidebar.slider(
        f'Filtra por {estadisticas[0]}:',
        float(columnas_grafico[estadisticas[0]].min()), float(columnas_grafico[estadisticas[0]].max()), (float(columnas_grafico[estadisticas[0]].min()), float(columnas_grafico[estadisticas[0]].max())))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')

try:
    estadisticas1 = st.sidebar.slider(
        f'Filtra por {estadisticas[1]}:',
        float(columnas_grafico[estadisticas[1]].min()), float(columnas_grafico[estadisticas[1]].max()), (float(columnas_grafico[estadisticas[1]].min()), float(columnas_grafico[estadisticas[1]].max())))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')
minutos = None
minutos = st.sidebar.slider(
    'Filtra por minutos jugados:',
    int(data['stats_Min'].min()), int(data['stats_Min'].max()), (int(data['stats_Min'].min()), int(data['stats_Min'].max())))

titulo = None
titulo = st.sidebar.text_input(
        "Cambia el título 👇",
        placeholder="Elegí tu título",
    )

try:
    st.pyplot(scatter_plot(estadisticas[0:2], data, minutos, titulo, per90, estadisticas0, estadisticas1, jugadores, posiciones))
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
