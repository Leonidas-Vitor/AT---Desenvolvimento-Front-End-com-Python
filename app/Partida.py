import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import time
from statsbombpy import sb
from mplsoccer.pitch import Pitch
from services import at_generic_methods as at_g

at_g.select_match()

st.title("AT - Desenvolvimento Front-End com Python")
st.subheader("Estatísticas básicas da partida", divider=True)

if (st.session_state['competicao_nome'] and st.session_state['temporada_nome'] and st.session_state['partida_nome']):
    match_events = at_g.get_sb_events(match_id=st.session_state['partida_id'])
    st.success("Partida selecionada com sucesso!")
    cols = st.columns([0.3,0.2,0.2,0.2,0.2])
    with cols[0]:
        with st.expander("Informações da partida selecionada", expanded=True):
            st.write("Competição: " + st.session_state['competicao_nome'])
            st.write("Temporada: " + st.session_state['temporada_nome'])
            st.write("Partida: " + st.session_state['partida_nome'])
    with cols[1]:
        df_comp = at_g.get_sb_competitions()
        st.metric("Placar", at_g.get_sb_matches(competition_id=st.session_state['competicao_id'], 
            season_id=st.session_state['temporada_id'])[(at_g.get_sb_matches(competition_id=st.session_state['competicao_id'], 
            season_id=st.session_state['temporada_id'])['match_id'] == st.session_state['partida_id'])][['home_score','away_score']].values[0][0].astype(str) + 
            ' x ' + at_g.get_sb_matches(competition_id=st.session_state['competicao_id'], 
            season_id=st.session_state['temporada_id'])[(at_g.get_sb_matches(competition_id=st.session_state['competicao_id'], 
            season_id=st.session_state['temporada_id'])['match_id'] == st.session_state['partida_id'])][['home_score','away_score']].values[0][1].astype(str))
            
        st.metric("Total de dribles", match_events[match_events['type'] == 'Dribble'].shape[0])
    with cols[2]:
        st.metric("Total de interceptações", match_events[match_events['type'] == 'Interception'].shape[0])
        st.metric("Total de passes", match_events[match_events['type'] == 'Pass'].shape[0])
    with cols[3]:
        st.metric("Total de faltas", match_events[match_events['type'] == 'Foul Committed'].shape[0])
        st.metric("Total de substituições", match_events[match_events['type'] == 'Substitution'].shape[0])
    with cols[4]:
        st.metric("Total de chutes", match_events[match_events['type'] == 'Shot'].shape[0])
        st.metric("Total de paralisações", match_events[match_events['type'] == 'Injury Stoppage'].shape[0])

    events = at_g.get_sb_events_types(st.session_state['partida_id'])
    keys = list(events.keys())
    event_type = st.selectbox('Selecione o tipo de evento para visualizá-los', keys)
    st.dataframe(events[event_type], use_container_width = True)
else :
    st.error("Selecione uma partida")
#st.dataframe(match_events[match_events['type'] == 'Injury Stoppage'])

st.subheader("Visualizações", divider=True)

