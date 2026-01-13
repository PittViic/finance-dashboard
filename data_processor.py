import pandas as pd
# Importamos a função de previsão da IA
from ml_engine import prever_categoria_ml

def carregar_dados_upload(arquivos):
    if not arquivos:
        return pd.DataFrame()
    
    df_list = []
    for arquivo in arquivos:
        df = pd.read_csv(arquivo)
        df_list.append(df)
    
    dados = pd.concat(df_list, ignore_index=True)
    return dados

def categorizar_despesa(descricao):
    # 1. TENTA USAR A INTELIGÊNCIA ARTIFICIAL
    categoria_ml = prever_categoria_ml(descricao)
    if categoria_ml:
        return categoria_ml
    
    # 2. SE NÃO TIVER IA, USA AS REGRAS MANUAIS (FALLBACK)
    descricao = str(descricao).lower()
    if 'uber' in descricao or '99' in descricao or 'posto' in descricao:
        return 'Transporte'
    elif 'ifood' in descricao or 'restaurante' in descricao or 'mercado' in descricao:
        return 'Alimentação'
    elif 'netflix' in descricao or 'spotify' in descricao or 'amazon' in descricao:
        return 'Assinaturas'
    elif 'salario' in descricao or 'pix recebido' in descricao:
        return 'Receita'
    else:
        return 'Outros'

def processar_dados(df):
    if df.empty:
        return df

    df['Data'] = pd.to_datetime(df['Data'])
    df['Categoria'] = df['Descricao'].apply(categorizar_despesa)
    df['Mes'] = df['Data'].dt.month_name()
    df['Ano'] = df['Data'].dt.year
    
    df.columns = ['data', 'descricao', 'valor', 'categoria', 'mes', 'ano']
    return df