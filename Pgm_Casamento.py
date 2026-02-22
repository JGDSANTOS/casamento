import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuração da Página ---
st.set_page_config(
    page_title="Casamento José & Maria",
    page_icon="💍",
    layout="centered"
)

# --- IDs das Planilhas do Google ---
SHEET_ID_PRESENTES = '1dNRkTe-TgC59zd9ftar_8OkNEv9fkjIG-otl8uWCv1s'
SHEET_ID_RSVP = '1L6FAa8oLTUb5G9Pf-C3bpcvVqDVMHHncSBkDJfySL4Q'

# --- Conexão com Google Sheets (Cacheada) ---
@st.cache_resource
def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

# --- Funções de Leitura e Escrita ---

def carregar_dados(sheet_id):
    """Lê qualquer planilha e retorna um DataFrame"""
    client = conectar_google_sheets()
    sheet = client.open_by_key(sheet_id).sheet1
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    return df

def adicionar_rsvp(nome, qtd, msg):
    """Adiciona uma nova linha na planilha de convidados"""
    client = conectar_google_sheets()
    sheet = client.open_by_key(SHEET_ID_RSVP).sheet1
    # Adiciona a linha no final
    sheet.append_row([nome, qtd, msg])

def atualizar_presente(item_nome, nome_doador):
    """Busca o item e marca como indisponível"""
    client = conectar_google_sheets()
    sheet = client.open_by_key(SHEET_ID_PRESENTES).sheet1
    
    # Encontra a célula que tem o nome do item
    cell = sheet.find(item_nome)
    
    if cell:
        # Atualiza a coluna 'Disponivel' (Coluna 2) para FALSE
        sheet.update_cell(cell.row, 2, "FALSE")
        # Atualiza a coluna 'PresenteadoPor' (Coluna 3) com o nome
        sheet.update_cell(cell.row, 3, nome_doador)








import streamlit as st

# 2. Lista de opções (tem que ser idêntica em todo o código)
opcoes = ["🏠 Início", "🎁 Lista de Presentes", "✅ Confirmar Presença", "🔐 Área dos Noivos"]

# 3. Inicialização do Session State
# A 'key' do rádio será a nossa fonte da verdade
if "navegação" not in st.session_state:
    st.session_state["navegação"] = "🏠 Início"

# 4. Função para os botões do meio da tela
def mudar_pagina(nome_pagina):
    st.session_state["navegação"] = nome_pagina

# 5. Barra Lateral (Sidebar)
# O rádio usa a 'key' diretamente, então ele se atualiza sozinho
st.sidebar.radio(
    "Navegue por aqui:",
    opcoes,
    key="navegação"
)

# --- Lógica de Exibição Baseada no State ---

if st.session_state["navegação"] == "🏠 Início":
    st.image("Capa.png", caption="Sejam bem-vindos ao nosso site!")
    st.header("Estamos muito felizes em compartilhar esse momento com você!")
    st.write("Utilize o menu ao lado para ver nossa lista de presentes ou confirmar sua presença.")
    
    st.write("Escolha uma das opções abaixo para continuar:")

    # Criando as colunas para os botões
    col1, col2 = st.columns(2)
    
    with col1:
        # Quando clicado, chama a função 'mudar_pagina'
        st.button("🎁 Ver Lista de Presentes", 
                  on_click=mudar_pagina, 
                  args=("🎁 Lista de Presentes",),
                  use_container_width=True)

    with col2:
        st.button("✅ Confirmar Presença", 
                  on_click=mudar_pagina, 
                  args=("✅ Confirmar Presença",),
                  use_container_width=True)
        






