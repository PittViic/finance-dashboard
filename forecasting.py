import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from database import carregar_do_banco

def gerar_previsao():
    # 1. Carrega dados
    df = carregar_do_banco()
    if df.empty:
        return None

    # 2. Prepara os dados (Agrupa despesas por mês)
    # Filtra só despesas
    df_desp = df[df['valor'] < 0].copy()
    df_desp['valor'] = df_desp['valor'].abs()
    
    # Cria uma coluna de data truncada para o dia 1 do mês
    df_desp['data_ref'] = df_desp['data'].dt.to_period('M').dt.to_timestamp()
    
    # Agrupa soma por mês
    df_mensal = df_desp.groupby('data_ref')['valor'].sum().reset_index()
    
    if len(df_mensal) < 3:
        return "Dados insuficientes para previsão (mínimo 3 meses de histórico)."

    # 3. Engenharia de Features para o Modelo
    # O modelo não entende data, então convertemos para "número de dias desde o início"
    df_mensal['dias'] = (df_mensal['data_ref'] - df_mensal['data_ref'].min()).dt.days
    
    X = df_mensal[['dias']] # Feature (Tempo)
    y = df_mensal['valor']  # Target (Gasto)

    # 4. Treina Regressão Linear
    modelo = LinearRegression()
    modelo.fit(X, y)

    # 5. Prever Futuro (Próximos 3 meses)
    ultima_data = df_mensal['data_ref'].max()
    datas_futuras = [ultima_data + pd.DateOffset(months=i) for i in range(1, 4)]
    
    dias_futuros = [(d - df_mensal['data_ref'].min()).days for d in datas_futuras]
    X_futuro = pd.DataFrame(dias_futuros, columns=['dias'])
    
    y_pred = modelo.predict(X_futuro)

    # 6. Criar Gráfico de Tendência (Histórico + Previsão)
    fig = go.Figure()

    # Linha Histórica (Azul)
    fig.add_trace(go.Scatter(
        x=df_mensal['data_ref'], 
        y=df_mensal['valor'],
        mode='lines+markers',
        name='Histórico Real',
        line=dict(color='blue')
    ))

    # Linha de Previsão (Vermelho Tracejado)
    # Conectamos o último ponto real ao primeiro previsto para continuidade visual
    x_prev = [df_mensal['data_ref'].iloc[-1]] + datas_futuras
    y_prev = [df_mensal['valor'].iloc[-1]] + list(y_pred)

    fig.add_trace(go.Scatter(
        x=x_prev,
        y=y_prev,
        mode='lines+markers',
        name='Previsão (IA)',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title="Tendência de Gastos e Previsão (Próx. 3 Meses)",
        xaxis_title="Mês",
        yaxis_title="Total de Despesas (R$)",
        hovermode="x unified"
    )

    return fig