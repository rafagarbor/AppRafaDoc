import base64
import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st


def get_client():
  # Junta as partes da string Base64 salvas nos Secrets
  b64_str = st.secrets["part1"] + st.secrets["part2"]
  json_bytes = base64.b64decode(b64_str)
  creds_dict = json.loads(json_bytes.decode("utf-8"))

  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  return gspread.authorize(creds)


st.set_page_config(page_title="Doutorado UFRGS", page_icon="🎸", layout="centered")
st.title("🎸 Doutorado UFRGS")

aba1, aba2, aba3 = st.tabs(["⏱️ Timer/Estudos", "🎼 Repertório", "📚 Leituras"])

# --- ABA 1: TIMER E REGISTROS ---
with aba1:
  st.subheader("⏱️ Temporizador (Nativo iOS)")
  mins = st.number_input(
      "Minutos de estudo:", min_value=1, max_value=180, value=45
  )

  url_timer = f"shortcuts://run-shortcut?name=IniciarTimer&input=text&text={mins}"
  html_timer = f"""
    <a href="{url_timer}" style="text-decoration: none;">
        <div style="background-color: #4CAF50; color: white; padding: 15px; text-align: center; border-radius: 10px; font-size: 18px; font-weight: bold;">
            ⏰ Iniciar Timer no iPad ({mins} min)
        </div>
    </a>
    """
  st.markdown(html_timer, unsafe_allow_html=True)

  st.markdown("---")
  st.subheader("📝 Reflexão (Diário iOS)")
  resumo = st.text_input("Resumo da prática:")

  if st.button("Registrar no Diário"):
    if resumo:
      texto_fmt = resumo.replace(" ", "_")
      url_diario = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_fmt}"
      html_diario = f"""
            <a href="{url_diario}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #008CBA; color: white; padding: 12px; text-align: center; border-radius: 8px; font-size: 16px; margin-top: 10px;">
                    📲 Clique aqui para enviar ao Diário
                </div>
            </a>
            """
      st.markdown(html_diario, unsafe_allow_html=True)
    else:
      st.warning("Escreva o resumo primeiro.")

# --- ABA 2: REPERTÓRIO ---
with aba2:
  st.subheader("🎼 Repertório")
  client = get_client()
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
    if st.button("Salvar Obra"):
      if nova_obra:
        sheet.append_row([nova_obra, novo_status])
        st.success("Obra adicionada!")
        st.rerun()
      else:
        st.warning("Digite o nome da obra.")

  if len(data) > 1:
    df = pd.DataFrame(data[1:], columns=["Obra", "Status"])
    st.table(df)

    st.markdown("---")
    st.markdown("### ✏️ Editar ou Excluir Obra")

    obra_edit = st.selectbox(
        "Selecione a obra:", df["Obra"].tolist(), key="select_obra_edit"
    )

    col1, col2 = st.columns(2)

    with col1:
      status_edit = st.selectbox("Novo Status:", opcoes_status, key="status_edit_val")
      if st.button("Atualizar Status"):
        index = df[df["Obra"] == obra_edit].index[0] + 2
        sheet.update_cell(index, 2, status_edit)
        st.success("Status atualizado!")
        st.rerun()

    with col2:
      st.write("🗑️ **Excluir Registro**")
      confirmar_del_obra = st.checkbox("Confirmar exclusão", key="check_del_obra")
      if st.button("Excluir Obra", type="primary"):
        if confirmar_del_obra:
          index = df[df["Obra"] == obra_edit].index[0] + 2
          sheet.delete_rows(index)
          st.success(f"'{obra_edit}' removida com sucesso!")
          st.rerun()
        else:
          st.warning("Marque a caixa de confirmação antes de excluir.")

# --- ABA 3: LEITURAS ---
with aba3:
  st.subheader("📚 Leituras & Fichamento da Tese")
  client = get_client()
  sheet_l = client.open("Doutorado_Estudos").worksheet("Leituras")

  opcoes_leitura = ["Não Lido", "Lendo", "Lido", "Fichado para Tese"]

  with st.expander("➕ Adicionar Nova Leitura"):
    novo_artigo = st.text_input("Título / Autor do Texto", key="input_novo_artigo")
    status_leitura = st.selectbox("Status", opcoes_leitura, key="status_novo_artigo")
    anotacoes_tese = st.text_area(
        "Notas / Citações Relevantes para a Tese:",
        key="input_anotacoes_tese",
        help="Escreva aqui conceitos, citações ou ideias para utilizar na tese.",
    )

    if st.button("Salvar Leitura"):
      if novo_artigo:
        sheet_l.append_row([novo_artigo, status_leitura, anotacoes_tese])
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
      rows.append([artigo, status, anotacao])

    df_l = pd.DataFrame(rows, columns=["Artigo / Livro", "Status", "Anotações Tese"])
    st.table(df_l)

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

    idx_status = opcoes_leitura.index(status_atual) if status_atual in opcoes_leitura else 0

    novo_status_leitura = st.selectbox(
        "Atualizar Status:",
        opcoes_leitura,
        index=idx_status,
        key="edit_status_leitura",
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
        st.success("Informações atualizadas com sucesso!")
        st.rerun()

    with col_l2:
      st.write("🗑️ **Excluir Registro**")
      confirmar_del_leit = st.checkbox("Confirmar exclusão", key="check_del_leit")
      if st.button("Excluir Leitura", type="primary"):
        if confirmar_del_leit:
          row_idx = df_l[df_l["Artigo / Livro"] == artigo_edit].index[0] + 2
          sheet_l.delete_rows(row_idx)
          st.success(f"'{artigo_edit}' removido com sucesso!")
          st.rerun()
        else:
          st.warning("Marque a caixa de confirmação antes de excluir.")
