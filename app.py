import base64
from datetime import date
import json
import urllib.parse
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st


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


def gerar_botao_timer(minutos, cor="#4CAF50", texto_personalizado=None):
  """Gera botões HTML para disparar o timer via Atalho nativo do iOS."""
  url_timer = (
      f"shortcuts://run-shortcut?name=IniciarTimer&input=text&text={minutos}"
  )
  rotulo = texto_personalizado if texto_personalizado else f"⏱️ {minutos} min"
  return f"""
    <a href="{url_timer}" style="text-decoration: none;">
        <div style="background-color: {cor}; color: white; padding: 12px; text-align: center; border-radius: 8px; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
            {rotulo}
        </div>
    </a>
    """


st.set_page_config(page_title="Doutorado UFRGS", page_icon="🎸", layout="centered")
st.title("🎸 Doutorado UFRGS")

aba1, aba2, aba3, aba4 = st.tabs(
    ["⏱️ Timer/Estudos", "🎼 Repertório", "📊 Análise de Tempo", "📚 Leituras"]
)

client = get_client()

# --- ABA 1: TIMER E REGISTROS ---
with aba1:
  data_recital = date(2026, 11, 25)
  hoje = date.today()
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
        gerar_botao_timer(10, cor="#F57C00", texto_personalizado="☕ 10 min"),
        unsafe_allow_html=True,
    )
  with col4:
    st.markdown(
        gerar_botao_timer(5, cor="#D32F2F", texto_personalizado="⚡ 5 min"),
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.subheader("⏱️ Registrar Tempo Estudado por Peça")

  # Carrega as obras cadastradas no repertório
  sheet_rep = client.open("Doutorado_Estudos").worksheet("Repertorio")
  data_rep = sheet_rep.get_all_values()

  lista_obras = []
  if len(data_rep) > 1:
    lista_obras = [r[0] for r in data_rep[1:] if r[0]]

  if lista_obras:
    with st.form("form_log_tempo", clear_on_submit=True):
      obra_selecionada = st.selectbox("Selecione a Obra / Peça:", lista_obras)
      minutos_estudados = st.number_input(
          "Minutos Praticados:", min_value=5, max_value=300, value=30, step=5
      )
      obs_sessao = st.text_input(
          "Observação técnica (opcional):",
          placeholder="ex: Foco no compasso 24 a 32 / Metrônomo a 80bpm",
      )

      btn_salvar_tempo = st.form_submit_button("💾 Salvar Registro de Tempo")

      if btn_salvar_tempo:
        sheet_log = client.open("Doutorado_Estudos").worksheet("Log_Tempo")
        data_hoje_str = date.today().strftime("%d/%m/%Y")
        sheet_log.append_row([
            data_hoje_str,
            obra_selecionada,
            str(minutos_estudados),
            obs_sessao,
        ])
        st.success(
            f"Registrado! {minutos_estudados} min dedicados a"
            f" '{obra_selecionada}'."
        )
        st.rerun()
  else:
    st.info("Cadastre obras na aba 'Repertório' para começar a registrar o tempo.")

  st.markdown("---")
  st.subheader("📝 Reflexão (Diário iOS)")
  resumo = st.text_area("Resumo da prática:")

  if resumo:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
      texto_violao = f"#Violao\n\n{resumo}"
      texto_v_encoded = urllib.parse.quote(texto_violao)
      url_v = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_v_encoded}"
      st.markdown(
          f'<a href="{url_v}" style="text-decoration:none;"><div'
          ' style="background-color:#008CBA; color:white; padding:12px;'
          " text-align:center; border-radius:8px; font-weight:bold;"
          ' margin-top:8px;">🚀 Enviar ao Diário (Violão)</div></a>',
          unsafe_allow_html=True,
      )

    with col_d2:
      texto_doutorado = f"#Doutorado\n\n{resumo}"
      texto_d_encoded = urllib.parse.quote(texto_doutorado)
      url_d = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_d_encoded}"
      st.markdown(
          f'<a href="{url_d}" style="text-decoration:none;"><div'
          ' style="background-color:#8E44AD; color:white; padding:12px;'
          " text-align:center; border-radius:8px; font-weight:bold;"
          ' margin-top:8px;">🚀 Enviar ao Diário (Doutorado)</div></a>',
          unsafe_allow_html=True,
      )

