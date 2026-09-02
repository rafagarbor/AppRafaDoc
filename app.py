from datetime import date
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st


def get_client():
  creds_dict = dict(st.secrets["gcp_service_account"])
  if "private_key" in creds_dict:
    creds_dict["private_key"] = creds_dict["private_key"].replace(
        "\\n", "\n"
    )
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
  st.markdown(
      f'<a href="{url_timer}" style="text-decoration:none;">'
      '<div style="background-color:#4CAF50; color:white; padding:15px;'
      " text-align:center; border-radius:10px; font-size:18px;>"
      f"⏰ Iniciar Timer no iPad ({mins} min)</div></a>",
      unsafe_allow_html=True,
  )

  st.markdown("---")
  st.subheader("📝 Reflexão (Diário iOS)")
  resumo = st.text_input("Resumo da prática:")

  if st.button("Registrar no Diário"):
    if resumo:
      texto_fmt = resumo.replace(" ", "_")
      url_diario = f"shortcuts://run-shortcut?name=RegistrarEstudo&input=text&text={texto_fmt}"
      st.markdown(
          f'<a href="{url_diario}" target="_blank">Clique aqui para enviar ao'
          " Diário</a>",
          unsafe_allow_html=True,
      )
    else:
      st.warning("Escreva o resumo primeiro.")

# --- ABA 2: REPERTÓRIO ---
with aba2:
  st.subheader("🎼 Repertório")
  client = get_client()
  sheet = client.open("Doutorado_Estudos").worksheet("Repertorio")
  data = sheet.get_all_values()

  with st.expander("➕ Adicionar Obra"):
    nova_obra = st.text_input("Nome da Obra")
    novo_status = st.selectbox(
        "Status", ["Não Iniciado", "Em Andamento", "Pronto"]
    )
    if st.button("Salvar Obra"):
      sheet.append_row([nova_obra, novo_status])
      st.rerun()

  if len(data) > 1:
    df = pd.DataFrame(data[1:], columns=["Obra", "Status"])
    st.table(df)
    st.markdown("### Editar Status")
    obra_edit = st.selectbox("Selecione:", df["Obra"].tolist())
    status_edit = st.selectbox(
        "Novo:", ["Não Iniciado", "Em Andamento", "Pronto"]
    )
    if st.button("Atualizar"):
      index = df[df["Obra"] == obra_edit].index[0] + 2
      sheet.update_cell(index, 2, status_edit)
      st.rerun()

# --- ABA 3: LEITURAS ---
with aba3:
  st.subheader("📚 Leituras")
  client = get_client()
  sheet_l = client.open("Doutorado_Estudos").worksheet("Leituras")
  novo_artigo = st.text_input("Novo Artigo/Livro")
  if st.button("Adicionar"):
    sheet_l.append_row([novo_artigo, "Não Lido"])
    st.rerun()
  data_l = sheet_l.get_all_values()
  if len(data_l) > 1:
    st.table(pd.DataFrame(data_l[1:], columns=["Artigo", "Status"]))
