import streamlit as st

html_p = """<p style='text-align: center; font-size:%spx;'><b>%s</b></p>"""

github_link = '''https://github.com/Leonidas-Vitor/AT---Desenvolvimento-Front-End-com-Python'''
email = '''leonidas.almeida@al.infnet.edu.br'''

#st.divider()
columns = st.columns([0.3,0.7])
with columns[0]:
    st.image('Infnet_logo.png',width=200)

    #st.markdown(html_p % tuple([25,'Desenvolvimento Front-End com Python']),unsafe_allow_html = True)
    #st.markdown(html_p % tuple([25,'TP1']),unsafe_allow_html = True)

with columns[1]:
    st.markdown('''<h1 style='text-align: center; '><b>INSTITUTO INFNET</b></h1>''',unsafe_allow_html = True)
    st.markdown(html_p % tuple([35,"ESCOLA SUPERIOR DE TECNOLOGIA"]),unsafe_allow_html=True)
st.divider()
st.markdown(html_p % tuple([35,"AT - Desenvolvimento Front-End com Python"]),unsafe_allow_html=True)
st.markdown(html_p % tuple([25,'Aluno: Leônidas Almeida']),unsafe_allow_html = True)
st.markdown(html_p % tuple([25,f'E-mail: <a href= mailto:{email}>{email}</a>']),unsafe_allow_html = True)
st.markdown(html_p % tuple([25,f'GitHub: <a href={github_link}>Link para o repositório</a>']),unsafe_allow_html = True)

