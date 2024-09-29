import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import time
from statsbombpy import sb
from mplsoccer.pitch import Pitch
from mplsoccer import VerticalPitch, add_image, FontManager, Sbopen
from services import at_generic_methods as at_g
from matplotlib.colors import LinearSegmentedColormap

at_g.select_match()

st.title("AT - Desenvolvimento Front-End com Python")
st.subheader("Comparar jogadores", divider=True)

metricas = st.multiselect('Selecione as métricas', ['Passes', 'Chutes', 'Dribles', 'Interceptações', 'Faltas', 'Gols', 'TaxaGol', 'EventoPressao'], 
    default=['Passes', 'Chutes', 'Dribles', 'Interceptações', 'Faltas', 'Gols','TaxaGol', 'EventoPressao'])

df = pd.DataFrame()
dic = {}
dict_b = {}

cols = st.columns(2)

with cols[0]:
    player_a_container = st.container(border = True)
with cols[1]:
    player_b_container = st.container(border = True)

def show_select_player(team):
    st.markdown(f'### {team}')
    jogadores = sb.lineups(match_id=st.session_state['partida_id'])[team][['player_name','player_id','player_nickname','jersey_number']]
    #usar nickname se tiver, senão usar nome
    jogadores['player'] = jogadores['player_nickname'].fillna(jogadores['player_name'])
    #Adicionar o número da camisa no nome
    jogadores['player_jersey'] = jogadores['player'] + ' - ' + jogadores['jersey_number'].astype(str)
    #st.write(jogadores)
    jogador = st.selectbox('Selecione o jogador', jogadores['player_jersey'],key=team)
    jogador_foto = at_g.obter_foto_jogador(jogadores[jogadores['player_jersey'] == jogador]['player'].values[0])
    if jogador_foto:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="{jogador_foto}" style="height: {250}px;">
            </div>
            """, unsafe_allow_html=True
        )
        #st.image(jogador_foto)#, use_column_width=True, output_format='auto')
    else:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="{'https://upload.wikimedia.org/wikipedia/commons/0/0a/No-image-available.png'}" style="height: {250}px;">
            </div>
            """, unsafe_allow_html=True
        )
        #st.image('https://upload.wikimedia.org/wikipedia/commons/0/0a/No-image-available.png')#, use_column_width=True, output_format='auto')
    dic[team] = {'Jogador': jogador}
    player_events = at_g.get_sb_events(match_id=st.session_state['partida_id'])
    player_events = player_events[player_events['player'] == jogadores[jogadores['player_jersey'] == jogador]['player_name'].values[0]]
    return jogador, player_events

with cols[0]:
    with player_a_container:
        jogador_a, player_a_events = show_select_player(st.session_state["team_a"])
with cols[1]:
    with player_b_container:
        jogador_b, player_b_events = show_select_player(st.session_state["team_b"])


