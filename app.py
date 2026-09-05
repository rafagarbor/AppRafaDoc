import base64
from datetime import date, datetime
import json
import time
import urllib.parse
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import plotly.express as px
import streamlit as st

# --- LINK DO SEU QUADRO NO FREEFORM ---
URL_QUADRO_FREEFORM = (
    "https://www.icloud.com/freeform/0a7R0CLXWwjEwloLYfZ5OUApA#Tese_-_Brainstorming"
)

# --- FUSO HORÁRIO DE BRASÍLIA ---
TZ_BRT = ZoneInfo("America/Sao_Paulo")


# --- CACHE E CONEXÃO SEGURA ---
@st.cache_resource
def get_client():
  b64_str = st.secrets["part1"] + st.secrets["part2"]
  json_bytes = base64.b64decode(b64_str)
  creds_dict = json.loads(json_bytes.decode("utf-8"))

  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  return gspread.authorize(creds)


@st.cache_resource
def get_spreadsheet():
  """Abre a planilha com cache de recurso."""
  client = get_client()
  return client.open("Doutorado_Estudos")


@st.cache_data(ttl=600, show_spinner=False)
def carregar_dados_planilha(nome_aba):
  """Carrega dados da aba com sistema de re-tentativa para evitar travamento em 429/Timeout."""
  max_tentativas = 3
  for tentativa in range(max_tentativas):
    try:
      sh = get_spreadsheet()
      sheet = sh.worksheet(nome_aba)
      return sheet.get_all_values()
    except Exception:
      if tentativa < max_tentativas - 1:
        time.sleep(1.5 * (tentativa + 1))  # Pausa antes de tentar de novo
      else:
        st.error(
            f"⚠️ O Google Sheets demorou a responder ao ler '{nome_aba}'."
            " Aguarde alguns segundos e atualize a página (F5)."
        )
        return []


def limpar_cache():
  carregar_dados_planilha.clear()


def gerar_botao_timer(minutos, cor="#2E7D32", texto_personalizado=None):
  """Gera botões HTML com forçamento rigoroso de fonte branca e negrito para o iOS."""
  url_timer = (
      f"shortcuts://run-shortcut?name=IniciarTimer&input=text&text={minutos}"
  )
  rotulo = texto_personalizado if texto_personalizado else f"⏱️ {minutos} min"
  return f"""
    <a href="{url_timer}" class="custom-btn-link" style="text-decoration: none !important;">
        <div style="background-color: {cor}; padding: 12px; text-align: center; border-radius: 8px; margin-bottom: 8px;">
            <span style="color: #FFFFFF !important; font-size: 16px; font-weight: bold; text-decoration: none !important;">{rotulo}</span>
        </div>
    </a>
    """


def gerar_botao_metronomo():
  """Gera o botão para abrir o atalho do Metronome Beats no iOS."""
  url_metronomo = "shortcuts://run-shortcut?name=AbrirMetronomo"
  return f"""
    <a href="{url_metronomo}" class="custom-btn-link" style="text-decoration: none !important;">
        <div style="background-color: #8E24AA; padding: 12px; text-align: center; border-radius: 8px; margin-top: 4px; margin-bottom: 8px;">
            <span style="color: #FFFFFF !important; font-size: 15px; font-weight: bold; text-decoration: none !important;">🎼 Metrônomo</span>
        </div>
    </a>
    """


def gerar_botao_afinador():
  """Gera o botão para abrir o atalho do Afinador no iOS."""
  url_afinador = "shortcuts://run-shortcut?name=AbrirAfinador"
  return f"""
    <a href="{url_afinador}" class="custom-btn-link" style="text-decoration: none !important;">
        <div style="background-color: #00897B; padding: 12px; text-align: center; border-radius: 8px; margin-top: 4px; margin-bottom: 8px;">
            <span style="color: #FFFFFF !important; font-size: 15px; font-weight: bold; text-decoration: none !important;">🎸 Afinador</span>
        </div>
    </a>
    """


