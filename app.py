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
        h1, h2, h3, p, span, label, stMarkdown {{
            color: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 8px !important;
            padding: 5px !important;
        }}
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
            padding: 15px !important;
            border-radius: 8px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

st.title("🛵 Castrillon Entregas & Controle de Fila")

SENHA_EXPEDIDOR = "castrillon2026"

ENTREGADORES = [
    "Gui", 
    "João", 
    "Keyper", 
    "Nisley", 
    "Anderson", 
    "Hudson", 
    "Eduardo"
]

EMOJIS_ENTREGADORES = {
    "Gui": "🧑🏾",    
    "João": "👦🏾", 
    "Keyper": "👦🏼",      
    "Nisley": "👨‍🦲",      
    "Anderson": "🧑🏻",    
    "Hudson": "🧔🏽",      
    "Eduardo": "🧔🏻"       
}

@st.cache_resource
def iniciar_banco_dados():
    return {
        "relatorio_entregas": [],
        "fila_espera": [] 
    }

banco = iniciar_banco_dados()

if "historico_global" not in st.session_state:
    st.session_state["historico_global"] = banco["relatorio_entregas"]

if "fila_global" not in st.session_state:
    st.session_state["fila_global"] = banco["fila_espera"]

if "entregador_clicado" not in st.session_state:
    st.session_state.entregador_clicado = None

st.sidebar.header("🔑 Área Restrita")
senha_digitada = st.sidebar.text_input("Senha do Expedidor:", type="password", help="Digite a senha para liberar os comandos de lançamento.")

eh_expedidor = (senha_digitada == SENHA_EXPEDIDOR)

if eh_expedidor:
    st.sidebar.success("🔓 Modo Expedidor Ativo!")
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configurações do Painel")
    if st.sidebar.button("🗑️ Resetar Tudo (Fila e Histórico)", use_container_width=True):
        st.session_state["historico_global"] = []
        st.session_state["fila_global"] = []
        banco["relatorio_entregas"] = []
        banco["fila_espera"] = []
        st.rerun()
else:
    if senha_digitada:
        st.sidebar.error("❌ Senha Incorreta")
    st.sidebar.info("💡 Modo Visualização: Utilize a senha para fazer lançamentos.")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Histórico do Dia")
if st.session_state["historico_global"]:
    df_relatorio = pd.DataFrame(st.session_state["historico_global"])
    df_visualizacao = df_relatorio[["Data", "Horário", "Entregador", "Status", "Pedido", "Destino"]].iloc[::-1]
    st.sidebar.dataframe(df_visualizacao, use_container_width=True, hide_index=True)
else:
    st.sidebar.info("Nenhum registro histórico até o momento.")

df_download = pd.DataFrame(st.session_state["historico_global"]) if st.session_state["historico_global"] else pd.DataFrame(columns=["Data", "Horário", "Entregador", "Status", "Pedido", "Destino"])
csv = df_download.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name="entregas.csv", mime="text/csv", use_container_width=True)

st.markdown("---")

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

st.subheader("🏆 Ranking de Entregas do Dia")

placar = {nome: 0 for nome in ENTREGADORES}
for registro in st.session_state["historico_global"]:
    if registro["Status"] == "Saída para Entrega":
        entregador_nome = registro["Entregador"]
        if entregador_nome in placar:
            placar[entregador_nome] += 1

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
        # CORREÇÃO DA BOLINHA VERDE: Ela verifica estritamente se o entregador atual é o primeiro da fila ativa
        esta_na_vez = False
        if len(st.session_state["fila_global"]) > 0:
            if st.session_state["fila_global"][0] == nome:
                esta_na_vez = True
                
        label_botao = f"🟢 {nome}" if esta_na_vez else nome
        
        if colunas[i].button(label_botao, use_container_width=True, key=f"btn_{nome}"):
            st.session_state.entregador_clicado = nome
            st.rerun()

    nome_selecionado = st.session_state.entregador_clicado

    if nome_selecionado:
        # IMPLEMENTAÇÃO DO FORMULÁRIO: Garante resposta imediata no primeiro clique
        with st.form(key=f"form_{nome_selecionado}"):
            st.info(f"⚡ Entregador selecionado: **{nome_selecionado}**")
            st.write("2. Selecione a ação:")
            
            if nome_selecionado in st.session_state["fila_global"]:
                opcoes_acao = ["Saída para Entrega"]
            else:
                opcoes_acao = ["Entrar na Fila (Chegada Inicial)", "Retorno da Entrega"]
                
            opcao = st.radio("Ação:", opcoes_acao, horizontal=True, key=f"radio_{nome_selecionado}", label_visibility="collapsed")
            
            st.write("3. Informações da Entrega (Opcional):")
            col_ped, col_bai = st.columns(2)
            num_pedido = col_ped.text_input("Nº do Pedido / Nota:", placeholder="Ex: 1542", key=f"ped_{nome_selecionado}")
            bairro_destino = col_bai.text_input("Bairro / Destino:", placeholder="Ex: Centro", key=f"bai_{nome_selecionado}")
            
            botao_confirmar = st.form_submit_button(f"Confirmar Registro para {nome_selecionado}", type="primary", use_container_width=True)
            
            if botao_confirmar:
                agora = datetime.now()
                hora_formatada = agora.strftime("%H:%M:%S")
                salvar_historico = True
                
                if opcao == "Entrar na Fila (Chegada Inicial)":
                    if nome_selecionado not in st.session_state["fila_global"]:
                        st.session_state["fila_global"].append(nome_selecionado)
                    salvar_historico = False
                    
                elif opcao == "Saída para Entrega":
                    if nome_selecionado in st.session_state["fila_global"]:
                        st.session_state["fila_global"].remove(nome_selecionado)
                        
                elif opcao == "Retorno da Entrega":
                    if nome_selecionado in st.session_state["fila_global"]:
                        st.session_state["fila_global"].remove(nome_selecionado)
                    st.session_state["fila_global"].append(nome_selecionado)

                if salvar_historico:
                    novo_item = {
                        "Data": agora.strftime("%d/%m/%Y"),
                        "Horário": hora_formatada,