def show_player_stats(team, player_events, player_events_compare):
    cols = st.columns(2)
    with cols[0]:
        if 'Passes' in metricas:
            passes = player_events[player_events['type'] == 'Pass'].shape[0]
            dic[team]['Passes'] = passes
            delta = passes - player_events_compare[player_events_compare['type'] == 'Pass'].shape[0]
            st.metric("Total de passes", player_events[player_events['type'] == 'Pass'].shape[0],delta)
        if 'Chutes' in metricas:
            shots = player_events[player_events['type'] == 'Shot'].shape[0]
            dic[team]['Chutes'] = shots
            delta = shots - player_events_compare[player_events_compare['type'] == 'Shot'].shape[0]
            st.metric("Total de chutes", player_events[player_events['type'] == 'Shot'].shape[0],delta)
        if 'Dribles' in metricas:
            dribles = player_events[player_events['type'] == 'Dribble'].shape[0]
            dic[team]['Dribles'] = dribles
            delta = dribles - player_events_compare[player_events_compare['type'] == 'Dribble'].shape[0]
            st.metric("Total de dribles", player_events[player_events['type'] == 'Dribble'].shape[0],delta)
        if 'Interceptações' in metricas:
            interceptacoes = player_events[player_events['type'] == 'Interception'].shape[0]
            dic[team]['Interceptações'] = interceptacoes
            delta = interceptacoes - player_events_compare[player_events_compare['type'] == 'Interception'].shape[0]
            st.metric("Total de interceptações", player_events[player_events['type'] == 'Interception'].shape[0],delta)

    with cols[1]:
        if 'Faltas' in metricas:
            faltas = player_events[player_events['type'] == 'Foul Committed'].shape[0]
            dic[team]['Faltas'] = faltas
            delta = faltas - player_events_compare[player_events_compare['type'] == 'Foul Committed'].shape[0]
            st.metric("Total de faltas", player_events[player_events['type'] == 'Foul Committed'].shape[0],delta,'inverse')

        if 'Gols' in metricas:
            gols = player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'Goal')].shape[0]
            dic[team]['Gols'] = gols
            delta = gols - player_events_compare[(player_events_compare['type'] == 'Shot') & (player_events_compare['shot_outcome'] == 'Goal')].shape[0]
            st.metric("Total de goals", gols,delta)

        if 'TaxaGol' in metricas:
            try:
                shot_goal_rate = gols/shots * 100
            except:
                shot_goal_rate = 0
            try:
                shot_goal_rate_compare = player_events_compare[(player_events_compare['type'] == 'Shot') & (player_events_compare['shot_outcome'] == 'Goal')].shape[0]/player_events_compare[player_events_compare['type'] == 'Shot'].shape[0] * 100
            except:
                shot_goal_rate_compare = 0
            dic[team]['TaxaGol'] = shot_goal_rate
            delta = shot_goal_rate - shot_goal_rate_compare
            st.metric("Taxa de gols", f'{round(shot_goal_rate,1)}%',f'{round(delta,1)}%')
        if 'EventoPressao' in metricas:
            under_pressure = player_events[player_events['under_pressure'] == True].shape[0]
            dic[team]['EventoPressao'] = under_pressure
            delta = under_pressure - player_events_compare[player_events_compare['under_pressure'] == True].shape[0]
            st.metric("Total de evento sob pressão", under_pressure,delta)


def show_kde(player_events, color):
    st.write('### Mapa de calor')
    x = player_events['location'].apply(lambda x: x[0] if isinstance(x, (tuple, list)) else np.nan)
    y = player_events['location'].apply(lambda x: x[1] if isinstance(x, (tuple, list)) else np.nan)

    flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                ['#101010', color], N=100)
    pitch = VerticalPitch(line_color='#404040', line_zorder=2)
    fig, ax = pitch.draw(figsize=(4.4, 6.4))
    kde = pitch.kdeplot(x, y, ax=ax,
                        fill=True, levels=100,
                        thresh=0,
                        cut=4,
                        cmap=flamingo_cmap)
    fig.set_facecolor('none')
    ax.set_facecolor('none')
    st.pyplot(fig)


cols = st.columns(2)

with player_a_container:
    st.divider()
    show_player_stats(st.session_state["team_a"], player_a_events, player_b_events)
    show_kde(player_a_events, st.session_state['team_a_color'])

with player_b_container:
    st.divider()
    show_player_stats(st.session_state["team_b"], player_b_events, player_a_events)
    show_kde(player_b_events, st.session_state['team_b_color'])


#Mapa de passes
#Mapa de chutes
#Mapa de dribles
#Mapa de interceptações


#Download

if st.button('Download dados selecionados', key='download'):
    with st.spinner('Preparando dados...'):
        time.sleep(2)

    my_bar = st.progress(0, text='Progresso')
    for i in range(100):
        time.sleep(0.01)
        my_bar.progress(i + 1, text='Progresso')
    time.sleep(1)
    my_bar.empty()
    st.success('Download pronto para ser realizado!')
    st.download_button('Clique aqui para baixar o dataset filtrado', df.to_csv(), file_name='data.csv', mime='text/csv')
