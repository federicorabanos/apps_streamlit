import streamlit as st
import plotly.express as px
import pandas as pd
from mplsoccer import Bumpy, FontManager, add_image
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from highlight_text import fig_text

from mplsoccer import Bumpy, FontManager, add_image
URL = 'https://github.com/google/fonts/blob/main/ofl/fjallaone/FjallaOne-Regular.ttf?raw=true'
robotto_regular = FontManager(URL)

#df o lo que se use
reserva = {'Lanús':[	2,
8,
9,
10,
10,
7,
8,
6,
4,
3,
2,
1,
2,
2],
}
match_day = ["Fecha " + str(num) for num in range(1, 26)]
season_dict = reserva
lpf2021= {'Aldosivi':[25,	14,	20,	13,	7,	10,	5,	8,	9,	15,	18,	21,	23,	24,	24,	22,	22,	20,	20,	22,	17,	15,	19,	15,	13],
'AAAJ':[16,	5,	14,	17,	15,	11,	8,	10,	11,	12,	13,	13,	11,	8,	13,	13,	11,	14,	15,	14,	15,	17,	16,	17,	14],
'Arsenal':[10,	23,	15,	20,	21,	23,	25,	26,	26,	26,	26,	26,	26,	26,	25,	25,	25,	26,	25,	26,	26,	26,	26,	26,	26],
'Atlético Tucumán':[24,	13,	8,	8,	14,	14,	16,	13,	7,	7,	10,	15,	19,	20,	21,	19,	19,	18,	19,	21,	23,	23,	25,	25,	25],
'Banfield':[10,	17,	11,	11,	15,	19,	19,	20,	24,	24,	25,	25,	21,	22,	23,	23,	24,	24,	24,	20,	22,	22,	20,	21,	20],
'Boca Juniors':[10,	17,	23,	23,	23,	24,	20,	14,	14,	9,	9,	8,	6,	9,	6,	3,	3,	5,	6,	6,	4,	5,	6,	7,	4],
'Central Córdoba ':[10,	21,	12,	15,	19,	21,	22,	24,	25,	25,	22,	24,	25,	25,	26,	26,	26,	25,	26,	25,	24,	24,	22,	20,	22],
'Colón':[5,	15,	16,	9,	4,	3,	7,	7,	8,	8,	8,	6,	9,	10,	8,	6,	7,	6,	7,	7,	7,	8,	8,	6,	7],
'DyJ':[21,	25,	24,	19,	22,	16,	15,	11,	10,	11,	12,	12,	16,	13,	12,	8,	8,	7,	5,	5,	3,	2,	3,	3,	2],
'Estudiantes':[1,	8,	17,	10,	5,	4,	3,	1,	6,	6,	4,	3,	3,	4,	3,	5,	6,	10,	8,	9,	8,	7,	5,	5,	6],
'GELP':[8,	16,	10,	14,	10,	13,	13,	18,	19,	23,	23,	17,	12,	16,	15,	14,	12,	12,	11,	11,	10,	10,	10,	11,	11],
'Godoy Cruz':[5,	3,	7,	12,	6,	12,	12,	15,	21,	13,	7,	10,	8,	7,	9,	10,	13,	11,	12,	13,	12,	14,	14,	13,	17],
'Huracán':[5,	11,	12,	15,	20,	18,	18,	19,	22,	16,	16,	18,	13,	12,	11,	12,	9,	8,	9,	10,	11,	11,	11,	10,	8],
'Independiente	':[16,	5,	2,	2,	1,	1,	1,	5,	3,	3,	5,	5,	5,	5,	7,	9,	10,	9,	10,	8,	9,	9,	9,	9,	9],
'Lanús':[2,	1,	4,	5,	2,	2,	6,	3,	2,	2,	2,	4,	4,	3,	4,	4,	4,	4,	3,	3,	6,	6,	7,	8,	10],
'Newells     	':[4,	10,	5,	6,	3,	9,	11,	12,	15,	17,	14,	14,	17,	19,	20,	21,	20,	22,	22,	19,	21,	18,	18,	19,	19],
'Patronato	    ':[3,	2,	6,	7,	8,	6,	10,	9,	13,	14,	20,	16,	20,	21,	22,	24,	23,	21,	21,	23,	20,	21,	24,	24,	23],
'Platense	    ':[8,	20,	24,	25,	26,	21,	22,	25,	23,	22,	24,	23,	24,	23,	19,	17,	17,	19,	16,	17,	18,	19,	17,	18,	18],
'Racing Club	    ':[16,	19,	9,	3,	9,	5,	2,	4,	5,	5,	6,	7,	10,	11,	10,	11,	14,	15,	17,	12,	14,	16,	15,	16,	15],
'River Plate	    ':[21,	7,	3,	4,	12,	7,	9,	6,	4,	4,	3,	2,	2,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1,	1],
'Rosario Central	':[21,	11,	19,	22,	25,	25,	26,	22,	18,	21,	15,	11,	14,	17,	17,	16,	16,	13,	14,	16,	13,	12,	12,	12,	16],
'San Lorenzo		':[10, 4,	1,	1,	11,	15,	17,	21,	16,	18,	17,	20,	15,	15,	18,	20,	21,	23,	23,	24,	25,	25,	23,	23,	21],
'Sarmiento (J)	':[26,	26,	21,	24,	17,	20,	14,	16,	20,	20,	19,	19,	22,	18,	14,	18,	18,	16,	18,	18,	19,	20,	21,	22,	24],
'Talleres (C)	':[20,	9,	17,	18,	13,	8,	4,	2,	1,	1,	1,	1,	1,	2,	2,	2,	2,	2,	2,	2,	2,	3,	2,	2,	3],
'Unión	        ':[10,	24,	26,	26,	18,	17,	22,	17,	12,	19,	21,	22,	18,	14,	16,	15,	15,	17,	13,	15,	16,	13,	13,	14,	12],
'Vélez Sarsfield	':[16,	22,	22,	21,	24,	26,	21,	23,	17,	10,	11,	9,	7,	6,	5,	7,	5,	3,	4,	4,	5,	4,	4,	4,	5]}

