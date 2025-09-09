# pip install flask

from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import config_PythonsDeElite as config
import consultas

caminhoBanco = config.DB_PATH
pio.renderers.default = "browser"
nomeBanco = config.NOMEBANCO
rotas = config.ROTAS
tabelaA = config.TABELA_A
tabelaB = config.TABELA_B

#Arquivos a serem carregados
dfDrinks = pd.read_csv(f'{caminhoBanco}{tabelaA}')
dfAvengers = pd.read_csv(f'{caminhoBanco}{tabelaB}', encoding='latin1')
# outros exemplos de encodings: utf-8, cp1256, iso8859-1

# criamos o banco de dados em SQL caso nao exista
conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')

dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

html_template = f'''
    <h1>Dashboards</h1>
    <h2>Parte 01</h2>
    <ul>
        <li> <a href="{rotas[1]}">Top 10 Paises em consumo</a> </li>
        <li> <a href="{rotas[2]}">Media de consumo por tipo</a> </li>
        <li> <a href="{rotas[3]}">Consumo por região</a> </li>
        <li> <a href="{rotas[4]}">Comparativo entre Tipos</a> </li>
    </ul>
    <h2>Parte 02</h2>
    <ul>
        <li> <a href="{rotas[5]}">Comparar</a> </li>
        <li> <a href="{rotas[6]}">Upload</a> </li>
        <li> <a href="{rotas[7]}">Apagar tabela</a> </li>
        <li> <a href="{rotas[8]}">Ver Tabela</a> </li>
        <li> <a href="{rotas[9]}">V.A.A.</a> </li>
    </ul>
'''

#iniciar o flask
app = Flask(__name__)

def getDbConnect():
    conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
    conn.row_factory = sqlite3.Row
    return conn

@app.route(rotas[0])
def index():
    return render_template_string(html_template)

@app.route(rotas[1])
def grafico1():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta01, conn)
    figuraGrafico1 = px.bar(
        df,
        x = 'country',
        y = 'total_litres_of_pure_alcohol',
        title = 'Top 10 paises em sonumo de alcool!'
    )
    return figuraGrafico1.to_html()

@app.route(rotas[2])
def grafico2():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta02, conn) 
        #transforma as colunas cerveja deslitalos e vinhos e linhas criando no fim duas colunas, uma chamada bebidas com os nomes originais das colunas e outra com a media de porções com seus valores correspondentes
    df_melted = df.melt(var_name='Bebidas', value_name='Média de Porções')
    figuraGrafico2 = px.bar(
        df_melted,
        x = 'Bebidas',
        y = 'Média de Porções',
        title = 'Média de consumo global por tipo'
    )
    return figuraGrafico2.to_html()

@app.route(rotas[3])
def grafico3():
    regioes = {
        "Europa":['France','Germany','Spain','Italy','Portugal'],
        "Asia":['China','Japan','India','Thailand'],
        "Africa":['Angola','Nigeria','Egypt','Algeria'],
        "Americas":['USA','Brazil','Canada','Argentina','Mexico']
    }
    dados = []
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        # itera sobre o dicionario de regioes onde cada chave (regiao tem uma lista de paises)
        for regiao, paises in regioes.items():
            #criando a lista de placeholders para os paises dessa região
            #isso vai ser usado na consulta sql para filtrar o pais da região
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f"""
                SELECT SUM(total_litres_of_pure_alcohol) AS total
                FROM bebidas
                WHERE country IN ({placeholders})
            """
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append(
                    {
                        "Região": regiao, 
                        "Consumo Total": total
                    }
                )
    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,
        names = "Região",
        values = "Consumo Total",
        title = "Consumo total por Região"
    )
    return figuraGrafico3.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"

@app.route(rotas[4])
def grafico4():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta03, conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo','Média']
        figuraGrafico4 = px.pie(
            medias,
            names = "Tipo",
            values = "Média",
            title = "Proporção média entre os tipos de bebidas!"
        )
        return figuraGrafico4.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"
    
