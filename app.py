import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import carregar_dados_upload, processar_dados
from database import init_db, salvar_no_banco, carregar_do_banco, limpar_banco

# 1. Configuração Inicial
st.set_page_config(page_title="Finanças Pro", page_icon="💰", layout="wide")

# Inicializa o banco de dados
init_db()

# 2. Sidebar
with st.sidebar:
    st.header("📂 Importar Dados")
    uploaded_files = st.file_uploader("Adicionar Extratos (CSV):", type=['csv'], accept_multiple_files=True)
    
    # Botão para processar o upload
    if uploaded_files:
        if st.button("Processar e Salvar no Banco"):
            with st.spinner("Processando..."):
                df_temp = carregar_dados_upload(uploaded_files)
                if not df_temp.empty:
                    df_proc = processar_dados(df_temp)
                    salvar_no_banco(df_proc)
                    st.success("Dados adicionados com sucesso!")
                    # Rerun para atualizar os gráficos imediatamente
                    st.rerun()

    st.markdown("---")
    st.header("⚙️ Configurações")
    if st.button("Limpar Banco de Dados"):
        limpar_banco()
        st.warning("Banco de dados apagado!")
        st.rerun()

# 3. Carregamento dos Dados REAIS (Do Banco)
df = carregar_do_banco()

st.title("💰 Dashboard Financeiro (SQL Edition)")

# 4. Verifica se tem dados no banco para mostrar
if not df.empty:
    
    # --- FILTROS INTELIGENTES ---
    # Garantir que a ordenação dos meses esteja correta pode ser chato, 
    # vamos pegar lista de Anos e Meses disponíveis
    anos = sorted(df['ano'].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox("Ano", anos)
    
    meses_disponiveis = df[df['ano'] == ano_selecionado]['mes'].unique()
    mes_selecionado = st.sidebar.selectbox("Mês", meses_disponiveis)
    
    # Filtra o DataFrame principal
    df_filtered = df[(df['ano'] == ano_selecionado) & (df['mes'] == mes_selecionado)]

    # --- DASHBOARD (Igual ao anterior, mas agora alimentado via SQL) ---
    tab1, tab2 = st.tabs(["📊 Dashboard", "📝 Dados Brutos"])

    with tab1:
        # KPIs
        total_receitas = df_filtered[df_filtered['valor'] > 0]['valor'].sum()
        total_despesas = df_filtered[df_filtered['valor'] < 0]['valor'].sum()
        saldo = total_receitas + total_despesas

        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", f"R$ {total_receitas:,.2f}")
        c2.metric("Despesas", f"R$ {total_despesas:,.2f}")
        c3.metric("Saldo", f"R$ {saldo:,.2f}")

        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Por Categoria")
            df_despesas = df_filtered[df_filtered['valor'] < 0].copy()
            df_despesas['valor'] = df_despesas['valor'].abs()
            
            if not df_despesas.empty:
                fig = px.pie(df_despesas, values='valor', names='categoria', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Evolução Mensal")
            # Aqui podemos pegar o ano todo para ver a evolução
            df_ano = df[df['ano'] == ano_selecionado]
            df_evolucao = df_ano.groupby('mes')['valor'].sum().reindex(
                ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            ).reset_index()
            
            fig2 = px.bar(df_evolucao, x='mes', y='valor')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.dataframe(df_filtered)

else:
    st.info("O banco de dados está vazio. Faça o upload de arquivos CSV na barra lateral.")