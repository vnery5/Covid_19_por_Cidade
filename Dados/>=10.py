import pandas as pd
import os, glob

#lendo o arquivo csv (já editado pelo script do VBA)
df = pd.read_csv('teste.csv')

print(df.head(5))

#arrumando uns erros e só pegando as datas com pelo menos um caso
df = df[df.casosAcumulado > 9]
df = df[df.populacaoTCU2019.str[-1::] != ")"]

#arrumando os tipos das colunas
#limpando as linhas sem indicação de população
df.dropna(subset = ['populacaoTCU2019'], axis = 0, inplace = True)
df['populacaoTCU2019'] = df['populacaoTCU2019'].astype('int')
df['casosAcumulado'] = df['casosAcumulado'].astype('int')
df['obitosAcumulado'] = df['obitosAcumulado'].astype('int')
df['casosNovos'] = df['casosNovos'].astype('int')
df['obitosNovos'] = df['obitosNovos'].astype('int')

#vendo quantas linhas tem
print(df.count)

#exportando pra CSV e deletando a base de dados antiga
if os.path.isfile(os.path.expanduser('~/Downloads/GitHub/Covid_19_por_Cidade/Dados/dataset_covid_19.csv')):
    os.remove(os.path.expanduser('~/Downloads/GitHub/Covid_19_por_Cidade/Dados/dataset_covid_19.csv'))
else:
    print("Não foi possível achar o arquivo a ser excluído")
df.to_csv(os.path.expanduser('~/Downloads/GitHub/Covid_19_por_Cidade/Dados/dataset_covid_19.csv'), index = False)

#apagando o arquivo gerado pelo script do VBA
os.remove('teste.csv')

#apagando o arquivo do site do ministério da saúde
for arquivo in glob.glob(os.path.expanduser("~/Downloads/HIST_PAINEL*")):
    os.remove(arquivo)

print("Tudo certo!")