@app.route(rotas[5], methods=["POST","GET"])
def comparar():
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]
    
    if request.method == "POST":
        eixoX = request.form.get('eixo_x')
        eixoY = request.form.get('eixo_y')
        if eixoX == eixoY:
            return f"<h3> Selecione campos diferentes! </h3><br><a href='{rotas[0]}'>Voltar</a>"
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixoX,eixoY), conn)
        conn.close()
        figuraComparar = px.scatter(
            df,
            x = eixoX,
            y = eixoY,
            title = f"Comparação entre {eixoX} VS {eixoY}"
        )
        figuraComparar.update_traces(textposition = 'top center')
        return figuraComparar.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"

    return  render_template_string('''
        <h2> Comparar campos </h2>
        <form method="POST">
            <label> Eixo X: </label>
            <select name="eixo_x">
                    {% for opcao in opcoes %}
                        <option value='{{opcao}}'>{{opcao}}</option>
                    {% endfor %} 
            </select>
            <br><br>
                                   
            <label> Eixo Y: </label>
            <select name="eixo_y">
                    {% for opcao in opcoes %}
                        <option value='{{opcao}}'>{{opcao}}</option>
                    {% endfor %}                  
            </select>
            <br><br>
                                   
            <input type="submit" value="-- Comparar --">
        </form>
        <br><a href="{{rotaInterna}}">Voltar</a>
    ''', opcoes = opcoes, rotaInterna = rotas[0])

@app.route(rotas[6], methods=['GET','POST'])
def upload():
    if request.method == "POST":
        recebido = request.files['c_arquivo']
        if not recebido:
            return f"<h3> Nenhum arquivo enviado! </h3><br><a href='{rotas[6]}'>Voltar</a>"
        dfAvengers = pd.read_csv(recebido, encoding='latin1')
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        return  f"<h3> Upload Feito com sucesso! </h3><br><a href='{rotas[6]}'>Voltar</a>"
    return '''
        <h2> Upload da tabela Avengers! </h2>
        <form method="POST" enctype="multipart/form-data">
            <!-- Isso é um comentario no HTML -->
            <input type="file" name="c_arquivo" accept=".csv">
            <input type="submit" value="-- Carregar --">
        </form>
    '''