st.set_page_config(
    page_title="Dashboard de Estudos - Doutorado", page_icon="🎸", layout="centered"
)

# --- CSS GLOBAL PARA FORÇAR CORES DOS BOTÕES ---
st.markdown(
    """
    <style>
    /* Força qualquer link dentro de nossos componentes personalizados a ficar branco e sem sublinhado */
    .custom-btn-link, .custom-btn-link *, a.custom-btn-link, a.custom-btn-link span {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }
    .custom-btn-link:hover, .custom-btn-link *:hover {
        color: #FFFFFF !important;
        opacity: 0.9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎸 Doutorado UFRGS - Dashboard de Estudos")

# Reordenação das abas
aba1, aba2, aba5, aba3, aba4 = st.tabs([
    "⏱️ Timer/Estudos",
    "🎼 Repertório",
    "🎸 Obras Extras",
    "📊 Análise de Tempo",
    "📚 Leituras",
])

# Inicializa a planilha globalmente com tratamento amigável de erro 429
try:
  sh_global = get_spreadsheet()
except Exception as e:
  st.error(
      "⚠️ **Limite de requisições do Google atingido (Erro 429).** "
      "O Google restringe temporariamente o acesso quando há muitas leituras seguidas. "
      "Aguarde cerca de **1 minuto** e atualize a página (F5).\n\n"
      f"Detalhes técnicos: {e}"
  )
  st.stop()

tipos_estudo_opcoes = [
    "📖 Leitura / Decodificação",
    "⚙️ Técnica / Mecânica",
    "🎵 Musicalidade / Interpretação",
    "🔄 Manutenção / Memorização",
    "🎙️ Simulação de Performance",
]

opcoes_status_obra = [
    "1. Não Iniciada",
    "2. Leitura / Decodificação",
    "3. Polimento Técnico",
    "4. Maturação Musical",
    "5. Manutenção",
    "6. Pronta / Performada",
]

opcoes_leitura = ["Não Lido", "Lendo", "Lido", "Fichado para Tese"]
opcoes_app = ["Pré-visualização (PDF / Web / Arquivo)", "GoodNotes"]

# --- ABA 1: TIMER E REGISTROS ---
with aba1:
  data_recital = date(2026, 11, 25)
  hoje = datetime.now(TZ_BRT).date()
  dias_restantes = (data_recital - hoje).days

  if dias_restantes > 0:
    st.info(
        f"📅 **Faltam {dias_restantes} dias para o Recital!** ("
        f"{data_recital.strftime('%d/%m/%Y')})"
    )
  elif dias_restantes == 0:
    st.warning("🔥 **É HOJE! Dia do Recital!** 🔥")
  else:
    st.success(f"🎉 O recital foi realizado há {abs(dias_restantes)} dias!")

  st.markdown("---")

  st.subheader("⏱️ Temporizador Rápido (Nativo iOS)")
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    st.markdown(
        gerar_botao_timer(45, cor="#2E7D32", texto_personalizado="🧠 45 min"),
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        gerar_botao_timer(30, cor="#388E3C", texto_personalizado="🎯 30 min"),
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        gerar_botao_timer(10, cor="#D35400", texto_personalizado="☕ 10 min"),
        unsafe_allow_html=True,
    )
  with col4:
    st.markdown(
        gerar_botao_timer(5, cor="#C0392B", texto_personalizado="⚡ 5 min"),
        unsafe_allow_html=True,
    )

  with st.expander("⚙️ Tempo Personalizado"):
    mins_custom = st.number_input(
        "Minutos de estudo:", min_value=1, max_value=180, value=25
    )
    st.markdown(
        gerar_botao_timer(
            mins_custom,
            cor="#1976D2",
            texto_personalizado=f"⏰ Iniciar Timer Customizado ({mins_custom} min)",
        ),
        unsafe_allow_html=True,
    )

  # Ferramentas musicais (Metrônomo e Afinador)
  col_tool1, col_tool2 = st.columns(2)
  with col_tool1:
    st.markdown(gerar_botao_metronomo(), unsafe_allow_html=True)
  with col_tool2:
    st.markdown(gerar_botao_afinador(), unsafe_allow_html=True)

  st.markdown("---")
  st.subheader("⏱️ Registrar Tempo Estudado por Peça")

  try:
    data_rep = carregar_dados_planilha("Repertorio")
    lista_obras = []
    if len(data_rep) > 1:
      lista_obras = [r[0] for r in data_rep[1:] if r[0]]

    try:
      data_extras = carregar_dados_planilha("Obras_Extras")
      if len(data_extras) > 1:
        lista_obras.extend([r[0] for r in data_extras[1:] if r[0]])
    except Exception:
      pass

    if lista_obras:
      with st.form("form_log_tempo", clear_on_submit=True):
        c_form1, c_form2 = st.columns(2)
        with c_form1:
          obra_selecionada = st.selectbox("Selecione a Obra / Peça:", lista_obras)
          minutos_estudados = st.number_input(
              "Minutos Praticados:", min_value=5, max_value=300, value=30, step=5
          )
        with c_form2:
          tipo_selecionado = st.selectbox(
              "Foco / Tipo de Estudo:", tipos_estudo_opcoes
          )
          obs_sessao = st.text_input(
              "Observação técnica (opcional):",
              placeholder="ex: C. 24-32 / Metrônomo a 80bpm",
          )

        btn_salvar_tempo = st.form_submit_button("💾 Salvar Registro de Tempo")

        if btn_salvar_tempo:
          sheet_log = sh_global.worksheet("Log_Tempo")
          data_hoje_str = datetime.now(TZ_BRT).strftime("%d/%m/%Y")
          sheet_log.append_row([
              data_hoje_str,
              obra_selecionada,
              str(minutos_estudados),
              obs_sessao,
              tipo_selecionado,
          ])
          limpar_cache()
          st.success(
              f"Registrado! {minutos_estudados} min de {tipo_selecionado} em"
              f" '{obra_selecionada}'."
          )
          st.rerun()
    else:
      st.info(
          "Cadastre obras na aba 'Repertório' ou 'Obras Extras' para começar a"
          " registrar o tempo."
      )
  except Exception as e:
    st.error(f"Erro ao carregar repertório: {e}")

  st.markdown("---")
  st.subheader("📝 Reflexão (Diário iOS)")
  resumo = st.text_area(
      "Resumo da prática:",
      placeholder="Escreva suas notas aqui para habilitar os botões de envio...",
  )

  col_d1, col_d2 = st.columns(2)
  texto_para_enviar = (
      resumo if resumo else "Sessão de estudo sem resumo especificado."
  )

  with col_d1:
    texto_violao = f"#Violao\n\n{texto_para_enviar}"
    texto_v_encoded = urllib.parse.quote(texto_violao)
    url_v = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_v_encoded}"
    st.markdown(
        f'<a href="{url_v}" class="custom-btn-link" style="text-decoration: none'
        ' !important;"><div style="background-color:#008CBA; padding:12px;'
        ' text-align:center; border-radius:8px; margin-top:8px;"><span'
        ' style="color: #FFFFFF !important; font-weight: bold; font-size: 15px;'
        ' text-decoration: none !important;">🚀 Enviar ao Diário'
        " (Violão)</span></div></a>",
        unsafe_allow_html=True,
    )

  with col_d2:
    texto_doutorado = f"#Doutorado\n\n{texto_para_enviar}"
    texto_d_encoded = urllib.parse.quote(texto_doutorado)
    url_d = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_d_encoded}"
    st.markdown(
        f'<a href="{url_d}" class="custom-btn-link" style="text-decoration: none'
        ' !important;"><div style="background-color:#6C3483; padding:12px;'
        ' text-align:center; border-radius:8px; margin-top:8px;"><span'
        ' style="color: #FFFFFF !important; font-weight: bold; font-size: 15px;'
        ' text-decoration: none !important;">🚀 Enviar ao Diário'
        " (Doutorado)</span></div></a>",
        unsafe_allow_html=True,
    )

# --- ABA 2: REPERTÓRIO E MATERIAIS ---
with aba2:
  st.subheader("🎼 Repertório Principal")
  try:
    sheet_rep_obj = sh_global.worksheet("Repertorio")
    data = carregar_dados_planilha("Repertorio")

    with st.expander("➕ Adicionar Nova Obra"):
      nova_obra = st.text_input("Nome da Obra", key="input_nova_obra_rep")
      novo_status = st.selectbox(
          "Status", opcoes_status_obra, key="status_nova_obra"
      )
      link_goodnotes = st.text_input(
          "Link / URL da Partitura no GoodNotes (Opcional):",
          key="link_gn_novo_rep",
          help=(
              "Cole aqui o link do documento para abrir a partitura direto no"
              " iPad."
          ),
      )

      if st.button("Salvar Obra"):
        if nova_obra:
          sheet_rep_obj.append_row([nova_obra, novo_status, link_goodnotes])
          limpar_cache()
          st.success("Obra adicionada com sucesso!")
          st.rerun()
        else:
          st.warning("Digite o nome da obra.")

    if len(data) > 1:
      rows = [
          {
              "Obra": r[0] if len(r) > 0 else "",
              "Status": r[1] if len(r) > 1 else "",
              "GoodNotes Link": r[2] if len(r) > 2 else "",
          }
          for r in data[1:]
      ]
      df_rep = pd.DataFrame(rows)

      st.markdown("### 📋 Obras do Recital")

      for idx, row in df_rep.iterrows():
        c_rep1, c_rep2, c_rep3 = st.columns([3, 2, 2])
        with c_rep1:
          st.write(f"**{row['Obra']}**")
        with c_rep2:
          st.caption(f"Status: {row['Status']}")
        with c_rep3:
          link_val = row["GoodNotes Link"]
          if link_val and link_val.strip() != "":
            st.markdown(
                f'<a href="{link_val}" target="_blank" class="custom-btn-link"'
                ' style="text-decoration: none !important;"><div'
                ' style="background-color: #1E8449; padding: 8px 12px;'
                ' text-align: center; border-radius: 6px; box-shadow: 0px 1px'
                ' 3px rgba(0,0,0,0.2);"><span style="color: #FFFFFF !important;'
                ' font-size: 13px; font-weight: bold; text-decoration: none'
                ' !important;">🎵 Abrir Partitura</span></div></a>',
                unsafe_allow_html=True,
            )
          else:
            st.caption("Sem link")
        st.divider()

      st.markdown("---")
      st.markdown("### ✏️ Editar / Excluir Obra")
      obra_selecionada_edit = st.selectbox(
          "Selecione a obra para editar ou remover:",
          [""] + df_rep["Obra"].tolist(),
          key="select_obra_edit",
      )

      if obra_selecionada_edit:
        item_rep = df_rep[df_rep["Obra"] == obra_selecionada_edit].iloc[0]
        row_idx_rep = df_rep[df_rep["Obra"] == obra_selecionada_edit].index[0] + 2

        status_atual_rep = item_rep["Status"]
        link_atual_rep = item_rep["GoodNotes Link"]

        idx_status_rep = (
            opcoes_status_obra.index(status_atual_rep)
            if status_atual_rep in opcoes_status_obra
            else 0
        )

        novo_status_rep = st.selectbox(
            "Atualizar Status:",
            opcoes_status_obra,
            index=idx_status_rep,
            key="edit_status_obra_val",
        )

        novo_link_rep = st.text_input(
            "Link / URL da Partitura (GoodNotes):",
            value=link_atual_rep,
            key="edit_link_obra_val",
        )

        col_edit_rep1, col_edit_rep2 = st.columns(2)

        with col_edit_rep1:
          if st.button("Atualizar Obra", key="btn_update_obra"):
            sheet_rep_obj.update_cell(row_idx_rep, 2, novo_status_rep)
            sheet_rep_obj.update_cell(row_idx_rep, 3, novo_link_rep)
            limpar_cache()
            st.success(f"Obra '{obra_selecionada_edit}' atualizada com sucesso!")
            st.rerun()

        with col_edit_rep2:
          confirmar_del_rep = st.checkbox(
              "Confirmar exclusão da obra", key="check_del_rep"
          )
          if st.button(
              "🗑️ Excluir Obra Selecionada", type="primary", key="btn_del_obra"
          ):
            if confirmar_del_rep:
              sheet_rep_obj.delete_rows(row_idx_rep)
              limpar_cache()
              st.success(f"Obra '{obra_selecionada_edit}' removida com sucesso!")
              st.rerun()
            else:
              st.warning("Marque a caixa de confirmação antes de excluir.")
    else:
      st.info("Nenhuma obra cadastrada ainda.")
  except Exception as e:
    st.error(f"Erro ao carregar a aba Repertório: {e}")

  st.markdown("---")
  st.markdown("---")

  # SEÇÃO MATERIAIS DE APOIO
  st.subheader("📚 Materiais de Apoio & Métodos (GoodNotes)")
  try:
    sheet_mat_obj = sh_global.worksheet("Materiais_Apoio")
    data_mat = carregar_dados_planilha("Materiais_Apoio")

    with st.expander("➕ Adicionar Novo Material de Apoio"):
      nome_mat = st.text_input(
          "Nome do Material / Livro", key="input_nome_material"
      )
      tipo_mat = st.selectbox(
          "Tipo de Material",
          [
              "📖 Livro",
              "📄 Apostila / Método",
              "🎼 Partituras / Exercícios",
              "📝 Caderno de Anotações",
              "📁 Outros",
          ],
          key="tipo_material",
      )
      link_mat = st.text_input(
          "Link do GoodNotes / Arquivo:",
          key="link_material_gn",
          help="Cole aqui o link do GoodNotes para abrir direto no iPad.",
      )

      if st.button("Salvar Material"):
        if nome_mat and link_mat:
          sheet_mat_obj.append_row([nome_mat, tipo_mat, link_mat])
          limpar_cache()
          st.success("Material salvo com sucesso!")
          st.rerun()
        else:
          st.warning("Preencha o nome e o link do material.")

    if len(data_mat) > 1:
      rows_mat = [
          {
              "Material": r[0] if len(r) > 0 else "",
              "Tipo": r[1] if len(r) > 1 else "",
              "Link": r[2] if len(r) > 2 else "",
          }
          for r in data_mat[1:]
      ]
      df_mat = pd.DataFrame(rows_mat)

      st.markdown("### 📑 Seus Materiais de Apoio Cadastrados")

      for idx, row in df_mat.iterrows():
        c_m1, c_m2, c_m3 = st.columns([3, 2, 2])
        with c_m1:
          st.write(f"**{row['Material']}**")
        with c_m2:
          st.caption(f"Tipo: {row['Tipo']}")
        with c_m3:
          link_val_m = row["Link"]
          if link_val_m and link_val_m.strip() != "":
            st.markdown(
                f'<a href="{link_val_m}" target="_blank" class="custom-btn-link"'
                ' style="text-decoration: none !important;"><div'
                ' style="background-color: #2980B9; padding: 8px 12px;'
                ' text-align: center; border-radius: 6px; box-shadow: 0px 1px'
                ' 3px rgba(0,0,0,0.2);"><span style="color: #FFFFFF !important;'
                ' font-size: 13px; font-weight: bold; text-decoration: none'
                ' !important;">📖 Abrir Material</span></div></a>',
                unsafe_allow_html=True,
            )
          else:
            st.caption("Sem link")
        st.divider()

      st.markdown("---")
      st.markdown("### ✏️ Gerenciar / Excluir Material")
      mat_del = st.selectbox(
          "Selecione o material para remover:",
          [""] + df_mat["Material"].tolist(),
          key="select_mat_del",
      )

      if mat_del:
        if st.button(
            "🗑️ Excluir Material Selecionado",
            type="primary",
            key="btn_del_mat",
        ):
          idx_linha_mat = df_mat[df_mat["Material"] == mat_del].index[0] + 2
          sheet_mat_obj.delete_rows(idx_linha_mat)
          limpar_cache()
          st.success(f"Material '{mat_del}' removido!")
          st.rerun()
    else:
      st.info(
          "Nenhum material de apoio cadastrado ainda. Use o campo acima para"
          " cadastrar apostilas, livros e métodos do GoodNotes."
      )
  except Exception as e:
    st.info(
        "Certifique-se de ter criado uma aba chamada **'Materiais_Apoio'** na"
        f" sua planilha do Google Drive. Detalhes: {e}"
    )

# --- ABA 5: OBRAS EXTRAS ---
with aba5:
  st.subheader("🎸 Obras Extras")
  try:
    sheet_extra_obj = sh_global.worksheet("Obras_Extras")
    data_extra = carregar_dados_planilha("Obras_Extras")

    with st.expander("➕ Adicionar Nova Obra Extra"):
      nova_obra_extra = st.text_input(
          "Nome da Obra Extra", key="input_nova_obra_extra"
      )
      novo_status_extra = st.selectbox(
          "Status", opcoes_status_obra, key="status_nova_obra_extra"
      )
      link_gn_extra = st.text_input(
          "Link / URL da Partitura (Opcional):",
          key="link_gn_novo_extra",
          help=(
              "Cole aqui o link do documento para abrir a partitura direto no"
              " iPad."
          ),
      )

      if st.button("Salvar Obra Extra"):
        if nova_obra_extra:
          sheet_extra_obj.append_row(
              [nova_obra_extra, novo_status_extra, link_gn_extra]
          )
          limpar_cache()
          st.success("Obra extra adicionada com sucesso!")
          st.rerun()
        else:
          st.warning("Digite o nome da obra.")

    if len(data_extra) > 1:
      rows_extra = [
          {
              "Obra": r[0] if len(r) > 0 else "",
              "Status": r[1] if len(r) > 1 else "",
              "GoodNotes Link": r[2] if len(r) > 2 else "",
          }
          for r in data_extra[1:]
      ]
      df_extra = pd.DataFrame(rows_extra)

      st.markdown("### 📋 Suas Obras Extras Cadastradas")

      for idx, row in df_extra.iterrows():
        c_ex1, c_ex2, c_ex3 = st.columns([3, 2, 2])
        with c_ex1:
          st.write(f"**{row['Obra']}**")
        with c_ex2:
          st.caption(f"Status: {row['Status']}")
        with c_ex3:
          link_val_extra = row["GoodNotes Link"]
          if link_val_extra and link_val_extra.strip() != "":
            st.markdown(
                f'<a href="{link_val_extra}" target="_blank"'
                ' class="custom-btn-link" style="text-decoration: none'
                ' !important;"><div style="background-color: #D35400; padding:'
                ' 8px 12px; text-align: center; border-radius: 6px; box-shadow:'
                ' 0px 1px 3px rgba(0,0,0,0.2);"><span style="color: #FFFFFF'
                ' !important; font-size: 13px; font-weight: bold;'
                ' text-decoration: none !important;">🎵 Abrir'
                " Partitura</span></div></a>",
                unsafe_allow_html=True,
            )
          else:
            st.caption("Sem link")
        st.divider()

      st.markdown("---")
      st.markdown("### ✏️ Editar / Excluir Obra Extra")
      obra_extra_edit = st.selectbox(
          "Selecione a obra extra para editar ou remover:",
          [""] + df_extra["Obra"].tolist(),
          key="select_obra_extra_edit",
      )

      if obra_extra_edit:
        item_extra = df_extra[df_extra["Obra"] == obra_extra_edit].iloc[0]
        row_idx_extra = (
            df_extra[df_extra["Obra"] == obra_extra_edit].index[0] + 2
        )

        status_atual_extra = item_extra["Status"]
        link_atual_extra = item_extra["GoodNotes Link"]

        idx_status_extra = (
            opcoes_status_obra.index(status_atual_extra)
            if status_atual_extra in opcoes_status_obra
            else 0
        )

        novo_status_extra = st.selectbox(
            "Atualizar Status:",
            opcoes_status_obra,
            index=idx_status_extra,
            key="edit_status_extra_val",
        )

        novo_link_extra = st.text_input(
            "Link / URL da Partitura (GoodNotes):",
            value=link_atual_extra,
            key="edit_link_extra_val",
        )

        col_edit_ex1, col_edit_ex2 = st.columns(2)

        with col_edit_ex1:
          if st.button("Atualizar Obra Extra", key="btn_update_extra"):
            sheet_extra_obj.update_cell(row_idx_extra, 2, novo_status_extra)
            sheet_extra_obj.update_cell(row_idx_extra, 3, novo_link_extra)
            limpar_cache()
            st.success(
                f"Obra extra '{obra_extra_edit}' atualizada com sucesso!"
            )
            st.rerun()

        with col_edit_ex2:
          confirmar_del_extra = st.checkbox(
              "Confirmar exclusão da obra extra", key="check_del_extra"
          )
          if st.button(
              "🗑️ Excluir Obra Selecionada", type="primary", key="btn_del_extra"
          ):
            if confirmar_del_extra:
              sheet_extra_obj.delete_rows(row_idx_extra)
              limpar_cache()
              st.success(f"Obra extra '{obra_extra_edit}' removida!")
              st.rerun()
            else:
              st.warning("Marque a caixa de confirmação antes de excluir.")
    else:
      st.info("Nenhuma obra extra cadastrada ainda.")
  except Exception as e:
    st.error(
        "Erro ao carregar a aba Obras_Extras. Certifique-se de que você criou"
        f" uma aba chamada 'Obras_Extras' na sua planilha. Erro: {e}"
    )

# --- ABA 3: DASHBOARD / ANÁLISE DE TEMPO ---
with aba3:
  st.subheader("📊 Métricas e Análise de Tempo")

  try:
    data_log = carregar_dados_planilha("Log_Tempo")

    if len(data_log) > 1:
      rows_log = []
      for i, r in enumerate(data_log[1:], start=2):
        d_data = r[0] if len(r) > 0 else ""
        d_obra = r[1] if len(r) > 1 else ""
        d_min = r[2] if len(r) > 2 else "0"
        d_obs = r[3] if len(r) > 3 else ""
        d_tipo = r[4] if len(r) > 4 else "⚙️ Técnica / Mecânica"
        rows_log.append({
            "Row_Index": i,
            "Data": d_data,
            "Obra": d_obra,
            "Minutos": d_min,
            "Observacao": d_obs,
            "Tipo": d_tipo if d_tipo else "⚙️ Técnica / Mecânica",
        })

      df_log = pd.DataFrame(rows_log)
      df_log["Minutos_Num"] = pd.to_numeric(df_log["MinParece que esta é a nossa primeira mensagem na conversa e eu não tenho o contexto do código anterior ou das alterações que você mencionou.

Você poderia colar o código original aqui e me explicar quais mudanças precisam ser feitas (ou qual é a ideia do aplicativo)? Assim que me passar os detalhes, eu gero o código completo e atualizado para você.
