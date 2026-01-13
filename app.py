import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import carregar_dados_upload, processar_dados
from database import init_db, salvar_no_banco, carregar_do_banco, limpar_banco
from ml_engine import treinar_modelo
from forecasting import gerar_previsao

# --- IMPORTS PARA O CHAT ---
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="Finanças Pro",
    page_icon="💰",
    layout="wide"
)

# Inicializa o banco de dados
init_db()

# ==============================================================================
# SIDEBAR (Barra Lateral)
# ==============================================================================
with st.sidebar:
    st.header("📂 Importar Extratos")
    uploaded_files = st.file_uploader(
        "Arraste arquivos CSV aqui:", 
        type=['csv'], 
        accept_multiple_files=True
    )
    
    # Botão de Processamento (ETL)
    if uploaded_files:
        if st.button("Processar e Salvar no Banco"):
            with st.spinner("Lendo arquivos, categorizando (IA) e salvando..."):
                # 1. Lê os arquivos da memória
                df_temp = carregar_dados_upload(uploaded_files)
                
                if not df_temp.empty:
                    # 2. Processa (Limpeza + IA Naive Bayes)
                    df_proc = processar_dados(df_temp)
                    
                    # 3. Salva no SQLite
                    salvar_no_banco(df_proc)
                    
                    st.success("✅ Dados processados e salvos com sucesso!")
                    st.rerun()

    st.markdown("---")
    
    # Seção Machine Learning (Treino)
    st.header("🧠 Inteligência Artificial")
    st.caption("Treine o modelo para categorizar automaticamente seus novos gastos.")
    if st.button("Treinar Novo Modelo"):
        with st.spinner("A IA está aprendendo com seu histórico..."):
            resultado = treinar_modelo()
            if "sucesso" in resultado:
                st.success(f"✅ {resultado}")
            else:
                st.warning(f"⚠️ {resultado}")

    st.markdown("---")

    # Configuração do Chat (Generative BI)
    st.header("💬 Configuração do Chat")
    st.caption("Insira sua API Key para conversar com os dados.")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("---")
    
    # Botão de Reset
    st.header("⚙️ Admin")
    if st.button("🗑️ Limpar Banco de Dados"):
        limpar_banco()
        st.warning("Banco de dados apagado!")
        st.rerun()

# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================
st.title("💸 Dashboard Financeiro (AI + SQL + Forecasting)")

# Carrega dados do Banco SQL
df = carregar_do_banco()

if not df.empty:
    # --- FILTROS ---
    col_filtro1, col_filtro2 = st.columns(2)
    
    # Filtro de Ano
    anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
    with col_filtro1:
        ano_selecionado = st.selectbox("Selecione o Ano", anos_disponiveis)
    
    # Filtro de Mês
    meses_disponiveis = df[df['ano'] == ano_selecionado]['mes'].unique()
    # Tenta ordenar meses cronologicamente
    ordem_meses = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    meses_ordenados = [m for m in ordem_meses if m in meses_disponiveis]
    if not meses_ordenados: meses_ordenados = meses_disponiveis

    with col_filtro2:
        mes_selecionado = st.selectbox("Selecione o Mês", meses_ordenados)
    
    # Aplica Filtros
    df_filtered = df[(df['ano'] == ano_selecionado) & (df['mes'] == mes_selecionado)]

    # --- ABAS (TABS) ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Gerencial", "📝 Extrato", "🤖 Chat com Dados", "🔮 Previsões"])

    # TAB 1: DASHBOARD
    with tab1:
        # KPIs
        total_rec = df_filtered[df_filtered['valor'] > 0]['valor'].sum()
        total_desp = df_filtered[df_filtered['valor'] < 0]['valor'].sum()
        saldo = total_rec + total_desp

        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", f"R$ {total_rec:,.2f}", delta="Entradas")
        c2.metric("Despesas", f"R$ {total_desp:,.2f}", delta="-Saídas", delta_color="inverse")
        c3.metric("Saldo Mensal", f"R$ {saldo:,.2f}", delta_color="normal")

        st.markdown("---")

        # Gráficos
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Onde gastei?")
            df_desp = df_filtered[df_filtered['valor'] < 0].copy()
            df_desp['valor'] = df_desp['valor'].abs()
            
            if not df_desp.empty:
                fig_pizza = px.pie(
                    df_desp, 
                    values='valor', 
                    names='categoria', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info("Sem despesas neste período.")

        with col_g2:
            st.subheader("Receitas vs Despesas (Ano)")
            df_ano = df[df['ano'] == ano_selecionado].copy()
            df_ano['tipo'] = df_ano['valor'].apply(lambda x: 'Receita' if x > 0 else 'Despesa')
            
            df_evo = df_ano.groupby(['mes', 'tipo'])['valor'].sum().reset_index()
            fig_bar = px.bar(
                df_evo, 
                x='mes', 
                y='valor', 
                color='tipo', 
                barmode='group',
                color_discrete_map={'Receita': 'green', 'Despesa': 'red'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # TAB 2: EXTRATO
    with tab2:
        st.dataframe(df_filtered, use_container_width=True)

    # TAB 3: CHAT (PandasAI)
    with tab3:
        st.header("🤖 Consultor Financeiro IA")
        st.markdown("Faça perguntas como: *'Qual categoria teve maior aumento em relação ao mês passado?'*")
        
        if not openai_api_key:
            st.warning("⚠️ Insira sua OpenAI API Key na barra lateral para ativar.")
        else:
            pergunta = st.text_area("Digite sua pergunta:")
            if st.button("Enviar"):
                if pergunta:
                    with st.spinner("Analisando dados..."):
                        try:
                            llm = OpenAI(api_token=openai_api_key)
                            # Passamos o DF completo para ele ter contexto histórico
                            sdf = SmartDataframe(df, config={"llm": llm})
                            resposta = sdf.chat(pergunta)
                            
                            st.write("### Resposta:")
                            st.write(resposta)
                            
                            # Se for gráfico
                            if isinstance(resposta, str) and ".png" in resposta:
                                st.image(resposta)
                        except Exception as e:
                            st.error(f"Erro na IA: {e}")
    

    # TAB 4: PREVISÕES (FORECASTING)
    with tab4:
        st.header("🔮 Bola de Cristal Financeira")
        st.markdown("Projeção de gastos para os próximos 3 meses baseada em regressão linear.")
        
        if st.button("Gerar Previsão"):
            with st.spinner("Calculando tendências..."):
                resultado = gerar_previsao()
                
                if isinstance(resultado, str):
                    # Se retornou string, é mensagem de erro (ex: dados insuficientes)
                    st.warning(resultado)
                elif resultado:
                    # Se retornou objeto gráfico Plotly
                    st.plotly_chart(resultado, use_container_width=True)
                    st.success("Previsão gerada com sucesso!")

else:
    # Empty State (Tela Inicial)
    st.info("👋 Bem-vindo ao Finanças Pro!")
    st.markdown("""
        ### Como usar:
        1. Gere dados de teste com `python gerador_dados.py` ou use seus CSVs.
        2. Arraste para a **sidebar** e clique em **Processar**.
        3. Treine a IA para categorização automática.
        4. Explore os gráficos, chat e previsões.
    """)
