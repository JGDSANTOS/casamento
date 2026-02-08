import streamlit as st
import pandas as pd
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Casamento José & Maria",
    page_icon="💍",
    layout="centered"
)

# --- Arquivos de Dados ---
ARQUIVO_PRESENTES = 'lista_presentes.csv'
ARQUIVO_RSVP = 'rsvp.csv'

# --- Funções Auxiliares ---
def inicializar_dados():
    # Se não existir arquivo de presentes, cria um padrão
    if not os.path.exists(ARQUIVO_PRESENTES):
        dados_iniciais = {
            'Item': ['Geladeira', 'Fogão', 'Microondas', 'Liquidificador', 'Jogo de Jantar', 'Cafeteira', 'Fritadeira Airfryer', 'Jogo de Lençol', 'Faqueiro', 'Lua de Mel (Cota)'],
            'Disponivel': [True] * 10,
            'PresenteadoPor': [''] * 10
        }
        df = pd.DataFrame(dados_iniciais)
        df.to_csv(ARQUIVO_PRESENTES, index=False)
    
    # Se não existir arquivo de RSVP, cria vazio
    if not os.path.exists(ARQUIVO_RSVP):
        df_rsvp = pd.DataFrame(columns=['Nome', 'Qtd_Pessoas', 'Mensagem'])
        df_rsvp.to_csv(ARQUIVO_RSVP, index=False)

def carregar_presentes():
    return pd.read_csv(ARQUIVO_PRESENTES)

def salvar_presentes(df):
    df.to_csv(ARQUIVO_PRESENTES, index=False)

def salvar_rsvp(nome, qtd, msg):
    df = pd.read_csv(ARQUIVO_RSVP)
    novo_rsvp = pd.DataFrame({'Nome': [nome], 'Qtd_Pessoas': [qtd], 'Mensagem': [msg]})
    df = pd.concat([df, novo_rsvp], ignore_index=True)
    df.to_csv(ARQUIVO_RSVP, index=False)

def carregar_rsvp():
    return pd.read_csv(ARQUIVO_RSVP)

# Inicializa os arquivos na primeira execução
inicializar_dados()

# --- Interface Principal ---
st.title("Casamento de José & Maria")
st.markdown("---")

# Menu Lateral para Navegação
menu = st.sidebar.radio(
    "Navegue por aqui:",
    ("🏠 Início", "🎁 Lista de Presentes", "✅ Confirmar Presença", "🔐 Área dos Noivos")
)

# --- Página Inicial ---
if menu == "🏠 Início":
    st.image("Capa.png", caption="Sejam bem-vindos ao nosso site!")
    st.header("Estamos muito felizes em compartilhar esse momento com você!")
    st.write("Utilize o menu ao lado para ver nossa lista de presentes ou confirmar sua presença.")

# --- Página de Presentes ---
elif menu == "🎁 Lista de Presentes":
    st.header("Lista de Presentes")

    # Verifica se um presente acabou de ser dado (para mostrar a foto)
    if 'presente_confirmado' in st.session_state and st.session_state['presente_confirmado']:
        st.image("Obrigado.png", caption="Muito obrigado pelo carinho!")
        st.balloons()
        st.success(f"Registrado com sucesso! Agradecemos muito.")
        del st.session_state['presente_confirmado'] 
        st.markdown("---")

    st.write("Escolha um item para nos presentear.")
    df_presentes = carregar_presentes()
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
                    idx = df_presentes.index[df_presentes['Item'] == presente_escolhido].tolist()[0]
                    df_presentes.at[idx, 'Disponivel'] = False
                    df_presentes.at[idx, 'PresenteadoPor'] = nome_doador
                    salvar_presentes(df_presentes)
                    st.session_state['presente_confirmado'] = True
                    st.rerun() 
                else:
                    st.error("Por favor, digite seu nome.")

    st.markdown("---")
    st.subheader("Já presenteados:")
    presentes_indisponiveis = df_presentes[df_presentes['Disponivel'] == False]
    if not presentes_indisponiveis.empty:
        st.dataframe(presentes_indisponiveis[['Item']], hide_index=True)

# --- Página de RSVP ---
elif menu == "✅ Confirmar Presença":
    st.header("Confirmação de Presença")
    
    with st.form("form_rsvp"):
        nome_rsvp = st.text_input("Nome do Convidado Principal:")
        qtd_pessoas = st.number_input("Quantas pessoas (incluindo você)?", min_value=1, max_value=10, step=1)
        mensagem = st.text_area("Deixe uma mensagem (opcional):")
        confirmar = st.form_submit_button("Confirmar Presença")
        
        if confirmar:
            if nome_rsvp:
                salvar_rsvp(nome_rsvp, qtd_pessoas, mensagem)
                st.balloons()
                st.success(f"Confirmado! Esperamos você, {nome_rsvp}.")
            else:
                st.error("Por favor, preencha seu nome.")

# --- NOVA ABA: Área dos Noivos ---
elif menu == "🔐 Área dos Noivos":
    st.header("Área Restrita")
    
    senha = st.text_input("Digite a senha de acesso:", type="password")
    
    if senha == "1234":
        st.success("Acesso Liberado!")
        st.markdown("---")
        
        df_convidados = carregar_rsvp()
        
        if df_convidados.empty:
            st.warning("Ninguém confirmou presença ainda.")
        else:
            # Cálculo dos totais
            total_confirmacoes = len(df_convidados)
            total_pessoas = df_convidados['Qtd_Pessoas'].sum()
            
            # Mostrando métricas em destaque
            col1, col2 = st.columns(2)
            col1.metric("Famílias/Grupos Confirmados", total_confirmacoes)
            col2.metric("Total de Pessoas (Cabeças)", int(total_pessoas))
            
        st.markdown("### Lista Completa")
            # Mostra a tabela interativa
        df_presentes = carregar_presentes()
        presentes_indisponiveis = df_presentes[df_presentes['Disponivel'] == False]
        if not presentes_indisponiveis.empty:
            st.dataframe(presentes_indisponiveis[['Item', 'PresenteadoPor','valor']], hide_index=True)
    elif senha:

        st.error("Senha incorreta.")
