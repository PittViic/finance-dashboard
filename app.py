import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import carregar_dados_upload, processar_dados
from database import init_db, salvar_no_banco, carregar_do_banco, limpar_banco
from ml_engine import treinar_modelo

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="Finanças Pro",
    layout="wide"
)

# Inicializa o banco de dados (Cria tabela se não existir)
init_db()

# Barra Lateral
with st.sidebar:
    st.header("📂 Importar Extratos")
    uploaded_files = st.file_uploader(
        "Arraste arquivos CSV aqui:", 
        type=['csv'], 
        accept_multiple_files=True
    )
    
    # Botão de Processamento
    if uploaded_files:
        if st.button("Processar e Salvar no Banco"):
            with st.spinner("Lendo arquivos e categorizando..."):
                # 1. Carrega CSVs da memória
                df_temp = carregar_dados_upload(uploaded_files)
                
                if not df_temp.empty:
                    # 2. Processa (Limpeza + IA ou Regras)
                    df_proc = processar_dados(df_temp)
                    
                    # 3. Salva no SQLite
                    salvar_no_banco(df_proc)
                    
                    st.success("✅ Dados importados com sucesso!")
                    # Recarrega a página para atualizar os gráficos
                    st.rerun()

    st.markdown("---")
    
    # Seção de Machine Learning
    st.header("🧠 Inteligência Artificial")
    st.markdown("Ensine a IA a categorizar seus gastos com base no seu histórico.")
    
    if st.button("Treinar Novo Modelo"):
        with st.spinner("A IA está estudando seu banco de dados..."):
            resultado = treinar_modelo()
            if "sucesso" in resultado:
                st.success(f"✅ {resultado}")
            else:
                st.warning(f"⚠️ {resultado}")

    st.markdown("---")
    
    # Seção de Configuração
    st.header("⚙️ Configurações")
    if st.button("Limpar Banco de Dados"):
        limpar_banco()
        st.warning("Banco de dados apagado!")
        st.rerun()
        
    st.markdown("---")
    st.markdown("Desenvolvido por **Pedro Victor**")

# Main
st.title("Dashboard Financeiro")

# Carrega os dados persistentes do SQLite
df = carregar_do_banco()

if not df.empty:
    # Filtros
    col_filtro1, col_filtro2 = st.columns(2)
    
    # Filtro de Ano
    anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
    with col_filtro1:
        ano_selecionado = st.selectbox("Selecione o Ano", anos_disponiveis)
    
    # Filtro de Mês
    meses_disponiveis = df[df['ano'] == ano_selecionado]['mes'].unique()
    # Ordem cronológica dos meses
    ordem_meses = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    meses_ordenados = [m for m in ordem_meses if m in meses_disponiveis]
    # Se a lista ordenada estiver vazia, usa o unique direto
    if not meses_ordenados: 
        meses_ordenados = meses_disponiveis

    with col_filtro2:
        mes_selecionado = st.selectbox("Selecione o Mês", meses_ordenados)
    
    # Aplica os filtros
    df_filtered = df[(df['ano'] == ano_selecionado) & (df['mes'] == mes_selecionado)]

    # Vizualização
    tab1, tab2 = st.tabs(["📊 Visão Gerencial", "📝 Extrato Detalhado"])

    with tab1:
        # 1. KPIs
        total_receitas = df_filtered[df_filtered['valor'] > 0]['valor'].sum()
        total_despesas = df_filtered[df_filtered['valor'] < 0]['valor'].sum()
        saldo = total_receitas + total_despesas

        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", f"R$ {total_receitas:,.2f}", delta="Entradas")
        c2.metric("Despesas", f"R$ {total_despesas:,.2f}", delta="-Saídas", delta_color="inverse")
        c3.metric("Saldo do Mês", f"R$ {saldo:,.2f}", delta_color="normal")

        st.markdown("---")

        # 2. Gráficos
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Despesas por Categoria")
            df_despesas = df_filtered[df_filtered['valor'] < 0].copy()
            df_despesas['valor'] = df_despesas['valor'].abs()
            
            if not df_despesas.empty:
                # Gráfico de Rosca (Donut) usando px.pie com hole
                fig_pizza = px.pie(
                    df_despesas, 
                    values='valor', 
                    names='categoria', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info("Nenhuma despesa registrada neste período.")

        with col_g2:
            st.subheader("Evolução Anual (Receitas vs Despesas)")
            # Agrupa dados do ano todo para ver a tendência
            df_ano = df[df['ano'] == ano_selecionado].copy()
            # Cria coluna de tipo para colorir o gráfico
            df_ano['tipo'] = df_ano['valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            
            df_evolucao = df_ano.groupby(['mes', 'tipo'])['valor'].sum().reset_index()
            
            fig_bar = px.bar(
                df_evolucao, 
                x='mes', 
                y='valor', 
                color='tipo',
                barmode='group', # Barras lado a lado
                color_discrete_map={'Receita': 'green', 'Despesa': 'red'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.markdown("### 📄 Dados das Transações")
        st.dataframe(df_filtered, use_container_width=True)

else:
    # Estado Vazio (Empty State)
    st.info("👋 Bem-vindo ao Finanças Pro!")
    st.markdown("""
        ### Como começar:
        1. Prepare seu extrato bancário em formato **CSV** (`Data`, `Descricao`, `Valor`).
        2. Arraste o arquivo para a barra lateral esquerda.
        3. Clique em **"Processar e Salvar no Banco"**.
        4. (Opcional) Clique em **"Treinar Novo Modelo"** para a IA aprender seus padrões.
    """)