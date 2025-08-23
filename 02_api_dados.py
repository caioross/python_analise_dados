import json, requests

nome = input("Escreva o nome a ser buscado")
resposta = requests.get(f'https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}')

jsonDados = json.loads(resposta.text)

print(jsonDados[0]['res'])
