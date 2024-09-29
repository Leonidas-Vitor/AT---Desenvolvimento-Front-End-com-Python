import streamlit as st


intro_page = st.Page("Intro.py", title="Introdução", icon="📑")
partida = st.Page("Partida.py", title="Dados da partida", icon="1️⃣")
jogadores = st.Page("Jogadores.py", title="Comparar jogadores", icon="2️⃣")
pg = st.navigation([intro_page, partida, jogadores])

st.set_page_config(
        page_title="Intro",
        page_icon="Infnet_logo.png",
        layout="wide",
        initial_sidebar_state = "expanded")

pg.run()
