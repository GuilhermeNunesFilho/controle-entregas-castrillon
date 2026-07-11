# controle-entregas-castrillon

# 🛵 Castrillon Entregas

Sistema de gerenciamento e controle de rotas de entregas desenvolvido em Python com a biblioteca **Streamlit**. O aplicativo possui uma interface moderna, dark mode nativo e estilização customizada via CSS com background dinâmico.

---

## 🎯 Funcionalidades

* 📝 **Cadastro de Pedidos**: Formulário intuitivo para registrar novas entregas (Pedido, Cliente e Endereço).
* 📊 **Tabela em Tempo Real**: Visualização limpa dos dados de entregas ativas.
* 🎨 **Interface Customizada**: Design estilizado com fundo opaco em cima da logo da empresa para melhor legibilidade.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Streamlit** (Interface Web)
* **Pandas** (Manipulação de dados)

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório
```bash
git clone https://github.com
cd castrillon-entregas
```

### 2. Criar e Ativar Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências
```bash
pip install streamlit pandas
```

### 4. Preparar os Arquivos
Certifique-se de incluir a imagem da logo com o nome exato de **`logo.png`** na raiz do projeto para que o efeito de background funcione corretamente.

```text
castrillon-entregas/
├── app.py          # Arquivo principal do código
├── logo.png        # Imagem de fundo/logo da empresa
└── README.md
```

### 5. Iniciar o Aplicativo
```bash
streamlit run app.py
```

---

## 🎨 Personalização Visual (CSS)
O projeto injeta CSS customizado no Streamlit para:
* Aplicar uma máscara escura sobre a logo (`linear-gradient`) para não atrapalhar a leitura dos textos.
* Arredondar e aplicar bordas translúcidas nos blocos de conteúdo.
* Padronizar as tabelas (`st.dataframe`) nos tons de azul escuro (`#1e293b` e `#0f172a`).

---
Desenvolvido para otimização de logística e entregas rápidas. 🚀
