import pandas as pd

# ATENÇÃO AQUI: O nome da função deve ser este
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
    
    return df
