import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração visual da página
st.set_page_config(page_title="Castrillon Entregas", page_icon="🛵", layout="centered")

# --- TOPO DO APP: LOGO CENTRALIZADO ---
# Procura a imagem salva no seu repositório do GitHub
try:
    st.image("logo.png", use_container_width=True)
except:
    st.title("🛵 Castrillon Entregas & Controle de Fila")

# 1. DEFINIÇÃO DA SENHA DO EXPEDIDOR
SENHA_EXPEDIDOR = "castrillon2026"

# 2. LISTA DE ENTREGADORES OFICIAIS
ENTREGADORES = [
    "Guilherme", 
    "João Carlos", 
    "Keyper", 
    "Nisley", 
    "Anderson", 
    "Hudson", 
    "Eduardo"
]

# Banco de dados de avatares com base nas características da equipe
FOTOS_ENTREGADORES = {
    "Guilherme": "https://dicebear.com", 
    "João Carlos": "https://dicebear.com", 
    "Keyper": "https://dicebear.com", 
    "Nisley": "https://dicebear.com", 
    "Anderson": "https://dicebear.com", 
    "Hudson": "https://dicebear.com", 
    "Eduardo": "https://dicebear.com" 
}

# --- BANCO DE DADOS COMPARTILHADO NA NUVEM ---
@st.cache_resource
def iniciar_banco_dados():
    return {
        "relatorio_entregas": [],
        "fila_espera": []
    }

banco = iniciar_banco_dados()

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
st.subheader("⏱️ Próximos a Sair (Fila)")

if banco["fila_espera"]:
    card_styles = """
    <style>
    .fila-container { display: flex; flex-wrap: wrap; gap: 12px; padding: 10px 0; }
    .entregador-card { display: flex; align-items: center; background-color: #f0f2f6; border-radius: 8px; padding: 6px 14px; border: 1px solid #dcdfe6; }
    .badge-posicao { font-weight: bold; font-size: 13px; margin-right: 8px; color: #555; }
    .avatar-img { width: 32px; height: 32px; border-radius: 50%; margin-right: 8px; background-color: #fff; padding: 2px; }
    .nome-texto { font-weight: 600; color: #31333F; font-size: 14px; }
    </style>
    """
    st.markdown(card_styles, unsafe_allow_html=True)
    
    html_fila = '<div class="fila-container">'
    for idx, nome in enumerate(banco["fila_espera"]):
        posicao = "🥇 1º" if idx == 0 else "🥈 2º" if idx == 1 else "🥉 3º" else f"{idx + 1}º"
        foto_url = FOTOS_ENTREGADORES.get(nome, "https://dicebear.com")
        html_fila += f"""
        <div class="entregador-card">
            <span class="badge-posicao">{posicao}:</span>
            <img class="avatar-img" src="{foto_url}">
            <span class="nome-texto">{nome}</span>
        </div>
        """
    html_fila += '</div>'
    st.markdown(html_fila, unsafe_allow_html=True)
else:
    st.warning("⚠️ Nenhum entregador na base/fila no momento.")

st.markdown("---")

# --- PAINEL DE RANKING EM TEMPO REAL (PÚBLICO) ---
st.subheader("🏆 Ranking de Entregas do Dia")

placar = {nome: 0 for nome in ENTREGADORES}
for registro in banco["relatorio_entregas"]:
    if registro["Status"] == "Saída para Entrega":
        placar[registro["Entregador"]] += 1

ranking_ordenado = sorted(placar.items(), key=lambda x: x[1], reverse=True)
maior_numero_entregas = ranking_ordenado[0][1] if ranking_ordenado else 0

col_rank1, col_rank2 = st.columns(2)
with col_rank1:
    for i, (nome, qtd) in enumerate(ranking_ordenado[:3]):
        medalha = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        st.write(f"{medalha} **{nome}**: `{qtd} viag.`")

with col_rank2:
    for nome, qtd in ranking_ordenado:
        progresso = (qtd / maior_numero_entregas) if maior_numero_entregas > 0 else 0.0
        st.progress(progresso, text=f"{nome}: {qtd}")