#@st.cache_data
def plot_passes():
    with st.container():
        passes = at_g.get_sb_events_type(match_id=st.session_state['partida_id'], event_type='passes')

        #st.write(passes)

        team_a = st.session_state['team_a']
        team_b = st.session_state['team_b']

        passes_team_a = passes[passes['possession_team'] == team_a][['possession_team','team','location','pass']]
        passes_team_a['end_location'] = passes_team_a['pass'].apply(lambda x: x['end_location'])
        passes_team_a['sx'] = passes_team_a['location'].apply(lambda x: x[0])
        passes_team_a['sy'] = passes_team_a['location'].apply(lambda x: x[1])
        passes_team_a['ex'] = passes_team_a['end_location'].apply(lambda x: x[0])
        passes_team_a['ey'] = passes_team_a['end_location'].apply(lambda x: x[1])
        passes_team_a.drop(['pass','end_location','location'], axis=1, inplace=True)

        passes_team_b = passes[passes['possession_team'] == team_b][['possession_team','team','location','pass']]
        passes_team_b['end_location'] = passes_team_b['pass'].apply(lambda x: x['end_location'])
        passes_team_b['sx'] = passes_team_b['location'].apply(lambda x: x[0])
        passes_team_b['sy'] = passes_team_b['location'].apply(lambda x: x[1])
        passes_team_b['ex'] = passes_team_b['end_location'].apply(lambda x: x[0])
        passes_team_b['ey'] = passes_team_b['end_location'].apply(lambda x: x[1])
        passes_team_b.drop(['pass','end_location','location'], axis=1, inplace=True)

        cols = st.columns([0.7,0.3])
        with cols[0]:

            colsShow = st.columns([0.5,0.5])
            with colsShow[0]:
                show_team_a = st.toggle(f'Mostrar passes {team_a}', True)
                show_team_a_errados = st.toggle(f'Mostrar passes errados {team_a}', True)
            with colsShow[1]:
                show_team_b = st.toggle(f'Mostrar passes {team_b}', True)
                show_team_b_errados = st.toggle(f'Mostrar passes errados {team_b}', True)

            st.write('')

            pitch = Pitch(pitch_type='statsbomb',pitch_color='#22312b', line_color='#c7d5cc')
            fig, ax = pitch.draw()

            if (show_team_a):
                pitch.arrows(passes_team_a['sx'], passes_team_a['sy'], passes_team_a['ex'], 
                    passes_team_a['ey'], ax=ax, color=st.session_state['team_a_color'], zorder=1, width=1, headwidth=2, headlength=2, label=team_a)
            if (show_team_a_errados):
                passes_errados_tema_a = passes_team_a[passes_team_a['team'] != passes_team_a['possession_team']]
                pitch.arrows(passes_errados_tema_a['sx'], passes_errados_tema_a['sy'], passes_errados_tema_a['ex'], 
                    passes_errados_tema_a['ey'], ax=ax, color=st.session_state['team_b_color'], zorder=1, width=1, headwidth=2, headlength=2, label=team_a + ' errados')

            if (show_team_b):
                pitch.arrows(passes_team_b['sx'], passes_team_b['sy'], passes_team_b['ex'], 
                    passes_team_b['ey'], ax=ax, color=st.session_state['team_b_color'], zorder=1, width=1, headwidth=4, headlength=4, label=team_b)
            if (show_team_b_errados):
                passes_errados_tema_b = passes_team_b[passes_team_b['team'] != passes_team_b['possession_team']]
                pitch.arrows(passes_errados_tema_b['sx'], passes_errados_tema_b['sy'], passes_errados_tema_b['ex'], 
                    passes_errados_tema_b['ey'], ax=ax, color=st.session_state['team_a_color'], zorder=1, width=1, headwidth=4, headlength=4, label=team_b + ' errados')

            ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0), fontsize=5, facecolor='white', edgecolor='none')
            fig.set_facecolor('#808080')
            st.pyplot(fig)

        with cols[1]:
            
            passes_errados_tema_a = passes_team_a[passes_team_a['team'] != passes_team_a['possession_team']]
            passes_errados_tema_b = passes_team_b[passes_team_b['team'] != passes_team_b['possession_team']]

            colsPassesErrados = st.columns([0.5,0.5])
            with colsPassesErrados[0]:
                st.metric(f"Passes errados {team_a}", f'{round(passes_errados_tema_a.shape[0]/passes_team_a.shape[0] * 100,1)}%')
            with colsPassesErrados[1]:
                st.metric(f"Passes errados {team_b}", f'{round(passes_errados_tema_b.shape[0]/passes_team_b.shape[0] * 100,1)}%')


            fig, ax = plt.subplots(figsize=(5,8.6))
            sns.barplot(x=[team_a, team_b], y=[passes_team_a.shape[0], passes_team_b.shape[0]], palette=[st.session_state['team_a_color'], st.session_state['team_b_color']])
            #sns.countplot(x='sx', data=passes_team_a, color=st.session_state['team_a_color'], ax=ax)
            #sns.countplot(x='sx', data=passes_team_b, color=st.session_state['team_b_color'], ax=ax)
            #bar label
            ax.bar_label(ax.containers[0],fontsize=10)
            ax.bar_label(ax.containers[1],fontsize=10)
            ax.set_title('Quantidade de passes', fontsize=15)
            ax.set_facecolor('none')
            #ax.tick_params(axis='x', colors='white')
            fig.set_facecolor('#808080')
            st.pyplot(fig)

