import pandas as pd
import os

#lendo o arquivo csv (já editado pelo script do VBA)
df = pd.read_csv('teste.csv')

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

#exportando pra CSV
df.to_csv(os.path.expanduser('~/Downloads/GitHub/Covid_19_por_Cidade/Dados/dataset_covid_19.csv'), index = False)

#vendo quantas linhas tem
print(df.count)