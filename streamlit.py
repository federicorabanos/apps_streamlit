import streamlit as st
import plotly.express as px
import pandas as pd
from mplsoccer import Bumpy, FontManager, add_image
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from highlight_text import fig_text
import json

colores = {
    'Argentinos Juniors':'#fb0b0e',
    'Arsenal': '#00CCFF',
    'Atlético Tucumán': '#62bcf1',
    'Banfield': '#03953f', 'Barracas Central':'#FF0000', 'Belgrano':'0099d4', 'Boca Juniors':'#103f79',
    'Central Córdoba (SdE)':'#000000', 'Colón':'#e1171d', 'Defensa y Justicia':'#008234', 'Estudiantes (LP)':'#e40b12',
    'Gimnasia y Esgrima (LP)':'#09446a', 'Godoy Cruz':'#002988', 'Huracán':'#ff0000', 'Independiente':'#e2001a', 'Instituto':'#ff0000',
    'Lanús':'#ab2a3e', "Newell's Old Boys":'#f42121', 'Platense':'#804000', 'Racing Club':'#029cdc', 'River Plate':'#eb192e',
    'Rosario Central':'#f5c513', 'San Lorenzo':'#273b56', 'Sarmiento (J)':'#255028', 'Talleres (C)':'#05173b', 'Tigre':'#0e0ad5', 'Unión':'#df1216',
    'Vélez Sarsfield':'#0a539c'

}

URL = 'https://github.com/google/fonts/blob/main/ofl/fjallaone/FjallaOne-Regular.ttf?raw=true'
robotto_regular = FontManager(URL)

with open("lpf2023_posc.json", "r") as archivo:
    lpf = json.load(archivo)

match_day = ["Fecha " + str(num) for num in range(1, 28)]


st.set_page_config(page_title="Posiciones de los equipos en la Liga Argentina 2022", page_icon=":bar_chart:", layout="wide")

st.sidebar.header("Elegí los equipos:")
equipos = st.sidebar.multiselect(
    "Elegí el equipo:",
    options=lpf.keys(),
    default=list(lpf.keys())[0]
)
highlight_dict = {equipo: colores.get(equipo, '') for equipo in equipos}

st.title(":bar_chart: Posiciones de los equipos en el Torneo Binance 2023")
st.markdown("##")

bumpy = Bumpy(
    background_color="#F6F6F6", scatter_color="#282A2C", line_color="#252525", label_color="#121212", # scatter and line colors
    rotate_xticks=90,  # rotate x-ticks by 90 degrees
    ticklabel_size=19, label_size=30,  # ticklable and label font-size
    scatter_primary='o',  # marker to be used
    show_right=True,  # show position on the rightside
    plot_labels=True,  # plot the labels
    alignment_yvalue=0.1,  # y label alignment
    alignment_xvalue=0.065  # x label alignment
)

# plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day,  # match-day or match-week
    y_list=np.linspace(1, 28, 28).astype(int),  # position value from 1 to 20
    values=lpf,  # values having positions for each team
    secondary_alpha=0.05,   # alpha value for non-shaded lines/markers
    highlight_dict=highlight_dict,  # team to be highlighted with their colors
    figsize=(16, 10),  # size of the figure
    x_label='Fecha', y_label='Posición',  # label name
    lw=2.5,   # linewidth of the connecting lines
    #ylim=(-0.41, 14),
    fontproperties=robotto_regular.prop   # fontproperties for ticklables/labels
)

# Titulos
def formatear_equipos(equipos):
    # Usar una comprensión de lista para formatear cada equipo
    equipos_formateados = [f"<{equipo}>" for equipo in equipos]
    
    # Usar join para combinar los equipos formateados en una cadena
    cadena_formateada = ', '.join(equipos_formateados)
    
    return cadena_formateada

resultado = formatear_equipos(equipos)

SUB_TITLE = f"Posiciones en el transcurso de la LPF 2023 de\n{resultado}"

def obtener_colores(equipos, colores):
    colores_equipos = [{"color": colores.get(equipo, '')} for equipo in equipos]
    return colores_equipos
colores_texto = obtener_colores(equipos, colores)

fig_text(
    0.09, 0.98, SUB_TITLE, color="#121212",
    highlight_textprops=colores_texto,
    size=26, fig=fig, fontproperties=robotto_regular.prop
)

URL2 = "rToIfopo_400x400-modified.png"
fdj_cropped2 = Image.open(URL2)
ax_image2 = add_image(
    fdj_cropped2, fig, left=0.92, bottom=0.91, width=0.085, height=0.085
)   # these values might differ when you are plotting

st.pyplot(fig)