st.markdown("---")

# --- SEÇÃO DE COMANDOS (LIBERADA APENAS COM SENHA) ---
if eh_expedidor:
    st.subheader("🛠️ Painel de Controle do Expedidor")
    
    st.write("1. Escolha o Entregador:")
    colunas = st.columns(len(ENTREGADORES))

    for i, nome in enumerate(ENTREGADORES):
        label_botao = f"🟢 {nome}" if nome in banco["fila_espera"] else nome
        if colunas[i].button(label_botao, use_container_width=True, key=f"btn_{nome}"):
            st.session_state.entregador_clicado = nome
            st.rerun()

    nome_selecionado = st.session_state.entregador_clicado

    if nome_selecionado:
        st.info(f"⚡ Entregador selecionado: **{nome_selecionado}**")
        st.write("2. Selecione a ação:")
        
        index_padrao = 0 if nome_selecionado in banco["fila_espera"] else 1
        opcao = st.radio("Ação:", ["Saída para Entrega", "Retorno da Entrega"], index=index_padrao, horizontal=True, label_visibility="collapsed")
        
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
            
            if opcao == "Retorno da Entrega":
                if nome_selecionado not in banco["fila_espera"]:
                    banco["fila_espera"].append(nome_selecionado)
                    st.toast(f"📥 {nome_selecionado} entrou na fila!")
                else:
                    st.toast(f"⚠️ {nome_selecionado} já está na fila!")
                    
            elif opcao == "Saída para Entrega":
                if nome_selecionado in banco["fila_espera"]:
                    if banco["fila_espera"][0] != nome_selecionado:
                        st.toast(f"⚠️ Atenção: {nome_selecionado} não era o primeiro da vez!", icon="🚨")
                    banco["fila_espera"].remove(nome_selecionado)
                    st.toast(f"🚀 {nome_selecionado} saiu para entrega!")
                else:
                    st.toast(f"🚀 {nome_selecionado} saiu para entrega (fora da fila).")

            novo_item = {
                "Data": agora.strftime("%d/%m/%Y"),
                "Horário": hora_formatada,
                "Entregador": nome_selecionado,
                "Status": opcao,
                "Pedido": num_pedido if num_pedido else "-",
                "Destino": bairro_destino if bairro_destino else "-"
            }
            banco["relatorio_entregas"].append(novo_item)
            
            st.session_state.entregador_clicado = None
            st.rerun()
            
    st.markdown("---")
else:
    st.warning("🔒 Os botões de controle de fila e lançamentos estão ocultos. Digite a senha na barra lateral esquerda para liberar o acesso.")

# --- EXIBIÇÃO DO RELATÓRIO TEMPORÁRIO (PÚBLICO) ---
st.subheader("📋 Histórico do Dia")
if banco["relatorio_entregas"]:
    df_relatorio = pd.DataFrame(banco["relatorio_entregas"])
    
    def estilizar_status(val):
        if val == "Saída para Entrega": return 'background-color: #28a745; color: white; font-weight: bold;'
        elif val == "Retorno da Entrega": return 'background-color: #dc3545; color: white; font-weight: bold;'
        return ''

    df_relatorio = df_relatorio[["Data", "Horário", "Entregador", "Status", "Pedido", "Destino"]]
    df_estilizado = df_relatorio.iloc[::-1].style.map(estilizar_status, subset=['Status'])
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    
    col_csv, col_limpar = st.columns(2)
    
    csv = df_relatorio.to_csv(index=False).encode('utf-8')
    col_csv.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name="entregas.csv", mime="text/csv", use_container_width=True)
    
    if eh_expedidor:
        if col_limpar.button("🗑️ Resetar Tudo (Fila e Histórico)", use_container_width=True):
            banco["relatorio_entregas"] = []
            banco["fila_espera"] = []
            st.session_state.entregador_clicado = None
            st.rerun()
else:
    st.info("Nenhum registro histórico até o momento.")
