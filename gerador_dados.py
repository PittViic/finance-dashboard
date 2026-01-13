import pandas as pd
import random
from datetime import datetime, timedelta

# Configuração: Quantas linhas você quer?
NUM_TRANSACOES = 500

def gerar_dados_sinteticos():
    # Padrões de descrição para a IA aprender
    # (Categoria: [Lista de palavras-chave possíveis])
    padroes = {
        'Transporte': ['Uber', '99Pop', 'Posto Shell', 'Estacionamento', 'Sem Parar', 'Gasolina Ipiranga', 'Metrô', 'Bilhete Único'],
        'Alimentação': ['McDonalds', 'Burger King', 'Supermercado Extra', 'Carrefour', 'Padaria do Zé', 'Restaurante Kilo', 'Ifood', 'Rappi'],
        'Assinaturas': ['Netflix', 'Spotify', 'Amazon Prime', 'Youtube Premium', 'Disney+', 'HBO Max'],
        'Lazer': ['Cinema', 'Ingresso.com', 'Bar do Léo', 'Steam Games', 'Playstation Store'],
        'Saúde': ['Drogasil', 'Farmácia Pague Menos', 'Consulta Dr', 'Exame Laboratório'],
        'Receita': ['Salário Mensal', 'Pix Recebido', 'Reembolso', 'Venda OLX']
    }

    dados = []
    data_inicial = datetime(2025, 1, 1)

    print(f"Gerando {NUM_TRANSACOES} transações fictícias...")

    for _ in range(NUM_TRANSACOES):
        # 1. Escolhe uma categoria aleatória
        categoria_real = random.choice(list(padroes.keys()))
        
        # 2. Escolhe uma descrição baseada na categoria + um número aleatório para variar (ex: Uber 492)
        descricao_base = random.choice(padroes[categoria_real])
        descricao = f"{descricao_base} {random.randint(100, 999)}" 
        
        # 3. Gera data aleatória nos últimos 365 dias
        dias_aleatorios = random.randint(0, 365)
        data = data_inicial + timedelta(days=dias_aleatorios)
        
        # 4. Gera valor (Negativo para gastos, Positivo para Receita)
        if categoria_real == 'Receita':
            valor = round(random.uniform(2000.00, 5000.00), 2)
        else:
            valor = round(random.uniform(-150.00, -10.00), 2)

        dados.append([data.strftime('%Y-%m-%d'), descricao, valor])

    # Cria o DataFrame e salva
    df = pd.DataFrame(dados, columns=['Data', 'Descricao', 'Valor'])
    nome_arquivo = "dataset_treino_grande.csv"
    df.to_csv(nome_arquivo, index=False)
    print(f"✅ Arquivo '{nome_arquivo}' gerado com sucesso!")

if __name__ == "__main__":
    gerar_dados_sinteticos()