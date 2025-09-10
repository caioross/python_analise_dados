from flask import Flask, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px

DB_PATH = "filmes.db"
app = Flask(__name__)

def carregar_df():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM filmes", conn)
    return df

@app.route("/")
def index():
    html = """
    <h1>Análise de Filmes</h1>
    <p>Escolha uma opção:</p>
    <a href="/grafico"><button>Gráfico: Quantidade de filmes por Nota</button></a><br>
    <a href="/tabela"><button>Ver Tabela + Estatísticas</button></a><br>
    <a href="/grafico_diretor_totais"><button>Barras: total de filmes por diretor</button></a><br>
    """
    return render_template_string(html)

@app.route("/grafico")
def grafico():
    df = carregar_df()
    df = df.dropna(subset=["Nota"]).copy()
    df["Nota_arred"] = df["Nota"].round(1)

    base = (
        df.groupby("Nota_arred", as_index=False)
          .agg(Qtd=("Titulo", "count"))
          .sort_values("Nota_arred")
    )

    if base.empty:
        return render_template_string("<h2>Sem dados de nota para plotar.</h2><a href='/'>Voltar</a>")

    fig = px.scatter(
        base,
        x="Nota_arred",
        y="Qtd",
        size="Qtd",
        hover_data=["Nota_arred", "Qtd"],
        title="Quantidade de filmes por Nota",
        labels={"Nota_arred": "Nota", "Qtd": "Quantidade de filmes"}
    )
    grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    html = """
    <h1>Gráfico</h1>
    <div>{{grafico|safe}}</div>
    <br>
    <a href="/"><button>Voltar</button></a>
    """
    return render_template_string(html, grafico=grafico_html)

def carregar_df():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM filmes", conn)
    return df

@app.route("/tabela")
def tabela():
    df = carregar_df()

    total_filmes = len(df)
    notas_validas = df["Nota"].dropna() if "Nota" in df.columns else pd.Series([])

    media_nota = round(notas_validas.mean(), 2) if not notas_validas.empty else None
    mediana_nota = round(notas_validas.median(), 2) if not notas_validas.empty else None
    min_nota = round(notas_validas.min(), 2) if not notas_validas.empty else None
    max_nota = round(notas_validas.max(), 2) if not notas_validas.empty else None

    tabela_html = df.to_html(index=False)

    stats_html = "<ul>"
    stats_html += f"<li>Total de filmes: <b>{total_filmes}</b></li>"
    stats_html += f"<li>Média das notas: <b>{media_nota if media_nota is not None else 'N/A'}</b></li>"
    stats_html += f"<li>Mediana das notas: <b>{mediana_nota if mediana_nota is not None else 'N/A'}</b></li>"
    stats_html += f"<li>Nota mínima: <b>{min_nota if min_nota is not None else 'N/A'}</b></li>"
    stats_html += f"<li>Nota máxima: <b>{max_nota if max_nota is not None else 'N/A'}</b></li>"
    stats_html += "</ul>"

    html = """
    <h1>Tabela & Estatísticas</h1>
    <h3>Estatísticas rápidas</h3>
    <div>{{stats|safe}}</div>
    <h3>Tabela completa (todas as colunas do banco)</h3>
    <div style="max-width: 100%; overflow-x: auto;">{{tabela|safe}}</div>
    <br>
    <a href="/"><button>Voltar</button></a>
    """
    return render_template_string(html, stats=stats_html, tabela=tabela_html)


@app.route("/grafico_diretor_totais")
def filmes_diretor():
    df = carregar_df()
    if "Direcao" not in df.columns and "Direção" in df.columns:
        df = df.rename(columns={"Direção": "Direcao"})

    g = (
        df["Direcao"].fillna("").astype(str).str.strip()
          .replace({"N/A": ""})
    )
    g = g[g.ne("")]
    g = g.value_counts().reset_index()
    g.columns = ["Diretor", "Quantidade"]
    g = g.sort_values("Quantidade", ascending=True)

    fig = px.bar(g, x="Diretor", y="Quantidade",
                 title="Total de Filmes por Diretor (ordem crescente)",
                 template="plotly_dark")
    fig.update_layout(
        title_x=0.5, height=520, bargap=0.3,
        margin=dict(l=30, r=30, t=60, b=120),
        paper_bgcolor="#111", plot_bgcolor="#111",
        xaxis_tickangle=-45
    )

    grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    html = """
    <style>
      body{margin:0;background:#111;color:#eee;font-family:Arial}
      #wrap{max-width:1200px;margin:0 auto}
      .plot{margin:0}
    </style>
    <div id="wrap">
      <div class="plot">{{grafico|safe}}</div>
    </div>
    """
    return render_template_string(html, grafico=grafico_html)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
