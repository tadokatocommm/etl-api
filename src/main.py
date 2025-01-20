import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Integração com Logfire
import logging
import logfire
from logging import basicConfig, getLogger
# Configura o Logfire e adiciona o handler
logfire.configure()
basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logger = getLogger(__name__)
logger.setLevel(logging.INFO)

from database import Base, CasosCovid

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def criar_tabela():
    Base.metadata.create_all(engine)
    logger.info("Tabela criada/verificada com sucesso!")


def extrair_dados():
    url = "https://disease.sh/v3/covid-19/vaccine/coverage/countries?lastdays=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Erro na API: {response.status_code}")
        return None


def transformar_dados(dados_json):
    dados_tratados = []
    timestamp = datetime.now()

    for item in dados_json:
        pais = item['country']
        timeline = item['timeline']

        for data, vacinas_aplicadas in timeline.items():
            data_formatada = datetime.strptime(
                data, "%m/%d/%y").strftime("%d-%m-%Y")

            dados_tratados.append({
                "pais": pais,
                "data": data_formatada,
                "vacinas_aplicadas": vacinas_aplicadas,
                "timestamp": timestamp
            })

    return dados_tratados

def salvar_dados_postgres(dados_tratados):
    session = Session() 
    try:
        novos_registros = 0 

        for dados in dados_tratados:
            novo_registro = CasosCovid(**dados)  
            session.add(novo_registro)  
            novos_registros += 1
        session.commit()  
        
        if novos_registros > 0:
            logger.info(f"[{dados_tratados[0]['timestamp']}] {novos_registros} registros salvos no PostgreSQL!")
        else:
            logger.info("Nenhum dado novo para salvar no PostgreSQL.")

    except Exception as ex:
        logger.error(f"Erro ao inserir dados no PostgreSQL: {ex}")
        session.rollback()  
    finally:
        session.close() 

if __name__ == "__main__":
    criar_tabela()
    logger.info("Iniciando ETL com atualização a cada 15 segundos... (CTRL+C para interromper)")

    while True:
        try:
            dados_json = extrair_dados()
            if dados_json:
                dados_tratados = transformar_dados(dados_json)
                logger.info(f"Dados Tratados: {dados_tratados}")  
                salvar_dados_postgres(dados_tratados)
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\nProcesso interrompido pelo usuário. Finalizando...")
            break
        except Exception as e:
            logger.error(f"Erro durante a execução: {e}")
            time.sleep(60)
