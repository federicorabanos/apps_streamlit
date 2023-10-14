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
import pygsheets
import streamlit as st

from PIL import Image
import os

######################



######################

st.set_page_config(page_title="Scatter plots - Liga Argentina", page_icon=":bar_chart:", layout="wide")

@st.cache_data
def load_data():
    gc = pygsheets.authorize(service_file='C:/Users/Federico Rábanos/Documents/lanus stats/creds.json')
    sheet = gc.open('Data Copa de la Liga 2023 Fbref')
    data = sheet[0].get_as_df()
    data[['Edad', 'Días']] = data['Age'].str.split('-', expand=True).fillna(0).astype('int')

    return data

@st.cache_data
def download_image():
    plt.savefig('archivo.png', bbox_inches='tight')

def scatter_plot(estadisticas, data, minutos, titulo, edad, tag, per90):
    columna1 = estadisticas[0]
    columna2 = estadisticas[1]

    min_jugados = int(minutos[0])
    data = data[(data['Min'] >= min_jugados) & (data['Min'] < minutos[1])]

    data = data[(data['Edad'] >= edad[0]) & (data['Edad'] < edad[1])]

    percentil = 40
    data = data[(data[columna1] >= np.percentile(data[columna1], percentil)) & (data[columna2] > np.percentile(data[columna2], percentil))]

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

    cant_jugadores = data.shape[0]
    if tag:
        tag_extra = f' - {tag} '
    else:
        tag_extra = f" "

    fig_text(
        x = 0.09, y = 0.91, 
        s = f"Se muestran {cant_jugadores} jugadores con más de {min_jugados} minutos jugados. Estadísticas {tipo_estadisticas}.\nSolo se muestran los jugadores que en ambas estadísticas están por encima del percentil {percentil} y entre las edades de {edad[0]} - {edad[1]}.\nVisualización por @LanusStats{tag_extra}| Data: Fbref + @BeGriffis | Copa de la Liga Argentina 2023",
        va = "bottom", ha = "left",
        fontsize = 13, color = "#5A5A5A", font = "Karla"
    )

    download_image()

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

data = load_data()

st.title(":bar_chart: Arma tu propio scatter plot de la Copa de la Liga 2023. Por: @LanusStats")
st.markdown("##")
st.link_button("Revisa todo mi contenido! Twitter, YouTube y mucho más.", "https://linktr.ee/lanusstats")


st.sidebar.header("Filtros que quieras para tu gráfico:")

per90 = st.sidebar.checkbox('Estadísticas por 90 minutos?')

if per90:
    cols_per90 = [col for col in data.columns if 'Per90' in col]
    cols_to_keep = data.columns[:10]
    data = data[cols_to_keep].join(data[cols_per90]).join(data['Edad'])
    lista_default = list(data.keys())[10:12]
else:
    cols_to_drop = [col for col in data.columns if 'Per90' in col]
    data = data.drop(columns=cols_to_drop)
    lista_default = list(data.keys())[13:15]

estadisticas = None
estadisticas = st.sidebar.multiselect(
    "Elegí 2 (solo toma las primeras dos)\nestadísticas para visualizar:",
    options=data.keys(),
    default=lista_default
    )

minutos = st.sidebar.slider(
    'Filtra por minutos jugados:',
    data['Min'].min(), data['Min'].max(), (float(data['Min'].min()), float(data['Min'].max())))

edad = st.sidebar.slider(
    'Filtra por edad:',
    16, int(data['Edad'].max()), (16, int(data['Edad'].max())))

titulo = st.sidebar.text_input(
        "Cambia el título 👇",
        placeholder="Elegí tu título",
    )

tag = st.sidebar.text_input(
        "Agrega tu @ o nombre 👇",
        placeholder="Agrega el crédito",
    )

try:
    st.pyplot(scatter_plot(estadisticas[0:2], data, minutos, titulo, edad, tag, per90))
except IndexError:
    st.error('Tenes que elegir 2 estadísticas en el filtro. :point_left:')
except np.core._exceptions.UFuncTypeError as e:
    st.error('Elegí una estadística que sea númerica (Squad, Position y esas no son númericas).')

with open("archivo.png", "rb") as file:
    btn = st.download_button(
            label="Descarga imagen",
            data=file,
            file_name="imagen.png",
            mime="image/png "
          )
    
st.write('Aclaración: Hay casos de jugadores que Fbref no tiene las estadísitcas por error de subida de datos. Un ejemplo es Alan Lescano. Los nombres de las columnas pueden ser confusos, no las pude traducir todavía')
st.write('Pueden entrar en https://fbref.com/es/comps/905/Estadisticas-de-Copa-de-la-Liga-Profesional y ver que significa cada una')