# Personal Finance Dashboard & ETL Automation

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)

## Sobre o Projeto

Este projeto é uma solução completa de **Engenharia de Dados e Visualização** voltada para finanças pessoais. Ele resolve o problema da descentralização de informações financeiras, automatizando a ingestão de extratos bancários e gerando insights visuais instantâneos.

Diferente de planilhas manuais, esta aplicação utiliza um pipeline de **ETL (Extract, Transform, Load)** para processar arquivos brutos (`.csv`), categorizar despesas automaticamente com lógica condicional e apresentar KPIs em um dashboard interativo.

## Funcionalidades

* **ETL Automatizado:** Script em Python que lê múltiplos arquivos CSV, trata tipos de dados (datetime/float) e consolida em um único DataFrame.
* **Categorização Inteligente:** Algoritmo que lê a descrição da transação e atribui categorias (ex: Uber -> Transporte) automaticamente.
* **Dashboard Interativo:** Interface web construída com **Streamlit** permitindo filtros por mês e análises dinâmicas.
* **Monitoramento (Watcher):** Script auxiliar (`monitor.py`) que vigia a pasta de dados e notifica quando novos extratos são adicionados.

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Manipulação de Dados:** Pandas
* **Visualização:** Plotly & Streamlit
* **Automação:** Watchdog Library

## Estrutura do Projeto

```text
dashboard-financas/
├── extratos/          # Pasta onde os CSVs brutos são depositados
├── app.py             # Aplicação Front-end (Streamlit)
├── data_processor.py  # Motor de processamento de dados (Back-end logic)
├── monitor.py         # Script de automação de arquivos
├── requirements.txt   # Dependências do projeto
└── README.md          # Documentação