# --- ABA 2: REPERTÓRIO ---
with aba2:
  st.subheader("🎼 Repertório")
  sheet = client.open("Doutorado_Estudos").worksheet("Repertorio")
  data = sheet.get_all_values()

  opcoes_status = [
      "1. Não Iniciada",
      "2. Leitura / Decodificação",
      "3. Polimento Técnico",
      "4. Maturação Musical",
      "5. Manutenção",
      "6. Pronta / Performada",
  ]

  with st.expander("➕ Adicionar Obra"):
    nova_obra = st.text_input("Nome da Obra")
    novo_status = st.selectbox(
        "Status", opcoes_status, key="status_nova_obra"
    )
    link_goodnotes = st.text_input(
        "Link / URL da Partitura no GoodNotes (Opcional):",
        help="Cole aqui o link do documento do GoodNotes para abrir a partitura direto no iPad.",
    )

    if st.button("Salvar Obra"):
      if nova_obra:
        sheet.append_row([nova_obra, novo_status, link_goodnotes])
        st.success("Obra adicionada!")
        st.rerun()
      else:
        st.warning("Digite o nome da obra.")

  if len(data) > 1:
    rows = []
    for r in data[1:]:
      obra = r[0] if len(r) > 0 else ""
      status = r[1] if len(r) > 1 else ""
      gn_link = r[2] if len(r) > 2 else ""
      rows.append([obra, status, gn_link])

    df = pd.DataFrame(rows, columns=["Obra", "Status", "GoodNotes Link"])

    for idx, row in df.iterrows():
      col_a, col_b, col_c = st.columns([3, 2, 2])
      with col_a:
        st.write(f"**{row['Obra']}**")
      with col_b:
        st.caption(f"Status: {row['Status']}")
      with col_c:
        if row["GoodNotes Link"]:
          st.markdown(
              f"[📖 Abrir Partitura]({row['GoodNotes Link']})",
              unsafe_allow_html=True,
          )
        else:
          st.caption("Sem link")
      st.divider()

    st.markdown("---")
    st.markdown("### ✏️ Editar ou Excluir Obra")

    obra_edit = st.selectbox(
        "Selecione a obra:", df["Obra"].tolist(), key="select_obra_edit"
    )

    item_obra = df[df["Obra"] == obra_edit].iloc[0]
    status_obra_atual = item_obra["Status"]
    gn_link_atual = item_obra["GoodNotes Link"]

    idx_st = (
        opcoes_status.index(status_obra_atual)
        if status_obra_atual in opcoes_status
        else 0
    )

    status_edit = st.selectbox(
        "Novo Status:", opcoes_status, index=idx_st, key="status_edit_val"
    )
    gn_edit = st.text_input(
        "Link GoodNotes:", value=gn_link_atual, key="gn_edit_val"
    )

    col1, col2 = st.columns(2)

    with col1:
      if st.button("Atualizar Obra"):
        index = df[df["Obra"] == obra_edit].index[0] + 2
        sheet.update_cell(index, 2, status_edit)
        sheet.update_cell(index, 3, gn_edit)
        st.success("Obra atualizada!")
        st.rerun()

    with col2:
      st.write("🗑️ **Excluir Registro**")
      confirmar_del_obra = st.checkbox(
          "Confirmar exclusão", key="check_del_obra"
      )
      if st.button("Excluir Obra", type="primary"):
        if confirmar_del_obra:
          index = df[df["Obra"] == obra_edit].index[0] + 2
          sheet.delete_rows(index)
          st.success(f"'{obra_edit}' removida com sucesso!")
          st.rerun()
        else:
          st.warning("Marque a caixa de confirmação antes de excluir.")

