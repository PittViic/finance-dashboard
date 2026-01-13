import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import carregar_dados, processar_dados

# Configuração da Página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

st.title("Minhas Finanças Pessoais")

# 1. Carregamento e Processamento
df_raw = carregar_dados()

if not df_raw.empty:
    df = processar_dados(df_raw)

    # Sidebar para Filtros
    st.sidebar.header("Filtros")
    mes_selecionado = st.sidebar.selectbox("Selecione o Mês", df['Mes'].unique())
    
    df_filtered = df[df['Mes'] == mes_selecionado]

    # 2. KPIs (Indicadores Principais)
    total_receitas = df_filtered[df_filtered['Valor'] > 0]['Valor'].sum()
    total_despesas = df_filtered[df_filtered['Valor'] < 0]['Valor'].sum()
    saldo = total_receitas + total_despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", f"R$ {total_receitas:,.2f}")
    col2.metric("Despesas", f"R$ {total_despesas:,.2f}", delta_color="inverse")
    col3.metric("Saldo", f"R$ {saldo:,.2f}")

    st.markdown("---")

    # 3. Gráficos
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("Despesas por Categoria")
        # Filtra apenas despesas para o gráfico de pizza
        df_despesas = df_filtered[df_filtered['Valor'] < 0].copy()
        df_despesas['Valor'] = df_despesas['Valor'] * -1 # Deixar positivo para o gráfico
        
        fig_pizza = px.pie(df_despesas, values='Valor', names='Categoria', hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_graf2:
        st.subheader("Evolução no Tempo")
        # Agrupa por dia
        df_evolucao = df_filtered.groupby('Data')['Valor'].sum().reset_index()
        fig_linha = px.line(df_evolucao, x='Data', y='Valor', markers=True)
        st.plotly_chart(fig_linha, use_container_width=True)

    # 4. Tabela de Dados
    st.markdown("### Extrato Detalhado")
    st.dataframe(df_filtered)

else:
    st.warning("Nenhum dado encontrado. Adicione arquivos CSV na pasta 'extratos'.")