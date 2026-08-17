from datetime import date
import streamlit as st

# Configuração da Página para dispositivos móveis/iPad
st.set_page_config(
    page_title="Doutorado UFRGS - Violão", page_icon="🎸", layout="centered"
)

# Título Principal
st.title("🎸 Doutorado UFRGS")
st.markdown("### Práticas Interpretativas / Violão")
st.markdown(
    "Gerenciador de rotina para o recital de **25/11/2026** e a tese."
)

# Barra Lateral (Contador e Metas)
st.sidebar.header("🎯 Prazos e Metas")
data_recital = date(2026, 11, 25)
dias_restantes = (data_recital - date.today()).days

st.sidebar.metric(
    label="Contagem p/ o Recital",
    value=f"{dias_restantes} dias",
    delta="25/11/2026",
)
st.sidebar.markdown("---")
st.sidebar.info("🎸 Violão: ~70% do tempo\n📚 Pesquisa: ~30% do tempo")

# Abas Principais otimizadas para toque
aba1, aba2, aba3 = st.tabs(["⏱️ Horas", "🎼 Repertório", "📚 Leituras"])

# ---------------------------------------------------------
# ABA 1: REGISTRO DE HORAS DIÁRIAS
# ---------------------------------------------------------
with aba1:
    st.subheader("Registro Diário")

    horas_violao = st.number_input(
        "Horas de Violão (Técnica/Repertório):",
        min_value=0.0,
        max_value=12.0,
        step=0.5,
        value=4.0,
    )
    obs_violao = st.text_area(
        "Notas do estudo de violão de hoje:",
        placeholder="Ex: Passagens difíceis do 2º movimento...",
    )

    st.markdown("---")

    horas_pesquisa = st.number_input(
        "Horas de Pesquisa / Tese:",
        min_value=0.0,
        max_value=12.0,
        step=0.5,
        value=1.5,
    )
    obs_pesquisa = st.text_area(
        "Notas da pesquisa de hoje:",
        placeholder="Ex: Fichamento do artigo X...",
    )

    if st.button("Salvar Registro Diário", type="primary"):
        total_horas = horas_violao + horas_pesquisa
        st.success(
            f"Salvo! Total estudado hoje: {total_horas} horas. Bom descanso, doutorando!"
        )

# ---------------------------------------------------------
# ABA 2: REPERTÓRIO DO RECITAL (25/11/2026)
# ---------------------------------------------------------
with aba2:
    st.subheader("Obras do Recital")
    st.markdown("Acompanhe o andamento das obras.")

    obra_1 = st.expander("1. Obra Principal / Sonata")
    with obra_1:
        st.text_input("Compositor:", key="comp_1")
        st.select_slider(
            "Status:",
            options=[
                "Não Iniciado",
                "Estudo de Trechos",
                "Andamento Parcial",
                "Pronto para Polimento",
            ],
            key="status_1",
        )
        st.text_input("Metrônomo (Atual / Meta):", key="met_1")

    obra_2 = st.expander("2. Segunda Obra do Programa")
    with obra_2:
        st.text_input("Compositor:", key="comp_2")
        st.select_slider(
            "Status:",
            options=[
                "Não Iniciado",
                "Estudo de Trechos",
                "Andamento Parcial",
                "Pronto para Polimento",
            ],
            key="status_2",
        )
        st.text_input("Metrônomo (Atual / Meta):", key="met_2")

# ---------------------------------------------------------
# ABA 3: GESTÃO DE LEITURAS E ARTIGOS
# ---------------------------------------------------------
with aba3:
    st.subheader("Fila de Leituras (Tese)")

    novo_artigo = st.text_input("Título do Artigo / Livro e Autor")
    status_artigo = st.selectbox(
        "Status da Leitura", ["Não Lido", "Lendo", "Fichado"]
    )

    if st.button("Adicionar à Fila de Leituras"):
        if novo_artigo:
            st.success(f"'{novo_artigo}' adicionado com sucesso!")
        else:
            st.warning("Digite o nome do artigo.")

    st.markdown("---")
    st.markdown("**Exemplo na Fila:**")
    st.markdown("- *A Performance na Prática Interpretativa* — [Fichado]")
