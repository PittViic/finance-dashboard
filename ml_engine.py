import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from database import carregar_do_banco

# Nome do arquivo onde salvaremos o "cérebro" treinado
MODEL_PATH = "modelo_categorias.pkl"

def treinar_modelo():
    """
    Lê os dados do banco SQL e treina a IA para entender seus padrões.
    """
    df = carregar_do_banco()
    
    # Precisamos de pelo menos algumas transações para treinar
    if df.empty or len(df) < 5:
        return "Dados insuficientes para treinar (mínimo 5 transações)."

    # X = O que a IA vai ler (Descrição)
    # y = O que a IA deve aprender (Categoria)
    X = df['descricao']
    y = df['categoria']

    # Pipeline: Transforma texto em números -> Aplica Naive Bayes
    modelo = make_pipeline(CountVectorizer(), MultinomialNB())
    modelo.fit(X, y)

    # Salva o arquivo treinado
    joblib.dump(modelo, MODEL_PATH)
    return "Modelo treinado com sucesso!"

def prever_categoria_ml(descricao):
    """
    Tenta prever a categoria usando o modelo salvo.
    Se o modelo não existir, retorna None.
    """
    try:
        modelo = joblib.load(MODEL_PATH)
        # O modelo espera uma lista, então passamos [descricao] e pegamos o 1º resultado
        predicao = modelo.predict([descricao])[0]
        return predicao
    except:
        return None  # Modelo ainda não foi treinado