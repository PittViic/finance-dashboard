import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import carregar_dados_upload, processar_dados

# 1. Configuração da Página (Deve ser a primeira linha)
st.set_page_config(
    page_title="Finanças Pro",
    page_icon="💸",
    layout="wide"
)

# 2. Sidebar (Barra Lateral) de Configuração
with st.sidebar:
    st.header("📂 Carregar Dados")
    uploaded_files = st.file_uploader(
        "Arraste seus extratos (CSV) aqui:", 
        type=['csv'], 
        accept_multiple_files=True
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ Sobre")
    st.markdown("Dashboard desenvolvido para análise financeira pessoal automatizada.")
    st.markdown("Desenvolvido por **Pedro Victor**")

# 3. Título Principal
st.title("Dashboard Financeiro Inteligente")

# 4. Lógica Principal
if uploaded_files:
    # Processamento
    df_raw = carregar_dados_upload(uploaded_files)
    df = processar_dados(df_raw)
    
    # Filtros na Sidebar (só aparecem após upload)
    st.sidebar.header("Filtros")
    todos_meses = df['Mes'].unique()
    mes_selecionado = st.sidebar.selectbox("Selecione o Mês", todos_meses)
    
    # Filtrar dados
    df_filtered = df[df['Mes'] == mes_selecionado]

    # --- INÍCIO DO LAYOUT DE ABAS ---
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📝 Extrato Detalhado"])

    with tab1:
        # Seção de KPIs (Indicadores)
        total_receitas = df_filtered[df_filtered['Valor'] > 0]['Valor'].sum()
        total_despesas = df_filtered[df_filtered['Valor'] < 0]['Valor'].sum()
        saldo = total_receitas + total_despesas

        col1, col2, col3 = st.columns(3)
        col1.metric("Entradas", f"R$ {total_receitas:,.2f}", delta="Receitas")
        col2.metric("Saídas", f"R$ {total_despesas:,.2f}", delta="-Despesas", delta_color="inverse")
        col3.metric("Saldo Mensal", f"R$ {saldo:,.2f}", delta_color="normal")

        st.markdown("---")

        # Gráficos Lado a Lado
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Onde estou gastando?")
            df_despesas = df_filtered[df_filtered['Valor'] < 0].copy()
            df_despesas['Valor'] = df_despesas['Valor'].abs()
            
            if not df_despesas.empty:
                # CORREÇÃO AQUI: Mudamos de px.donut para px.pie
                fig_pizza = px.pie(
                    df_despesas, 
                    values='Valor', 
                    names='Categoria', 
                    hole=0.4, # O 'hole' é o que transforma a pizza em rosca
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info("Sem despesas registradas neste mês.")

        with col_g2:
            st.subheader("Fluxo de Caixa Diário")
            df_evolucao = df_filtered.groupby('Data')['Valor'].sum().reset_index()
            
            fig_bar = px.bar(
                df_evolucao, 
                x='Data', 
                y='Valor', 
                color='Valor',
                color_continuous_scale=['red', 'green']
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.markdown("### Histórico de Transações")
        # Mostra a tabela com opção de download nativa do Streamlit
        st.dataframe(df_filtered, use_container_width=True)

else:
    # Tela de Boas-vindas (Empty State)
    st.info("Bem-vindo! Por favor, faça o upload dos arquivos CSV na barra lateral para começar.")
    st.markdown("""
    ### Formato esperado do CSV:
    O arquivo deve conter as colunas: `Data`, `Descricao`, `Valor`.
    
    Exemplo:
    | Data | Descricao | Valor |
    | :--- | :--- | :--- |
    | 2024-01-10 | Uber | -20.00 |
    | 2024-01-11 | Salario | 3000.00 |
    """)