def plot_chutes():
    with st.container():
        chutes = at_g.get_sb_events_type(match_id=st.session_state['partida_id'], event_type='shots')

        team_a = st.session_state['team_a']
        team_b = st.session_state['team_b']

        chutes_team_a = chutes[chutes['possession_team'] == team_a][['location','shot']]
        chutes_team_a['end_location'] = chutes_team_a['shot'].apply(lambda x: x['end_location'])
        chutes_team_a['sx'] = chutes_team_a['location'].apply(lambda x: x[0])
        chutes_team_a['sy'] = chutes_team_a['location'].apply(lambda x: x[1])
        chutes_team_a['ex'] = chutes_team_a['end_location'].apply(lambda x: x[0])
        chutes_team_a['ey'] = chutes_team_a['end_location'].apply(lambda x: x[1])
        chutes_team_a['outcome'] = chutes_team_a['shot'].apply(lambda x: x['outcome']['name'])
        chutes_team_a.drop(['shot','end_location','location'], axis=1, inplace=True)

        chutes_team_b = chutes[chutes['possession_team'] == team_b][['location','shot']]
        chutes_team_b['end_location'] = chutes_team_b['shot'].apply(lambda x: x['end_location'])
        chutes_team_b['sx'] = chutes_team_b['location'].apply(lambda x: x[0])
        chutes_team_b['sy'] = chutes_team_b['location'].apply(lambda x: x[1])
        chutes_team_b['ex'] = chutes_team_b['end_location'].apply(lambda x: x[0])
        chutes_team_b['ey'] = chutes_team_b['end_location'].apply(lambda x: x[1])
        chutes_team_b['outcome'] = chutes_team_b['shot'].apply(lambda x: x['outcome']['name'])
        chutes_team_b.drop(['shot','end_location','location'], axis=1, inplace=True)

        cols = st.columns([0.7,0.3])
        with cols[0]:

            colsShow = st.columns([0.5,0.5])
            with colsShow[0]:
                show_team_a = st.toggle(f'Mostrar finalizações {team_a}', True)
                show_team_a_gols = st.toggle(f'Mostrar gols {team_a}', True)
            with colsShow[1]:
                show_team_b = st.toggle(f'Mostrar finalizações {team_b}', True)
                show_team_b_gols = st.toggle(f'Mostrar gols {team_b}', True)
            
            st.write('')

            pitch = Pitch(pitch_type='statsbomb',pitch_color='#22312b', line_color='#c7d5cc')
            fig, ax = pitch.draw()

            chutes = at_g.get_sb_events_type(match_id=st.session_state['partida_id'], event_type='shots')

            #st.write(chutes['shot'].str['outcome'])#['outcome'])

            if (show_team_a):
                pitch.arrows(chutes_team_a['sx'], chutes_team_a['sy'], chutes_team_a['ex'], 
                    chutes_team_a['ey'], ax=ax, color=st.session_state['team_a_color'], zorder=1, width=1, headwidth=2, headlength=2, label=team_a)
            if (show_team_a_gols):
                chutes_gols_tema_a = chutes_team_a[chutes_team_a['outcome'] == 'Goal']
                pitch.arrows(chutes_gols_tema_a['sx'], chutes_gols_tema_a['sy'], chutes_gols_tema_a['ex'], 
                    chutes_gols_tema_a['ey'], ax=ax, color=st.session_state['team_a_color'], zorder=1, width=1, headwidth=2, headlength=2, label=team_a + ' gols')

            if (show_team_b):
                pitch.arrows(chutes_team_b['sx'], chutes_team_b['sy'], chutes_team_b['ex'], 
                    chutes_team_b['ey'], ax=ax, color=st.session_state['team_b_color'], zorder=1, width=1, headwidth=4, headlength=4, label=team_b)
            if (show_team_b_gols):
                chutes_gols_tema_b = chutes_team_b[chutes_team_b['outcome'] == 'Goal']
                pitch.arrows(chutes_gols_tema_b['sx'], chutes_gols_tema_b['sy'], chutes_gols_tema_b['ex'], 
                    chutes_gols_tema_b['ey'], ax=ax, color=st.session_state['team_b_color'], zorder=1, width=1, headwidth=4, headlength=4, label=team_b + ' gols')
            
            ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0), fontsize=5, facecolor='white', edgecolor='none')
            fig.set_facecolor('#808080')
            st.pyplot(fig)

        with cols[1]:
            gols_a = chutes_team_a[chutes_team_a['outcome'] == 'Goal'].shape[0]
            gols_b = chutes_team_b[chutes_team_b['outcome'] == 'Goal'].shape[0]

            colsChutesErrados = st.columns([0.5,0.5])
            with colsChutesErrados[0]:
                st.metric(f"Finalizações com gol {team_a}", f'{round(gols_a/chutes_team_a.shape[0] * 100,1)}%')
            with colsChutesErrados[1]:
                st.metric(f"Finalizações com gol {team_b}", f'{round(gols_b/chutes_team_b.shape[0] * 100,1)}%')

            fig, ax = plt.subplots(figsize=(5,8.6))
            sns.barplot(x=[team_a, team_b], y=[chutes_team_a.shape[0], chutes_team_b.shape[0]], palette=[st.session_state['team_a_color'], st.session_state['team_b_color']])
            #sns.countplot(x='sx', data=passes_team_a, color=st.session_state['team_a_color'], ax=ax)
            #sns.countplot(x='sx', data=passes_team_b, color=st.session_state['team_b_color'], ax=ax)
            #bar label
            ax.bar_label(ax.containers[0],fontsize=10)
            ax.bar_label(ax.containers[1],fontsize=10)
            ax.set_title('Quantidade de finalizações', fontsize=15)
            ax.set_facecolor('none')
            #ax.tick_params(axis='x', colors='white')
            fig.set_facecolor('#808080')
            st.pyplot(fig)

st.markdown("##### Passes")
plot_passes()

st.markdown("##### Finaliozações")
plot_chutes()

#------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("##### Heatmap")

def plot_heatmap(team):
    fig, ax = plt.subplots(figsize=(10,10))
    #Contar eventos por tipo e plotar um heatmap
    events = at_g.get_sb_events_types(st.session_state['partida_id'])
    keys = list(events.keys())
    data = {}
    for key in keys:
        data[key] = events[key][events[key]['team'] == team].shape[0]
    data = pd.DataFrame(data, index=[0])
    sns.heatmap(data.corr(), annot=True, fmt='d', cmap='coolwarm', ax=ax)
    st.pyplot(fig)

#cols = st.columns([0.5,0.5])
#with cols[0]:
#    plot_heatmap(st.session_state['team_a'])
#with cols[1]:
#    plot_heatmap(st.session_state['team_b'])
#Falta relacionar eventos (passes com chutes e etc.)

#Falta mais um plot do mplsoccer
