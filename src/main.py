import requests
from datetime import datetime


def extrair_dados():
    url = "https://disease.sh/v3/covid-19/vaccine/coverage/countries?lastdays=1"
    response = requests.get(url)
    return response.json()


def transformar_dados(dados_json):
    dados_tratados = []

    # Itera sobre cada país no JSON retornado
    for item in dados_json:
        pais = item['country']
        timeline = item['timeline']

        # Itera sobre as datas e valores no timeline
        for data, vacinas_aplicadas in timeline.items():
            data_formatada = datetime.strptime(
                data, "%m/%d/%y").strftime("%d-%m-%Y")

            dados_tratados.append({
                "pais": pais,
                "data": data_formatada,
                "vacinas_aplicadas": vacinas_aplicadas
            })

    return dados_tratados


if __name__ == "__main__":
    dados_json = extrair_dados()
    dados_tratados = transformar_dados(dados_json)
    print(dados_tratados)
