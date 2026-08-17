{\rtf1\ansi\ansicpg1252\cocoartf2513
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from datetime import date\
import streamlit as st\
\
# Configura\'e7\'e3o da P\'e1gina para dispositivos m\'f3veis/iPad\
st.set_page_config(\
    page_title="Doutorado UFRGS - Viol\'e3o", page_icon="
\f1 \uc0\u55356 \u57272 
\f0 ", layout="centered"\
)\
\
# T\'edtulo Principal\
st.title("
\f1 \uc0\u55356 \u57272 
\f0  Doutorado UFRGS")\
st.markdown("### Pr\'e1ticas Interpretativas / Viol\'e3o")\
st.markdown(\
    "Gerenciador de rotina para o recital de **25/11/2026** e a tese."\
)\
\
# Barra Lateral (Contador e Metas)\
st.sidebar.header("
\f1 \uc0\u55356 \u57263 
\f0  Prazos e Metas")\
data_recital = date(2026, 11, 25)\
dias_restantes = (data_recital - date.today()).days\
\
st.sidebar.metric(\
    label="Contagem p/ o Recital",\
    value=f"\{dias_restantes\} dias",\
    delta="25/11/2026",\
)\
st.sidebar.markdown("---")\
st.sidebar.info("
\f1 \uc0\u55356 \u57272 
\f0  Viol\'e3o: ~70% do tempo\\n
\f1 \uc0\u55357 \u56538 
\f0  Pesquisa: ~30% do tempo")\
\
# Abas Principais otimizadas para toque\
aba1, aba2, aba3 = st.tabs(["
\f1 \uc0\u9201 \u65039 
\f0  Horas", "
\f1 \uc0\u55356 \u57276 
\f0  Repert\'f3rio", "
\f1 \uc0\u55357 \u56538 
\f0  Leituras"])\
\
# ---------------------------------------------------------\
# ABA 1: REGISTRO DE HORAS DI\'c1RIAS\
# ---------------------------------------------------------\
with aba1:\
    st.subheader("Registro Di\'e1rio")\
\
    horas_violao = st.number_input(\
        "Horas de Viol\'e3o (T\'e9cnica/Repert\'f3rio):",\
        min_value=0.0,\
        max_value=12.0,\
        step=0.5,\
        value=4.0,\
    )\
    obs_violao = st.text_area(\
        "Notas do estudo de viol\'e3o de hoje:",\
        placeholder="Ex: Passagens dif\'edceis do 2\'ba movimento...",\
    )\
\
    st.markdown("---")\
\
    horas_pesquisa = st.number_input(\
        "Horas de Pesquisa / Tese:",\
        min_value=0.0,\
        max_value=12.0,\
        step=0.5,\
        value=1.5,\
    )\
    obs_pesquisa = st.text_area(\
        "Notas da pesquisa de hoje:",\
        placeholder="Ex: Fichamento do artigo X...",\
    )\
\
    if st.button("Salvar Registro Di\'e1rio", type="primary"):\
        total_horas = horas_violao + horas_pesquisa\
        st.success(\
            f"Salvo! Total estudado hoje: \{total_horas\} horas. Bom descanso, doutorando!"\
        )\
\
# ---------------------------------------------------------\
# ABA 2: REPERT\'d3RIO DO RECITAL (25/11/2026)\
# ---------------------------------------------------------\
with aba2:\
    st.subheader("Obras do Recital")\
    st.markdown("Acompanhe o andamento das obras.")\
\
    obra_1 = st.expander("1. Obra Principal / Sonata")\
    with obra_1:\
        st.text_input("Compositor:", key="comp_1")\
        st.select_slider(\
            "Status:",\
            options=[\
                "N\'e3o Iniciado",\
                "Estudo de Trechos",\
                "Andamento Parcial",\
                "Pronto para Polimento",\
            ],\
            key="status_1",\
        )\
        st.text_input("Metr\'f4nomo (Atual / Meta):", key="met_1")\
\
    obra_2 = st.expander("2. Segunda Obra do Programa")\
    with obra_2:\
        st.text_input("Compositor:", key="comp_2")\
        st.select_slider(\
            "Status:",\
            options=[\
                "N\'e3o Iniciado",\
                "Estudo de Trechos",\
                "Andamento Parcial",\
                "Pronto para Polimento",\
            ],\
            key="status_2",\
        )\
        st.text_input("Metr\'f4nomo (Atual / Meta):", key="met_2")\
\
# ---------------------------------------------------------\
# ABA 3: GEST\'c3O DE LEITURAS E ARTIGOS\
# ---------------------------------------------------------\
with aba3:\
    st.subheader("Fila de Leituras (Tese)")\
\
    novo_artigo = st.text_input("T\'edtulo do Artigo / Livro e Autor")\
    status_artigo = st.selectbox(\
        "Status da Leitura", ["N\'e3o Lido", "Lendo", "Fichado"]\
    )\
\
    if st.button("Adicionar \'e0 Fila de Leituras"):\
        if novo_artigo:\
            st.success(f"'\{novo_artigo\}' adicionado com sucesso!")\
        else:\
            st.warning("Digite o nome do artigo.")\
\
    st.markdown("---")\
    st.markdown("**Exemplo na Fila:**")\
    st.markdown("- *A Performance na Pr\'e1tica Interpretativa* \'97 [Fichado]")\
}