@app.route('/apagar_tabela/<nome_tabela>', methods=['GET'])
def apagarTabela(nome_tabela):
    conn = getDbConnect()
    # realiza o apontamento para o banco que será manipulado
    cursor = conn.cursor()
    #usaremos o try except para controlar possiveis erros
    # confirmar antes se a tabela existe
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
    # pega o resultado da cntagem(0 se nao existir e 1 se existir)
    existe = cursor.fetchone()[0] 
    if not existe :
        conn.close()
        return "Tabela não encontrada"

    try:
        cursor.execute(f'DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f"Tabela {nome_tabela} apagada com ssuceso!"

    except Exception as erro:
        conn.close()
        return f"Não foi possivel apagar a tabela erro: {erro}"
    
@app.route(rotas[8], methods=["POST","GET"])
def ver_tabela():
    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas','vingadores']:
            return f"<h3>Tabela {nome_tabela} não encontrada!</h3><br><a href={rotas[8]}>Voltar</a>"
        conn =getDbConnect()
        df = pd.read_sql_query(f"SELECT * from {nome_tabela}", conn)
        conn.close()
        tabela_html = df.to_html(classes='table table-striped')
        return f'''
            <h3>Conteudo da tabela {nome_tabela}:</h3>
            {tabela_html}
            <br><a href={rotas[8]}>Voltar</a>
        '''
    return render_template_string('''
        <marquee>Selecione a tabela a ser visualizada:</marquee>
        <form method="POST">
            <label for="tabela">Escolha a tabela abaixo:</label>
            <select name="tabela">
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
            </select>
            <input type="submit" value="Consultar Tabela">
        </form>
        <hr>
        <br><a href={{rotas[0]}}>Voltar</a>
    ''', rotas=rotas)

@app.route(rotas[7], methods=['POST','GET'])
def apagarV2():
   if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3>Tabela {nome_tabela} não permitida para apagar!</h3><br><a href={rotas[7]}>Voltar</a>"
        confirmacao = request.form.get('confirmacao')
        conn = getDbConnect()
        if confirmacao == "Sim":
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?',(nome_tabela,))
                if cursor.fetchone() is None:
                    return f"<h3>Tabela {nome_tabela} não encontrada no banco de dados! </h3><br><a href={rotas[7]}>Voltar</a>"
                cursor.execute(f'DROP TABLE IF EXISTS "{nome_tabela}"')
                conn.commit()
                conn.close()
                return f"<h3>Tabela {nome_tabela} excluida com sucesso! </h3><br><a href={rotas[7]}>Voltar</a>"
            except Exception as erro:
                conn.close()
                return f"<h3>Erro ao apagar a tabela {nome_tabela} Erro:{erro}</h3><br><a href={rotas[7]}>Voltar</a>"
   return f'''
        <html>
            <head>
                <title><marquee> CUIDADO!-  Apagar Tabela  </marquee></title>
            </head>
            <body>
            <h2> Selecione a tabela para apagar </h1>
            <form method="POST" id="formApagar">
                <label for="tabela"> Escolha na tabela abaixo: </label>
                <select name="tabela" id="tabela">
                    <option value="">Selecione...</option>
                    <option value="bebidas">Bebidas</option>
                    <option value="vingadores">Vingadores</option>
                    <option value="vingadores">Usuarios</option>
                </select>
                <input type="hidden" name="confirmacao" value="" id="confirmacao">
                <input type="submit" value="-- Apagar! --" onclick="return confirmarExclusao();">

            </form>
            <br><a href={{rotas[0]}}>Voltar</a>
            <script type="text/javascript">
                function confirmarExclusao(){{
                    var ok = confirm('Tem certeza de que deseja apagar a tabela selecionada?');
                    if(ok) {{
                        document.getElementById('confirmacao').value = 'Sim';
                        return true;
                    }}
                    else {{
                        document.getElementById('confirmacao').value = 'Não';
                        return false;
                    }}
                }}
            </script>
            </body>
        </html>
    '''

@app.route(rotas[9], methods=['GET','POST'])
def vaa_mortes_consumo():
    # cada dose corresponde a 14g de alcool puro!
    metricas_beb = {
        "Total (L de Alcool)":"total_litres_of_pure_alcohol",
        "Cerveja (Doses)":"beer_servings",
        "Destilados (Doses)":"spirit_servings",
        "Vinho (Doses)":"wine_servings"
    }

    if request.method == "POST":
        met_beb_key = request.form.get("metrica_beb") or "Total (L de Alcool)"
        met_beb = metricas_beb.get(met_beb_key, "total_litres_of_pure_alcohol")

        #semente opcional para reproduzir a mesma distribuição de paises nos vingadores
        try:
            semente = int(request.form.get("semente"))
        except:
            semente = 42
        sementeAleatoria = random.Random(semente) #gera o valor aleatorio baseado na semente escolhida.

        # le os dados do SQL
        with getDbConnect() as conn:
            dfA = pd.read_sql_query('SELECT * FROM vingadores', conn)
            dfB = pd.read_sql_query('SELECT country, beer_servings, spirit_servings, wine_servings, total_litres_of_pure_alcohol FROM bebidas', conn)

        # ---- Mortes dos vingadores
        # estrategia: somar colunas que contenha o death como true (case-insensitive)
        # contaremos não-nulos como 1, ou seja, death1 tem True? vale 1, não tem nada? vale 0
        death_cols =  [c for c in dfA.columns if "death" in c.lower()]
        if death_cols:
            dfA["Mortes"] = dfA[death_cols].notna().astype(int).sum(axis=1)
        elif "Deaths" in dfA.columns:
            # fallback obvio
            dfA["Mortes"] = pd.to_numeric(dfA["Deaths"], errors="coerce").fillna(0).astype(int)
        else: 
            dfA["Mortes"] = 0
        
        if "Name/Alias" in dfA.columns:
            col_name = "Name/Alias"
        elif "Name" in dfA.columns:
            col_name = "Name"
        elif "Alias" in dfA.columns:
            col_name = "Alias"
        else:
            possivel_texto = [c for c in dfA.columns if dfA[c].dtype == "object"]
            col_nome = possivel_texto[0] if possivel_texto else dfA.columns[0]
        dfA.rename(columns={col_name: "Personagem"}, inplace=True)

        # ---- sortear um pais para cada vingador
        paises = dfB["country"].dropna().astype(str).to_list()
        if not paises:
            return f"<h3>Não há paises na tabela de bebidas!</h3><a href={rotas[9]}>Voltar</a>"
        
        dfA["Pais"] = [sementeAleatoria.choice(paises) for _ in range(len(dfA))]
        dfB_cons = dfB[["country", met_beb]].rename(columns={
            "country":"Pais",
            met_beb : "Consumo"
        })
        base = dfA[["Personagem","Mortes","Pais"]].merge(dfB_cons, on="Pais", how="left")
        
        #filtrar apenas linhas validas
        base = base.dropna(subset=['Consumo'])
        base["Mortes"] = pd.to_numeric(base["Mortes"], errors="coerce").fillna(0).astype(int)
        base = base[base["Mortes"] >= 0]
        #correlacao (se possivel)
        corr_txt = ""
        if base["Consumo"].notna().sum() >= 3 and base["Mortes"].notna().sum() >= 3:
            try:
                corr = base["Consumo"].corr(base["Mortes"])
                # • <- faz com alt+7 (7 do teclado numerico)
                corr_txt = f" • r = {corr:.3f} "
            except Exception:
                pass

        # ----- GRAFICO SCATTER 2D: CONSUMO X MORTES (cor = pais) -------
        fig2d = px.scatter(
            base,
            x = "Consumo",
            y = "Mortes",
            color = "Pais",
            hover_name = "Personagem",
            hover_data = {
                "Pais": True,
                "Consumo": True,
                "Mortes": True
                },
            title = f"Vingadores - Mortes VS consumo de Alcool do pais ({met_beb_key}){corr_txt}"
        )
        fig2d.update_layout(
            xaxis_title = f"{met_beb_key}", 
            yaxis_title = "Mortes (contagem)",
            margin = dict(l=40, r=20, t=70, b=40)
        )
        return (
            "<h3> --- Grafico 2D --- </h3>"
            + fig2d.to_html(full_html= False)
            + "<hr>"
            + "<h3> --- Grafico 3D --- </h3>"
            + "<p> Em Breve </p>"
            + "<hr>"
            + "<h3> ---Preview dos dados --- </h3>"
            + "<p> Em Breve </p>"
            + "<hr>"
            + f"<a href={rotas[9]}>Voltar</a>"
            + "<br>"
            + f"<a href={rotas[0]}>Menu Inicial</a>"
        )

        
    return render_template_string('''
    <style>
        :root{
  --bg: #0f1220;
  --bg-elev: #171a2b;
  --text: #e9ecf1;
  --muted: #b8c0d4;
  --primary: #6ea8fe;       /* alto contraste, amigável para daltônicos */
  --primary-strong: #3f7ef2;
  --accent: #8ef0d6;
  --danger: #f08c8c;
  --border: #252a41;
  --radius: 16px;
  --shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.02);
  --gap: 14px;
  --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
}

/* Claro/escuro automáticos */
@media (prefers-color-scheme: light){
  :root{
    --bg:#f6f7fb; --bg-elev:#ffffff;
    --text:#1b2333; --muted:#5b6376;
    --border:#e6e8f0;
    --shadow: 0 10px 20px rgba(16,24,40,.08), inset 0 1px 0 rgba(255,255,255,.6);
  }
}

/* Reset suave + tipografia */
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  padding: clamp(16px, 3vw, 40px);
  font-family: var(--font);
  color: var(--text);
  background:
    radial-gradient(1200px 800px at 10% -10%, rgba(142,240,214,.08), transparent 40%),
    radial-gradient(1000px 700px at 110% 0%, rgba(110,168,254,.07), transparent 45%),
    var(--bg);
  line-height:1.5;
}

/* Título */
h2{
  margin: 0 auto clamp(18px,3vw,28px);
  max-width: 900px;
  font-size: clamp(22px, 3.4vw, 40px);
  letter-spacing:.2px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--text), var(--accent));
  -webkit-background-clip:text;
  background-clip:text;
  color: transparent;
  text-wrap: balance;
}

/* Cartão do formulário */
form{
  width: min(900px, 100%);
  margin: 0 auto;
  padding: clamp(18px, 2.8vw, 28px);
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  backdrop-filter: saturate(120%) blur(4px);
}

/* Labels e campos */
label{
  display:block;
  margin-bottom: 6px;
  color: var(--muted);
  font-weight:600;
  letter-spacing:.2px;
}

select,
input[type="number"]{
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01));
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  outline: none;
  transition: border-color .2s ease, box-shadow .2s ease, transform .06s ease;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
}

select{
  background-image:
    linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01)),
    radial-gradient(5px 5px at calc(100% - 16px) 50%, currentColor 49%, transparent 51%);
  background-repeat: no-repeat;
  background-position: right 12px center, right 8px center;
  padding-right: 36px;
  cursor:pointer;
}

select:hover,
input[type="number"]:hover{
  border-color: color-mix(in lab, var(--primary), var(--border) 30%);
}

select:focus-visible,
input[type="number"]:focus-visible{
  border-color: var(--primary);
  box-shadow: 0 0 0 4px color-mix(in lab, var(--primary) 25%, transparent);
}

/* Espaçamentos verticais consistentes */
#metrica_beb,
#semente{ margin-bottom: clamp(14px, 2vw, 18px); }

/* Botão principal */
input[type="submit"]{
  display:inline-block;
  width: 100%;
  margin-top: 4px;
  border: 0;
  border-radius: 14px;
  padding: 14px 16px;
  font-weight: 800;
  letter-spacing:.3px;
  color: #0a0f1a;
  background: linear-gradient(180deg, var(--accent), color-mix(in lab, var(--accent) 72%, #0a0f1a));
  cursor: pointer;
  transition: transform .06s ease, filter .2s ease, box-shadow .2s ease;
  box-shadow: 0 10px 22px rgba(142,240,214,.25);
}

input[type="submit"]:hover{
  filter: brightness(1.03) saturate(1.05);
  box-shadow: 0 12px 28px rgba(142,240,214,.3);
}

input[type="submit"]:active{
  transform: translateY(1px);
}

/* Texto explicativo */
p{
  max-width: 900px;
  margin: clamp(16px, 2.2vw, 22px) auto 0;
  color: var(--muted);
  font-size: clamp(14px, 1.4vw, 16px);
}

/* Link “Voltar” com aparência de botão secundário */
a[href]{
  display: inline-block;
  width: min(220px, 100%);
  text-align:center;
  margin: 14px auto 0;
  padding: 11px 14px;
  text-decoration:none;
  color: var(--text);
  border: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01));
  border-radius: 12px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
  transition: border-color .2s ease, transform .06s ease, box-shadow .2s ease, color .2s ease;
}

a[href]:hover{
  border-color: color-mix(in lab, var(--primary), var(--border) 40%);
  box-shadow: 0 6px 18px rgba(110,168,254,.18);
  color: color-mix(in lab, var(--text), var(--primary) 18%);
}

a[href]:active{ transform: translateY(1px); }

/* Estados de foco acessíveis */
:focus-visible{
  outline: 3px solid color-mix(in lab, var(--primary) 65%, transparent);
  outline-offset: 2px;
  border-radius: 12px;
}

/* Animações respeitando acessibilidade */
@media (prefers-reduced-motion: reduce){
  *{ transition:none !important; }
}

/* Pequenos refinamentos responsivos */
@media (max-width: 520px){
  form{ padding: 16px; }
  input[type="submit"]{ padding: 13px 14px; }
  a[href]{ width:100%; }
}

/* Estados de erro (prontos caso use no futuro) */
.is-error,
input[type="number"].is-error,
select.is-error{
  border-color: color-mix(in lab, var(--danger), var(--border) 30%);
  box-shadow: 0 0 0 4px color-mix(in lab, var(--danger) 20%, transparent);
}
    </style>
     <h2> V.A.A - Pais X Consumo X Mortes </h2>
        <form method="POST">
            <label for="metrica_beb"> <b> Metrica de Consumo: </b> </label>
            <select name="metrica_beb" id="metrica_beb">
                {% for metrica in metricas_beb.keys() %}
                       <option value="{{metrica}}"> {{metrica}} </option>           
                {% endfor %}
            </select>
            <br><br> 
            <label for="semente"> <b>Semente:</b> (<i>opcional, p/ reprodutibilidade</i>) </label>
            <input type="number" name="semente" id="semente" value="42">
                                  
            <br><br>
            <input type="submit" value="-- Gerar Graficos --">                                                   
        </form>
        <p>
            Esta visão sorteia um pais para cada Vingador, soma as mortes dos personagens (Usando todas as colunhas que contenham Death) e anexa o consumo de alcool do pais, ao fim plota um Scatter 2D (Consumo x Mortes) e um Grafico 3D (Pais x Mortes)
        </p>
        <br>
        <a href={{rotas[0]}}>Voltar</a>
    ''', metricas_beb = metricas_beb, rotas=rotas)



# inicia o servidor
if __name__ == '__main__':
    app.run(
        debug = config.FLASK_DEBUG,
        host =  config.FLASK_HOST,
        port =  config.FLASK_PORT
    )
