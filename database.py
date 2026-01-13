import sqlite3
import pandas as pd

# Conecta ao banco (cria o arquivo se não existir)
def get_connection():
    return sqlite3.connect("financas.db")

# Cria a tabela inicial se não existir
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            valor REAL,
            categoria TEXT,
            mes TEXT,
            ano INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Salva o DataFrame no banco (Append: adiciona ao que já existe)
def salvar_no_banco(df):
    conn = get_connection()
    # Pandas tem uma função mágica que faz isso direto
    df.to_sql('transacoes', conn, if_exists='append', index=False)
    conn.close()

# Carrega os dados do banco para o Pandas
def carregar_do_banco():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM transacoes", conn)
        # Garante que a data venha como datetime e não string
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# Função extra para limpar o banco (útil para testes)
def limpar_banco():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes")
    conn.commit()
    conn.close()