# --- ABA 3: DASHBOARD / ANÁLISE DE TEMPO ---
with aba3:
  st.subheader("📊 Distribuição e Porcentagem de Tempo Estudado")

  try:
    sheet_log = client.open("Doutorado_Estudos").worksheet("Log_Tempo")
    data_log = sheet_log.get_all_values()

    if len(data_log) > 1:
      df_log = pd.DataFrame(
          data_log[1:], columns=["Data", "Obra", "Minutos", "Observacao"]
      )
      df_log["Minutos"] = pd.to_numeric(df_log["Minutos"], errors="coerce")
      df_log = df_log.dropna(subset=["Minutos"])

      total_minutos = df_log["Minutos"].sum()
      total_horas = round(total_minutos / 60, 1)

      m_col1, m_col2 = st.columns(2)
      with m_col1:
        st.metric("Total de Tempo Dedicado", f"{total_horas} hrs", f"{int(total_minutos)} minutos")
      with m_col2:
        st.metric("Sessões de Estudo Registradas", f"{len(df_log)}")

      st.markdown("---")

      # Agrupa o tempo por obra
      df_agrupado = (
          df_log.groupby("Obra")["Minutos"]
          .sum()
          .reset_index()
          .sort_values(by="Minutos", ascending=False)
      )

      # Calcula Porcentagem
      df_agrupado["Porcentagem (%)"] = (
          (df_agrupado["Minutos"] / total_minutos) * 100
      ).round(1)
      df_agrupado["Horas"] = (df_agrupado["Minutos"] / 60).round(1)

      st.write("### 📈 Porcentagem de Tempo por Obra")

      # Exibição do gráfico em barra nativo do Streamlit
      st.bar_chart(
          data=df_agrupado.set_index("Obra")["Porcentagem (%)"],
          use_container_width=True,
      )

      st.write("### 📋 Detalhamento por Peça")
      st.dataframe(
          df_agrupado[["Obra", "Porcentagem (%)", "Horas", "Minutos"]],
          hide_index=True,
          use_container_width=True,
      )

      st.markdown("---")
      with st.expander("📜 Histórico de Sessões Recentes"):
        st.dataframe(
            df_log[["Data", "Obra", "Minutos", "Observacao"]].iloc[::-1],
            hide_index=True,
            use_container_width=True,
        )
    else:
      st.info("Nenhum registro de tempo salvo ainda. Faça seu primeiro registro na Aba 'Timer/Estudos'.")
  except Exception as e:
    st.warning("Certifique-se de que a aba 'Log_Tempo' foi criada na planilha do Google Drive.")

