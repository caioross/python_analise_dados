import pandas as pd

# carregar dados da planilha 
caminho = 'C:/Users/sabado/Desktop/Python AD Caio/01_base_vendas.xlsx'

df1 = pd.read_excel(caminho, sheet_name='Relatório de Vendas')
df2 = pd.read_excel(caminho, sheet_name='Relatório de Vendas1')

#exibir as primeiras linhas das tabelas
print('-------- Primeiro relatório --------')
print(df1.head())

print('-------- Segundo relatório --------')
print(df2.head())

#verificar se há duplicatas
print('Duplicatas no relatorio 01')
print(df1.duplicated().sum())

print('Duplicatas no relatorio 02')
print(df2.duplicated().sum())

#vamos consolidar as duas tabelas
print('Dados consolidados!')
dfConsolidado = pd.concat([df1,df2], ignore_index=True)
print(dfConsolidado.head())

# exibir o numero de clientes por cidade
clientesPorCidade = dfConsolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('Clientes por cidade')
print(clientesPorCidade)

# numero de vendas po plano!
vendasPorPlano = dfConsolidado['Plano Vendido'].value_counts()
print('Numero de vendas por Plano')
print(vendasPorPlano)

#exibir as 3 cidades com mais clientes:
top3Cidades = clientesPorCidade.head(3)
# top3Cidades = clientesPorCidade.sort_values(ascending=False).head(3)
print('Top 3 Cidades')
print(top3Cidades)

# adicionar uma nova coluna de status (exemplo ficticio de analise)
#vamos classificar os planos como 'premium' se for enterprise, os demais serão 'padrão'
dfConsolidado['Status'] = dfConsolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrão')

#exibir a distribuição dos status
statusDist = dfConsolidado['Status'].value_counts()
print('Distribuição dos status:')
print(statusDist)

#Salvar a tabela em um arquivo novo
#Primeiro em Excel
dfConsolidado.to_excel('dados_consolidados.xlsx',index=False)
print('Dados salvos na planilha do Excel')
#Depois em CSV
dfConsolidado.to_csv('dados_consolidados.csv', index=False)
print('Dados salvos em CSV')

#Mensagem final
print('----- Programa finalizado! -----')