st.set_page_config(page_title="Posiciones de los equipos en la Liga Argentina 2022", page_icon=":bar_chart:", layout="wide")

st.sidebar.header("Please Filter Here:")
equipos = st.sidebar.multiselect(
    "Elegí el equipo:",
    options=lpf2021.keys(),
    default='Aldosivi'
)
valores_lista = list(np.where(equipos == [], None, equipos))
highlight_dict = {valores_lista[0]: "crimson"}

st.title(":bar_chart: Posiciones de los equipos en la Liga Argentina 2022")
st.markdown("##")

bumpy = Bumpy(
    background_color="#F6F6F6", scatter_color="#282A2C", line_color="#252525", label_color="#121212", # scatter and line colors
    rotate_xticks=90,  # rotate x-ticks by 90 degrees
    ticklabel_size=17, label_size=30,  # ticklable and label font-size
    scatter_primary='o',  # marker to be used
    show_right=True,  # show position on the rightside
    plot_labels=True,  # plot the labels
    alignment_yvalue=0.1,  # y label alignment
    alignment_xvalue=0.065  # x label alignment
)

# plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day,  # match-day or match-week
    y_list=np.linspace(1, 26, 26).astype(int),  # position value from 1 to 20
    values=lpf2021,  # values having positions for each team
    secondary_alpha=0.05,   # alpha value for non-shaded lines/markers
    highlight_dict=highlight_dict,  # team to be highlighted with their colors
    figsize=(16, 9),  # size of the figure
    x_label='', y_label='Posición',  # label name
    lw=2.5,   # linewidth of the connecting lines
    #ylim=(-0.41, 14),
    fontproperties=robotto_regular.prop   # fontproperties for ticklables/labels
)

# title and subtitle
TITLE = "Torneo de Reserva 2022"
SUB_TITLE = "Posiciones en el transcurso del campeonato de <Lanús> donde cosechó 25 puntos y terminó <campeón>"

# add title
fig.text(0.09, 0.99, TITLE, size=35, color="#121212", fontproperties=robotto_regular.prop)

# add subtitle
fig_text(
    0.09, 0.98, SUB_TITLE, color="#121212",
    highlight_textprops=[{"color": 'crimson'}, {"color": 'crimson'}],
    size=21, fig=fig, fontproperties=robotto_regular.prop
)

fig.text(0.09, 0.92, 'Goleador: Franco Orozco [4] - Más apariciones: Juan Martin Ginzo [17]', size=17, color="#121212", fontproperties=robotto_regular.prop)

URL = "png-transparent-club-atletico-lanus-superliga-argentina-de-futbol-logo-football-text-logo-sports.png"
fdj_cropped = Image.open(URL)
ax_image2 = add_image(
    fdj_cropped, fig, left=0.89, bottom=0.91, width=0.085, height=0.085
)   # these values might differ when you are plotting

URL2 = "rToIfopo_400x400-modified.png"
fdj_cropped2 = Image.open(URL2)
ax_image2 = add_image(
    fdj_cropped2, fig, left=0.92, bottom=0.91, width=0.085, height=0.085
)   # these values might differ when you are plotting

st.pyplot(fig)
