import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import time
from statsbombpy import sb
from mplsoccer.pitch import Pitch
from SPARQLWrapper import SPARQLWrapper, JSON


@st.cache_data
def get_sb_competitions():
    '''
    Função para obter as competições disponíveis no StatsBomb
    '''
    df = sb.competitions()
    return df

@st.cache_data
def get_sb_matches(competition_id, season_id):
    '''
    Função para obter as partidas de uma competição e temporada específicas
    '''
    df = sb.matches(competition_id=competition_id, season_id=season_id)
    return df

@st.cache_data
def get_sb_events(match_id):
    '''
    Função para obter os eventos de uma partida específica
    '''
    df = sb.events(match_id=match_id)
    return df

@st.cache_data
def get_sb_events_types(match_id):
    '''
    Função para obter os eventos de uma partida específica de um tipo específico (ex: passes, chutes, etc.)
    '''
    df = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    return df

@st.cache_data
def get_sb_events_type(match_id, event_type):
    '''
    Função para obter os eventos de uma partida específica de um tipo específico (ex: passes, chutes, etc.)
    '''
    df = sb.events(match_id=match_id, split=True, flatten_attrs=False)[event_type]
    return df

def select_match():
    '''
    Função para selecionar a partida no sidebar do Streamlit e armazenar as informações da competição, temporada e partida selecionadas em st.session_state para uso posterior na aplicação
    '''
    df_comp = get_sb_competitions()
    competicoes = df_comp[['competition_name','competition_id']].drop_duplicates()
    competicoes.reset_index(drop=True, inplace=True)
    with st.sidebar:
        st.markdown("## Selecionar partida")
        try:
            competicao_selecionada = st.selectbox('Selecione a competição', competicoes['competition_name'], index=int(competicoes['competition_name'].loc[competicoes['competition_name'] == st.session_state['competicao_nome']].index[0]))
        except:
            competicao_selecionada = st.selectbox('Selecione a competição', competicoes['competition_name'])
        competicao_id = competicoes[competicoes['competition_name'] == competicao_selecionada]['competition_id'].values[0]

        if competicao_selecionada:
            temporadas = df_comp[df_comp['competition_name'] == competicao_selecionada][['season_name', 'season_id']].drop_duplicates().reset_index(drop=True)
            try:
                temporada_selecionada = st.selectbox('Selecione a temporada', temporadas['season_name'], index=int(temporadas[temporadas['season_name'] == st.session_state['temporada_nome']].index[0]))
            except:
                temporada_selecionada = st.selectbox('Selecione a temporada', temporadas['season_name'])
            temporada_id = temporadas[temporadas['season_name'] == temporada_selecionada]['season_id'].values[0]

        if competicao_id and temporada_id:
            partidas = get_sb_matches(competition_id=competicao_id, season_id=temporada_id)
            partidas['partida'] = partidas['home_team'] + ' x ' + partidas['away_team'] + ' - ' + partidas['match_date']

            try:
                partida_selecionada = st.selectbox('Selecione a partida', partidas['partida'], index=int(partidas[partidas['partida'] == st.session_state['partida_nome']].index[0]))
            except:
                partida_selecionada = st.selectbox('Selecione a partida', partidas['partida'])
            partida_id = partidas[partidas['partida'] == partida_selecionada]['match_id'].values[0]

        if partida_id:
            cols = st.columns([0.5,0.5])
            team_a = partidas[partidas['match_id'] == partida_id]['home_team'].values[0]
            team_b = partidas[partidas['match_id'] == partida_id]['away_team'].values[0]
            with cols[0]:
                try:
                    st.session_state['team_a_color'] = st.color_picker(f'Cor do time: {team_a}', st.session_state['team_a_color'])
                except:
                    st.session_state['team_a_color'] = st.color_picker(f'Cor do time: {team_a}', '#111111')
            with cols[1]:
                try:
                    st.session_state['team_b_color'] = st.color_picker(f'Cor do time: {team_b}', st.session_state['team_b_color'])
                except:
                    st.session_state['team_b_color'] = st.color_picker(f'Cor do time: {team_b}', '#000000')

        st.session_state['competicao_nome'] = competicao_selecionada
        st.session_state['competicao_id'] = competicao_id
        st.session_state['temporada_nome'] = temporada_selecionada
        st.session_state['temporada_id'] = temporada_id
        st.session_state['partida_nome'] = partida_selecionada
        st.session_state['partida_id'] = partida_id
        st.session_state['team_a'] = team_a
        st.session_state['team_b'] = team_b

def obter_foto_jogador(nome_jogador):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    SELECT ?thumbnail WHERE {{
        ?player a dbo:SoccerPlayer ;
                foaf:name "{nome_jogador}"@en ;
                dbo:thumbnail ?thumbnail .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if results["results"]["bindings"]:
        foto_url = results["results"]["bindings"][0]["thumbnail"]["value"]
        return foto_url
    else:
        return None
