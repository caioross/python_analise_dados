from flask import Flask, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px

DB_PATH = "filmes.db"

app = Flask(__name__)

@app.route("/")
def index():
    #aqui a rota inicial
    return  None

@app.route("/grafico")
def grafico():
    #aqui rota que controi e mostra o grafico
    return  None

@app.route("/tabela")
def tabela():
    #aqui rota que controi e mostra a tabela
    return  None

if __name__ == '__main__':
    app.run(debug=True)