# --- ABA 4: LEITURAS ---
with aba4:
  st.subheader("📚 Leituras & Fichamento da Tese")
  sheet_l = client.open("Doutorado_Estudos").worksheet("Leituras")

  opcoes_leitura = ["Não Lido", "Lendo", "Lido", "Fichado para Tese"]
  opcoes_app = ["Pré-visualização (PDF / Web / Arquivo)", "GoodNotes"]

  with st.expander("➕ Adicionar Nova Leitura"):
    novo_artigo = st.text_input("Título / Autor do Texto", key="input_novo_artigo")
    status_leitura = st.selectbox(
        "Status", opcoes_leitura, key="status_novo_artigo"
    )
    app_leitura = st.selectbox("Onde você lê este texto?", opcoes_app, key="app_novo_artigo")
    link_leitura = st.text_input(
        "Link / URL do Texto ou GoodNotes (Opcional):",
        key="link_novo_artigo",
        help="Cole aqui o link do GoodNotes ou o link do PDF/Arquivo (iCloud, Drive, Web).",
    )
    anotacoes_tese = st.text_area(
        "Notas / Citações Relevantes para a Tese:",
        key="input_anotacoes_tese",
        help="Escreva aqui conceitos, citações ou ideias para utilizar na tese.",
    )

    if st.button("Salvar Leitura"):
      if novo_artigo:
        sheet_l.append_row([novo_artigo, status_leitura, anotacoes_tese, app_leitura, link_leitura])
        st.success("Leitura salva com sucesso!")
        st.rerun()
      else:
        st.warning("Preencha o título/autor do texto.")

  data_l = sheet_l.get_all_values()

  if len(data_l) > 1:
    rows = []
    for r in data_l[1:]:
      artigo = r[0] if len(r) > 0 else ""
      status = r[1] if len(r) > 1 else "Não Lido"
      anotacao = r[2] if len(r) > 2 else ""
      app_origem = r[3] if len(r) > 3 else "Pré-visualização (PDF / Web / Arquivo)"
      link_doc = r[4] if len(r) > 4 else ""
      rows.append([artigo, status, anotacao, app_origem, link_doc])

    df_l = pd.DataFrame(
        rows, columns=["Artigo / Livro", "Status", "Anotações Tese", "App Origem", "Link Documento"]
    )

    for idx, row in df_l.iterrows():
      col_l_a, col_l_b, col_l_c = st.columns([3, 2, 2])
      with col_l_a:
        st.write(f"**{row['Artigo / Livro']}**")
        if row["Anotações Tese"]:
          st.caption(f"📝 *Notas:* {row['Anotações Tese'][:80]}..." if len(row["Anotações Tese"]) > 80 else f"📝 *Notas:* {row['Anotações Tese']}")
      with col_l_b:
        st.caption(f"Status: {row['Status']}")
      with col_l_c:
        if row["Link Documento"]:
          icone = "📖" if "GoodNotes" in row["App Origem"] else "📄"
          rotulo_btn = "Abrir no GoodNotes" if "GoodNotes" in row["App Origem"] else "Abrir Texto (Pré-visualização)"
          st.markdown(
              f"[{icone} {rotulo_btn}]({row['Link Documento']})",
              unsafe_allow_html=True,
          )
        else:
          st.caption("Sem link")
      st.divider()

    st.markdown("---")
    st.markdown("### ✏️ Editar ou Excluir Leitura")

    artigo_edit = st.selectbox(
        "Selecione o texto:",
        df_l["Artigo / Livro"].tolist(),
        key="select_artigo_edit",
    )

    item_atual = df_l[df_l["Artigo / Livro"] == artigo_edit].iloc[0]
    status_atual = item_atual["Status"]
    anotacao_atual = item_atual["Anotações Tese"]
    app_atual = item_atual["App Origem"]
    link_atual = item_atual["Link Documento"]

    idx_status = (
        opcoes_leitura.index(status_atual)
        if status_atual in opcoes_leitura
        else 0
    )
    idx_app = (
        opcoes_app.index(app_atual)
        if app_atual in opcoes_app
        else 0
    )

    novo_status_leitura = st.selectbox(
        "Atualizar Status:",
        opcoes_leitura,
        index=idx_status,
        key="edit_status_leitura",
    )

    novo_app_leitura = st.selectbox(
        "Onde lê este texto?:",
        opcoes_app,
        index=idx_app,
        key="edit_app_leitura",
    )

    novo_link_leitura = st.text_input(
        "Link / URL do Texto:",
        value=link_atual,
        key="edit_link_leitura",
    )

    novas_anotacoes = st.text_area(
        "Atualizar Anotações para a Tese:",
        value=anotacao_atual,
        key="edit_anotacoes_tese",
    )

    col_l1, col_l2 = st.columns(2)

    with col_l1:
      if st.button("Atualizar Leitura"):
        row_idx = df_l[df_l["Artigo / Livro"] == artigo_edit].index[0] + 2
        sheet_l.update_cell(row_idx, 2, novo_status_leitura)
        sheet_l.update_cell(row_idx, 3, novas_anotacoes)
        sheet_l.update_cell(row_idx, 4, novo_app_leitura)
        sheet_l.update_cell(row_idx, 5, novo_link_leitura)
        st.success("Informações atualizadas com sucesso!")
        st.rerun()

    with col_l2:
      st.write("🗑️ **Excluir Registro**")
      confirmar_del_leit = st.checkbox(
          "Confirmar exclusão", key="check_del_leit"
      )
      if st.button("Excluir Leitura", type="primary"):
        if confirmar_del_leit:
          row_idx = df_l[df_l["Artigo / Livro"] == artigo_edit].index[0] + 2
          sheet_l.delete_rows(row_idx)
          st.success(f"'{artigo_edit}' removido com sucesso!")
          st.rerun()
        else:
          st.warning("Marque a caixa de confirmação antes de excluir.")
