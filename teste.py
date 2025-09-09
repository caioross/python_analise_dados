import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3
import datetime

# BeautifulSoup biblioteca para parsear HTML e extrair informações.

# headers para simular um navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

baseURL = "https://www.adorocinema.com/filmes/melhores/"
filmes = []  # lista que vai armazenar os dados coletados de cada filme
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
agora = datetime.datetime.now()

paginaLimite = 2  # quantidade de paginas
card_temp_min = 1
card_temp_max = 3
pag_temp_min = 1
pag_temp_max = 2

# >>> Banco de dados SQLite simples no mesmo diretório
bancoDados = "filmes.db"

# CSV de saída
saidaCSV = f"filmes_adorocinema_{data_hoje}.csv"

for pagina in range(1, paginaLimite + 1):
    url = f"{baseURL}?page={pagina}"
    print(f"Coletando dados da pagina {pagina} : {url}")
    resposta = requests.get(url, headers=headers)

    # se o site não responder, pula para a proxima pagina
    if resposta.status_code != 200:
        print(f"Erro ao carregar a pagina {pagina}. Código do erro é: {resposta.status_code}")
        continue

    soup = BeautifulSoup(resposta.text, "html.parser")

    # cada filme aparece em uma div(card) com a classe abaixo.
    cards = soup.find_all("div", class_="card entity-card entity-card-list cf")

    # iteramos por cada card(div) de filme
    for card in cards:
        try:
            # capturar o titulo e link da pagina do filme
            titulo_tag = card.find("a", class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com" + titulo_tag['href'] if titulo_tag else None

            # capturar a nota do filme
            nota_tag = card.find("span", class_="stareval-note")
            nota = nota_tag.text.strip().replace(",", ".") if nota_tag else "N/A"

            diretor = "N/A"
            genero_block = None

            # caso exista o link acessar a pagina individual do site
            if link:
                filme_resposta = requests.get(link, headers=headers)
                if filme_resposta.status_code == 200:
                    filme_soup = BeautifulSoup(filme_resposta.text, "html.parser")

                    # captura o diretor do filme
                    diretor_tag = filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-oneline")
                    if diretor_tag:
                        diretor = (diretor_tag.text
                                   .strip()
                                   .replace("Direção:", "")
                                   .replace(",", "")
                                   .replace("|", "")
                                   .replace("\n", " ")
                                   .replace("\r", "")
                                   .strip())

                    # captura dos generos
                    genero_block = filme_soup.find("div", class_="meta-body-info")

            # captura dos generos (fallback se não acessou o link)
            if genero_block:
                generos_links = genero_block.find_all("a")
                generos = [g.text.strip() for g in generos_links]
                categoria = ", ".join(generos[:3]) if generos else "N/A"
            else:
                categoria = "N/A"

            # captura o ano de lançamento do filme
            # dica: a tag é um 'span' e o nome da classe é 'date'
            ano_tag = genero_block.find("span", class_="date") if genero_block else None
            ano = ano_tag.text.strip() if ano_tag else "N/A"

            # só adiciona o filme se todos os dados principais existirem
            if titulo != "N/A" and link is not None and nota != "N/A":
                filmes.append({
                    "Titulo": titulo,
                    "Direção": diretor,
                    "Nota": nota,
                    "Link": link,
                    "Ano": ano,
                    "Categoria": categoria
                })
            else:
                print(f"Filme incompleto ou erro na coleta de dados {titulo}")

            # aguardar um tempo aleatorio para nao sobrecarregar o site
            tempo = random.uniform(card_temp_min, card_temp_max)
            time.sleep(tempo)
            print(f'Tempo de espera: {tempo:.2f}s')
        except Exception as e:
            print(f"Erro ao processar o filme {titulo}. Erro: {e}")

    # esperar um tempo entre uma pagina e outra
    tempo = random.uniform(pag_temp_min, pag_temp_max)
    time.sleep(tempo)

# converter os dados coletados para um dataframe do pandas
df = pd.DataFrame(filmes)
print(df.head())

# salva os dados em um arquivo csv
df.to_csv(saidaCSV, index=False, encoding="utf-8-sig", quotechar="'", quoting=1)

# =========================
#  SQLite: criação e INSERT
# =========================
with sqlite3.connect(bancoDados) as conn:
    cursor = conn.cursor()

    # Tabela simples; Link único para evitar repetição ao rodar de novo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filmes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo    TEXT,
            Direcao   TEXT,
            Nota      REAL,
            Link      TEXT UNIQUE,
            Ano       TEXT,
            Categoria TEXT
        )
    ''')

    # Insere cada filme coletado
    for filme in filmes:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO filmes (Titulo, Direcao, Nota, Link, Ano, Categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                filme['Titulo'],
                filme['Direção'],  # chave do dicionário segue acento
                float(filme['Nota']) if filme['Nota'] != 'N/A' else None,
                filme['Link'],
                filme['Ano'],
                filme['Categoria']
            ))
        except Exception as e:
            print(f"Erro ao inserir filme {filme['Titulo']} no banco de dados. Detalhes: {e}")

    conn.commit()

print("---------------------------------------")
print('Dados raspados e salvos com sucesso!')
print(f"\nArquivo CSV salvo em: {saidaCSV}")
print(f"Banco de dados: {bancoDados}\n")
print("Obrigado por usar o Sistema de Bot do Seu nome")
print(f"Finalizado em: {agora.strftime('%H:%M:%S')}")
print("---------------------------------------")