# --- Página de Presentes ---
elif st.session_state["navegação"] == "🎁 Lista de Presentes":
    st.header("Lista de Presentes")

    # Verifica feedback de sucesso
    if 'msg_sucesso' in st.session_state:
        st.balloons()
        st.success(st.session_state['msg_sucesso'])
        # Limpa a mensagem para não aparecer de novo se recarregar
        del st.session_state['msg_sucesso']
        st.markdown("---")

    st.write("Escolha um item para nos presentear.")
    
    # Carrega do Google Sheets
    df_presentes = carregar_dados(SHEET_ID_PRESENTES)
    
    # Tratamento para garantir que "TRUE" (string) vire True (booleano)
    # O Google Sheets as vezes retorna texto em vez de booleano puro
    df_presentes['Disponivel'] = df_presentes['Disponivel'].astype(str).str.upper() == 'TRUE'
    
    presentes_disponiveis = df_presentes[df_presentes['Disponivel'] == True]

    if presentes_disponiveis.empty:
        st.success("Oba! Todos os presentes da lista já foram escolhidos! ❤️")
    else:
        with st.form("form_presente"):
            presente_escolhido = st.selectbox("Selecione o presente:", presentes_disponiveis['Item'].unique())
            nome_doador = st.text_input("Seu nome completo:")
            enviar = st.form_submit_button("Confirmar Presente")

            if enviar:
                if nome_doador:
                    # Chama a função que atualiza o Google Sheets
                    atualizar_presente(presente_escolhido, nome_doador)
                    
                    st.session_state['msg_sucesso'] = "Registrado com sucesso! Agradecemos muito."
                    st.rerun()
                else:
                    st.error("Por favor, digite seu nome.")

    st.markdown("---")
    st.subheader("Já presenteados:")
    # Filtra os indisponíveis
    presentes_indisponiveis = df_presentes[df_presentes['Disponivel'] == False]
    
    if not presentes_indisponiveis.empty:
        st.dataframe(presentes_indisponiveis[['Item', 'PresenteadoPor']], hide_index=True)
        
    st.button("⬅ Voltar ao Início", on_click=mudar_pagina, args=("🏠 Início",))





# --- Página de RSVP ---
elif st.session_state["navegação"] == "✅ Confirmar Presença":
    st.header("Confirmação de Presença")
    
    with st.form("form_rsvp"):
        nome_rsvp = st.text_input("Nome do Convidado Principal:")
        qtd_pessoas = st.number_input("Quantas pessoas (incluindo você)?", min_value=1, max_value=10, step=1)
        mensagem = st.text_area("Deixe uma mensagem (opcional):")
        confirmar = st.form_submit_button("Confirmar Presença")
        
        if confirmar:
            if nome_rsvp:
                # Salva no Google Sheets
                adicionar_rsvp(nome_rsvp, qtd_pessoas, mensagem)
                
                st.balloons()
                st.success(f"Confirmado! Esperamos você, {nome_rsvp}.")
            else:
                st.error("Por favor, preencha seu nome.")

    st.button("⬅ Voltar ao Início", on_click=mudar_pagina, args=("🏠 Início",))



# --- NOVA ABA: Área dos Noivos ---
elif st.session_state["navegação"] == "🔐 Área dos Noivos":
    st.header("Área Restrita")
    
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "1234":
        st.success("Acesso Liberado!")
        st.markdown("---")
        
        # Carrega RSVP do Google Sheets
        df_convidados = carregar_dados(SHEET_ID_RSVP)
        
        if df_convidados.empty:
            st.warning("Ninguém confirmou presença ainda.")
        else:
            total_confirmacoes = len(df_convidados)
            total_pessoas = df_convidados['Qtd_Pessoas'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Famílias/Grupos", total_confirmacoes)
            col2.metric("Total de Pessoas", int(total_pessoas))
            
            st.markdown("### Lista de Convidados")
            st.dataframe(df_convidados, hide_index=True)
            
        st.markdown("---")
        st.markdown("### Controle Financeiro dos Presentes")
        
        # Carrega Presentes do Google Sheets
        df_presentes = carregar_dados(SHEET_ID_PRESENTES)
        
        # Tratamento de booleano novamente
        df_presentes['Disponivel'] = df_presentes['Disponivel'].astype(str).str.upper() == 'TRUE'
        
        ganhos = df_presentes[df_presentes['Disponivel'] == False]
        
        if not ganhos.empty:
            # Tenta converter valor para número caso esteja como texto no Sheets
            try:
                # Remove R$ e converte vírgula para ponto se necessário
                ganhos['Valor'] = ganhos['Valor'].astype(str).str.replace('R$', '').str.replace(',', '.').astype(float)
                total_valor = ganhos['Valor'].sum()
                st.metric("Total em Presentes (R$)", f"R$ {total_valor:.2f}")
            except:
                st.warning("Não consegui somar os valores. Verifique se a coluna 'Valor' na planilha contém apenas números.")

            st.dataframe(ganhos[['Item', 'PresenteadoPor', 'Valor']], hide_index=True)
        else:
            st.info("Nenhum presente recebido ainda.")

    elif senha:
        st.error("Senha incorreta.")
