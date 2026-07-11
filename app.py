import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# Configuração visual da página
st.set_page_config(page_title="Castrillon Entregas", page_icon="🛵", layout="centered")

# --- TRATAMENTO DO FUNDO: IMAGEM DE BACKGROUND PERSONALIZADA ---
def obter_base64_imagem(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as f:
            dados = f.read()
        return base64.b64encode(dados).decode()
    return ""

img_base64 = obter_base64_imagem("logo.png")

# Aplica o fundo escuro ajustado e força os textos e botões a ficarem brancos
if img_base64:
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(14, 21, 37, 0.7), rgba(14, 21, 37, 0.7)), url("data:image/png;base64,{img_base64}");
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        
        /* Força a cor branca em todos os textos comuns */
        h1, h2, h3, p, span, label, stMarkdown {{
            color: #ffffff !important;
        }}
        
        /* Força o texto de dentro dos botões a ficar BRANCO */
        button[data-testid="baseButton-secondary"] p {{
            color: #ffffff !important;
        }}
        button[data-testid="baseButton-secondary"] {{
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }}
        
        div.stForm {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

st.title("🛵 Castrillon Entregas & Controle de Fila")

# 1. DEFINIÇÃO DA SENHA DO EXPEDIDOR
SENHA_EXPEDIDOR = "castrillon2026"

# 2. LISTA DE ENTREGADORES OFICIAIS
ENTREGADORES = [
    "Gui", 
    "João", 
    "Keyper", 
    "Nisley", 
    "Anderson", 
    "Hudson", 
    "Eduardo"
]

# Dicionário de Emojis ajustado
EMOJIS_ENTREGADORES = {
    "Gui": "🧑🏾",    
    "João": "👦🏾", 
    "Keyper": "👦🏼",      
    "Nisley": "👨‍🦲",      
    "Anderson": "🧑🏻",    
    "Hudson": "🧔🏽",      
    "Eduardo": "🧔🏻"       
}

# --- BANCO DE DADOS GLOBAL COMPARTILHADO ---
@st.cache_resource
def iniciar_banco_dados():
    return {
        "relatorio_entregas": [],
        "fila_espera": [] 
    }

banco = iniciar_banco_dados()

# Sincroniza o banco global com a sessão atual do navegador
if "historico_global" not in st.session_state:
    st.session_state["historico_global"] = banco["relatorio_entregas"]

if "fila_global" not in st.session_state:
    st.session_state["fila_global"] = banco["fila_espera"]

if "entregador_clicado" not in st.session_state:
    st.session_state.entregador_clicado = None

# --- SIDEBAR: ÁREA DE ACESSO DO EXPEDIDOR ---
st.sidebar.header("🔑 Área Restrita")
senha_digitada = st.sidebar.text_input("Senha do Expedidor:", type="password", help="Digite a senha para liberar os comandos de lançamento.")

eh_expedidor = (senha_digitada == SENHA_EXPEDIDOR)

if eh_expedidor:
    st.sidebar.success("🔓 Modo Expedidor Ativo!")
else:
    if senha_digitada:
        st.sidebar.error("❌ Senha Incorreta")
    st.sidebar.info("💡 Modo Visualização: Utilize a senha para fazer lançamentos.")

st.markdown("---")

# --- PAINEL VISUAL DA FILA DE ESPERA (PÚBLICO) ---
st.subheader("⏱️ Próximos a Sair (Ordem da Fila)")

if st.session_state["fila_global"]:
    for idx, nome in enumerate(st.session_state["fila_global"]):
        if idx == 0:
            posicao = "🥇 1º da Vez"
        elif idx == 1:
            posicao = "🥈 2º"
        elif idx == 2:
            posicao = "🥉 3º"
        else:
            posicao = f"🛵 {idx + 1}º"
            
        emoji_perfil = EMOJIS_ENTREGADORES.get(nome, "🛵")
        
        with st.container(border=True):
            col_pos, col_emo, col_nom = st.columns(3)
            col_pos.markdown(f"**{posicao}**")
            col_emo.markdown(f"<h3 style='margin:0; padding:0;'>{emoji_perfil}</h3>", unsafe_allow_html=True)
            col_nom.markdown(f"### {nome}")
else:
    st.info("⏱️ Todos os entregadores estão na rua ou a fila está vazia. Aguardando retornos...")

st.markdown("---")

# --- PAINEL DE RANKING EM TEMPO REAL (PÚBLICO) ---
st.subheader("🏆 Ranking de Entregas do Dia")

placar = {nome: 0 for nome in ENTREGADORES}
for registro in st.session_state["historico_global"]:
    if registro["Status"] == "Saída para Entrega":
        entregador_nome = registro["Entregador"]
        if entregador_nome in placar:
            placar[entregador_nome] += 1

# Ordena o ranking por maior número de viagens
ranking_ordenado = sorted(placar.items(), key=lambda x: x, reverse=True)

valores_viagens = [qtd for nome, qtd in ranking_ordenado]
maior_viagem = max(valores_viagens) if valores_viagens and max(valores_viagens) > 0 else 1

col_rank1, col_rank2 = st.columns(2)
with col_rank1:
    for i, (nome, qtd) in enumerate(ranking_ordenado[:3]):
        if i == 0:
            medalha = "🥇"
        elif i == 1:
            medalha = "🥈"
        else:
            medalha = "🥉"
        st.write(f"{medalha} **{nome}**: `{qtd} viag.`")

with col_rank2:
    for nome, qtd in ranking_ordenado:
        progresso = float(qtd / maior_viagem)
        st.progress(progresso, text=f"{nome}: {qtd}")

st.markdown("---")

# --- SEÇÃO DE COMANDOS (LIBERADA APENAS COM SENHA) ---
if eh_expedidor:
    st.subheader("🛠️ Painel de Controle do Expedidor")
    
    st.markdown("""
        <style>
        div.stButton > button p {
            white-space: nowrap !important;
            font-size: 14px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.write("1. Escolha o Entregador:")
    colunas = st.columns(len(ENTREGADORES))

    for i, nome in enumerate(ENTREGADORES):
        esta_na_vez = False
        if st.session_state["fila_global"] and st.session_state["fila_global"] == nome:
            esta_na_vez = True
                
        label_botao = f"🟢 {nome}" if esta_na_vez else nome
        
        if colunas[i].button(label_botao, use_container_width=True, key=f"btn_{nome}"):
            st.session_state.entregador_clicado = nome
            st.rerun()

    nome_selecionado = st.session_state.entregador_clicado

    if nome_selecionado:
        st.info(f"⚡ Entregador selecionado: **{nome_selecionado}**")
        st.write("2. Selecione a ação:")
        
        if nome_selecionado in st.session_state["fila_global"]:
            opcoes_acao = ["Saída para Entrega"]
        else:
            opcoes_acao = ["Entrar na Fila (Chegada Inicial)", "Retorno da Entrega"]
            
        opcao = st.radio("Ação:", opcoes_acao, horizontal=True, label_visibility="collapsed")
        
        num_pedido = ""
        bairro_destino = ""
        if opcao == "Saída para Entrega":
            st.write("3. Informações da Entrega (Opcional):")
            col_ped, col_bai = st.columns(2)
            num_pedido = col_ped.text_input("Nº do Pedido / Nota:", placeholder="Ex: 1542")
            bairro_destino = col_bai.text_input("Bairro / Destino:", placeholder="Ex: Centro")

        if st.button(f"Confirmar Registro para {nome_selecionado}", type="primary", use_container_width=True):
            agora = datetime.now()
            hora_formatada = agora.strftime("%H:%M:%S")
            salvar_historico = True
            
            if opcao == "Entrar na Fila (Chegada Inicial)":
                if nome_selecionado not in st.session_state["fila_global"]:
                    st.session_state["fila_global"].append(nome_selecionado)
                    st.toast(f"📥 {nome_selecionado} iniciou o turno na base.")
                salvar_historico = False
                
            elif opcao == "Saída para Entrega":
                if nome_selecionado in st.session_state["fila_global"]:
                    st.session_state["fila_global"].remove(nome_selecionado)
                st.toast(f"🚀 {nome_selecionado} saiu para a rua. Nome removido da fila da base!")
                    
            elif opcao == "Retorno da Entrega":
                if nome_selecionado in st.session_state["fila_global"]:
                    st.session_state["fila_global"].remove(nome_selecionado)
                st.session_state["fila_global"].append(nome_selecionado)
                st.toast(f"📥 {nome_selecionado} retornou da rua e foi para o final da fila.")

            if salvar_historico:
                novo_item = {
                    "Data": agora.strftime("%d/%m/%Y"),
                    "Horário": hora_formatada,
                    "Entregador": nome_selecionado,
                    "Status": opcao,
                    "Pedido": num_pedido if num_pedido else "-",
                    "Destino": bairro_destino if bairro_destino else "-"
                }
                st.session_state["historico_global"].append(novo_item)
            
            banco["relatorio_entregas"] = st.session_state["historico_global"]
            banco["fila_espera"] = st.session_state["fila_global"]
            
            st.session_state.entregador_clicado = None
            st.rerun()
            
    st.markdown("---")
else:
    st.warning("🔒 Os botões de controle de fila e lançamentos estão ocultos. Digite a senha na barra lateral esquerda para liberar o acesso.")

# --- EXIBIÇÃO DO RELATÓRIO TEMPORÁRIO (PÚBLICO) ---
st.subheader("📋 Histórico do Dia")
if st.session_state["historico_global"]:
    df_relatorio = pd.DataFrame(st.session_state["historico_global"])
    df_visualizacao = df_relatorio[["Data", "Horário", "Entregador", "Status", "Pedido", "Destino"]].iloc[::-1]
