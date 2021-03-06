##importando os módulos necessários
import plotly
import plotly.graph_objs as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction

from urllib.request import urlopen
import json

import pandas as pd 
import numpy as np
import math

import locale
locale.setlocale(locale.LC_ALL, '')
#importando datetime para verificar qual o dia de hoje
from datetime import date, timedelta
        
#coletando a base de dados mais recente:
url_base_de_dados = "https://raw.githubusercontent.com/vnery5/Covid_19_por_Cidade/master/Dados/dataset_covid_19.csv"
df = pd.read_csv(url_base_de_dados)

#importando as coordenadas dos estados
with urlopen('https://raw.githubusercontent.com/luizpedone/municipal-brazilian-geodata/master/data/Brasil.json') as response:
    estados_geojson = json.load(response)

##limpando a base de dados
#renomeando as colunas
df.rename({'populacaoTCU2019':'populacao','casosAcumulado':'Casos',
'obitosAcumulado':'Óbitos','data':'Data','estado':'Estado'}, axis = 1, inplace = True)

#transformando a coluna de data para o tipo apropriado
df['Data'] = pd.to_datetime(df['Data'])

#criando as medias moveis
df['mediamovelcasos'] = df['casosNovos'].rolling(7).mean()
df['mediamovelobitos'] = df['obitosNovos'].rolling(7).mean()

#definindo uma lista de todos os estados e suas siglas pra ser usado no dropwdown
lista_estados_sigla = [
    'Brasil',
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA',
    'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
]
lista_estados = [
    'Brasil',
    'Acre','Alagoas','Amazonas','Amapá','Bahia','Ceará','Distrito Federal','Espírito Santo','Goiás','Maranhão','Minas Gerais',
    'Mato Grosso do Sul','Mato Grosso','Pará','Paraíba','Pernambuco','Piauí','Paraná','Rio de Janeiro','Rio Grande do Norte',
    'Rondônia','Roraima','Rio Grande do Sul','Santa Catarina','Sergipe','São Paulo','Tocantins'
]

##criando o dataset que servira de base para os mapas
df_estados = df.loc[(df['Data'] == df['Data'].max() - pd.DateOffset(14)) | (df['Data'] == df['Data'].max())]
#pegando apenas os estados e excluindo a linha do Brasil
df_estados = df_estados.head(56).tail(54)

#calculando a variacao das medias moveis de duas semanas
df_estados['mediamovelcasos1'] = df_estados['mediamovelcasos'].shift(1)
df_estados['mediamovelobitos1'] = df_estados['mediamovelobitos'].shift(1)
df_estados['Variação dos casos frente a média móvel de duas semanas atrás'] = round((df_estados['mediamovelcasos']/df_estados['mediamovelcasos1'] - 1)*100,2)
df_estados['Variação dos óbitos frente a média móvel de duas semanas atrás']= round((df_estados['mediamovelobitos']/df_estados['mediamovelobitos1'] - 1)*100,2)

#pegando apenas valores referentes a ultima data disponível
df_estados =df_estados.loc[df_estados['Data'] == df_estados['Data'].max()]

#determinando qual a situação de uma UF
def Status_Casos(row):
    if row['Variação dos casos frente a média móvel de duas semanas atrás'] > 15:
        val = "Crescente"
    elif row['Variação dos casos frente a média móvel de duas semanas atrás'] < -15:
        val = "Decrescente"
    else:
        val = "Estável"
    return val

def Status_Obitos(row):
    if row['Variação dos óbitos frente a média móvel de duas semanas atrás'] > 15:
        val = "Crescente"
    elif row['Variação dos óbitos frente a média móvel de duas semanas atrás'] < -15:
        val = "Decrescente"
    else:
        val = "Estável"
    return val

df_estados['Situação (Casos)'] = df_estados.apply(Status_Casos, axis=1)
df_estados['Situação (Óbitos)'] = df_estados.apply(Status_Obitos, axis=1)

#formatando as colunas de variação
df_estados['Variação dos casos frente a média móvel de duas semanas atrás'] = df_estados['Variação dos casos frente a média móvel de duas semanas atrás'].astype(str) + "%"
df_estados['Variação dos óbitos frente a média móvel de duas semanas atrás'] = df_estados['Variação dos óbitos frente a média móvel de duas semanas atrás'].astype(str) + "%"

#criando os mapas de status
fig_casos = px.choropleth(
    df_estados, geojson=estados_geojson, locations='Estado',
    color = 'Situação (Casos)',
    color_discrete_sequence=["#08306B", "#3383BE", "#ABD0E6"],
    category_orders = {"Situação (Casos)":['Crescente','Estável','Decrescente']},
    featureidkey="properties.UF",
    scope="south america",
    hover_data = ['Variação dos casos frente a média móvel de duas semanas atrás']
)

fig_casos.update_geos(fitbounds="locations", visible=False)
fig_casos.update_layout(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    title ={
        'text': f'Evolução de Casos por UF',
        'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
    },
    margin=dict(l=30, r=30, t=40, b=20)
)

fig_obitos = px.choropleth(
    df_estados, geojson=estados_geojson, locations='Estado',
    color = 'Situação (Óbitos)',
    color_discrete_sequence=["#A71016", "#F86044", "#FEDDCE"],
    category_orders = {"Situação (Óbitos)":['Crescente','Estável','Decrescente']},
    featureidkey="properties.UF",
    scope="south america",
    hover_data = ['Variação dos óbitos frente a média móvel de duas semanas atrás'] 
)
fig_obitos.update_geos(fitbounds="locations", visible=False)
fig_obitos.update_layout(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    title ={
        'text': f'Evolução de Óbitos por UF',
        'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
    },
    margin=dict(l=30, r=30, t=40, b=20)
)
#calculando as incidências e mortalidades
df_estados['Incidência'] = round(df_estados['Casos']*100000/df_estados['populacao'],2)
df_estados['Mortalidade'] = round(df_estados['Óbitos']*100000/df_estados['populacao'],2)

#criando os mapas de incidencia e mortalidade
fig_incidencia = px.choropleth(
    df_estados, geojson=estados_geojson, locations='Estado',
    color='Incidência',
    color_continuous_scale="Blues",
    featureidkey="properties.UF",
    scope="south america",
    hover_data=["Casos"]
)
fig_incidencia.update_geos(fitbounds="locations", visible=False)
fig_incidencia.update_layout(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
    title ={
        'text': f'Incidência por UF<br><span style="font-size: 12px;">(Número de Casos por 100.000 Habitantes)</span>',
        'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
    },
    margin=dict(l=30, r=30, t=40, b=20)
)
fig_mortalidade = px.choropleth(
    df_estados, geojson=estados_geojson, locations='Estado',
    color='Mortalidade',
    color_continuous_scale="Reds",
    featureidkey="properties.UF",
    scope="south america",
    hover_data=["Óbitos"]
)
fig_mortalidade.update_geos(fitbounds="locations", visible=False)
fig_mortalidade.update_layout(
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
    geo=dict(bgcolor= 'rgba(0,0,0,0)'),
    title ={
        'text': f'Mortalidade por UF<br><span style="font-size: 12px;">(Número de Óbitos por 100.000 Habitantes)</span>',
        'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
    },
    margin=dict(l=30, r=30, t=40, b=20)
)

#fazendo o dashboard e criando o servidor do Flask
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

##criando o layout da página; para mais informações, veja o arquivo styles.css e s1.css
app.layout = html.Div(
    [dcc.Store(id="aggregate_data"),
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.A(
                            html.Button("Repositório GitHub"), #botão superior esquerdo
                            href="https://github.com/vnery5/Covid_19_por_Cidade",
                            target='_blank', #abrir em uma nova aba
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div( #header
                            [
                                html.H3(
                                    "Casos e Óbitos nas Cidades Brasileiras",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Painel Interativo com Indicadores sobre a Covid-19", 
                                    style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Mais dados da Covid-19 (Brasil.IO)"), #botão superior direito
                            href="https://brasil.io/covid19/",
                            target='_blank',
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div( #começando a fazer o container com os inputs do usuário e os textos
            [
                html.Div(
                    [
                        html.P(
                            "Qual município você deseja visualizar?",
                            className="control_label",
                        ),
                        dcc.Input( #caixa de texto
                            id="cidade_input",
                            type = "text",
                            value = "",
                            placeholder = "Deixe em branco para ver uma UF ou o Brasil",
                            style = {'align':'center','justifyContent':'center'}
                        ),
                        html.P(
                            "Selecione a UF do município escolhido (com pelo menos 20 casos) ou a UF que deseja visualizar:",
                            className = "control_label"
                        ),
                        dcc.Dropdown(  #seleção da UF/Brasil
                            id='opcao_de_estados',
                            options = [{'label': i, 'value': k} for i,k in dict(zip(lista_estados,lista_estados_sigla)).items()],
                            value='Brasil',
                            placeholder = "Selecione uma UF ou o Brasil",
                            style = {'align':'center','justifyContent':'center'}
                        ),
                        html.P(
                            "Escolha qual informação você deseja visualizar:",
                            className = "control_label"
                        ),
                        dcc.RadioItems( #casos ou mortes?
                            id='opcao_casos_ou_mortes',
                            options= [{'label': i, 'value': i} for i in ['Casos','Óbitos']],
                            value='Casos',
                            labelStyle={'display': 'inline-block'},
                            style = {'align':'center','justifyContent':'center'}
                        ),
                        html.P(
                            "Para atualizar os gráficos com os casos/óbitos do município/estado escolhido, aperte o botão abaixo:",
                            className = "control_label"
                        ),
                        html.Button( #botão de verificar
                            id='botao_verificar', n_clicks=0, children='Pesquisar'
                        ),
                        html.Div(id="se_der_erro"),#pra caso der erro no gráfico, avisar o usuário aqui
                        html.Hr(), #divisória bonitinha
                        html.Div( #informações gerais
                            [
                                html.P(
                                    """Para usar o painel, selecione o munícipio que deseja
                                    visualizar e a UF onde ele se encontra (uma vez que muitas
                                    cidades brasileiras possuem o mesmo nome).""",
                                    style = {"margin-top":"25px"}
                                ),
                                html.P(
                                    """Você também pode deixar o campo do munícipio em branco, caso queira
                                    visualizar os dados totais da UF selecionada no 2º campo."""
                                ),
                                html.P(
                                    f"""Criado com Python usando os dados mais recentes do Ministério da Saúde. 
                                    Atualizado em {(date.today() - timedelta(days = 1)).strftime("%d/%m/%Y")}."""
                                ),
                            ],
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div( #criando a divisão maior, na parte direita da tela
                    [
                        html.Div( #divisão de cima, que irá conter as estatísticas
                            [
                                html.Div(
                                    [html.H6(id="novos_casos_text"), html.P("Novos Casos")],
                                    id="novos_casos",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="casos_totais_text"), html.P("Casos Totais")],
                                    id="casos_totais",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="novas_mortes_text"), html.P("Novos Óbitos")],
                                    id="novas_mortes",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="obitos_totais_text"), html.P("Óbitos Totais")],
                                    id="obitos_totais",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="incidencia_text"), html.P("Incidência")],
                                    id="incidencia",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="mortalidade_text"), html.P("Mortalidade")],
                                    id="mortalidade",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="letalidade_text"), html.P("Taxa de Letalidade")],
                                    id="letalidade",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(#divisão do lado, com o gráfico
                            [dcc.Graph(id="mainGraph")],
                            id="mainGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="grafico_mm_casos")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="grafico_mm_obitos")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="grafico_incidencia", figure = fig_incidencia)],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="grafico_mortalidade", figure = fig_mortalidade)],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="grafico_casos", figure = fig_casos)],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="grafico_obitos", figure = fig_obitos)],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

##criando as funções de atualização dos gráficos e das informações usando o decorador app.callback
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("mainGraph", "figure")],
)

#usei o State pra só gerar o gráfico quando o usuário apertar o botão
@app.callback(
    [Output('mainGraph','figure'),
    Output('se_der_erro','children'),
    Output('novos_casos_text','children'),
    Output('casos_totais_text','children'),
    Output('incidencia_text','children'),
    Output('novas_mortes_text','children'),
    Output('obitos_totais_text','children'),
    Output('mortalidade_text','children'),
    Output('letalidade_text','children')],
    [Input('botao_verificar','n_clicks')],
    [State('cidade_input','value'),
    State('opcao_de_estados','value'),
    State('opcao_casos_ou_mortes','value')]
)
def Atualizar_Grafico_Principal(n_clicks,cidade,estado,opcao):
    #if para caso o Brasil ou um UF seja selecionada:
    if cidade == "":
        if estado == "Brasil":
            #fazendo o slice do dataframe
            df_cidade = df.loc[df['regiao'] == estado]

            #criando variaveis para fazer o titulo dos gráficos
            data_atual = df_cidade['Data'].dt.strftime('%d/%m/%Y').values.tolist()[-1]
            titulo_casos = f"Número de Casos no {estado} ({data_atual})"
            titulo_obitos = f"Número de Óbitos no {estado} ({data_atual})"
        else:
            #fazendo o slice do dataframe
            df_cidade = df.loc[(df['Estado'] == estado) & (df['municipio'].isnull())]

            #criando variaveis para fazer o titulo dos gráficos
            data_atual = df_cidade['Data'].dt.strftime('%d/%m/%Y').values.tolist()[-1]
            uf = lista_estados[lista_estados_sigla.index(estado)]
            titulo_casos = f"Número de Casos em {uf} ({data_atual})"
            titulo_obitos = f"Número de Óbitos em {uf} ({data_atual})"
    else:
        #coletando o nome da cidade e controlando para o nome ficar formatado da forma apropriada
        #temos que fazer um controle para "de","dos","das"
        lista_artigos = ["de","do","da","dos","das"]
        if " " in cidade:
            nomes_da_cidade = str(cidade).split()
            cidade_formatada = ""
            for nome in nomes_da_cidade:
                if nome not in lista_artigos:
                    cidade_formatada += f"{nome.capitalize()} "
                else:
                    cidade_formatada += f"{nome} "
            #tirando o espaço que fica no final do nome
            cidade = cidade_formatada[:-1]
        else:
            cidade = str(cidade).capitalize()

        #gerando o dataframe com os casos e óbitos só daquela cidade
        df_cidade = df.loc[(df['municipio'] == cidade) & (df['Estado'] == estado)]

        #criando variaveis para achar o titulo do grafico
        data_atual = df_cidade['Data'].dt.strftime('%d/%m/%Y').values.tolist()[-1]
        titulo_casos = f"Número de Casos em {cidade}-{estado} ({data_atual})"
        titulo_obitos = f"Número de Óbitos em {cidade}-{estado} ({data_atual})"

    #controle de erros
    if df_cidade.empty == True:
        erro = "Verifique se o nome da cidade está escrito corretamente e se você selecionou o estado correto!"
        fig = {}
        strzero = str(0)
        return fig, erro, strzero, strzero, strzero, strzero, strzero, strzero, strzero
    else:
        #se deu tudo certo, gerar o gráfico
        erro = ""

        #capturando e formatando todas as datas desde que a cidade registrou o 1º caso
        datas = df_cidade['Data'].dt.strftime('%d/%m/%Y').values.tolist()
        #capturando o número de dias que se passaram desde o 1º caso
        num_dias = len(datas)
        #fazendo uma array [1,2…,numero de dias]
        eixo_x = np.arange(num_dias)

        #capturando o número atual acumulado de casos e mortes da cidade
        num_de_casos = int(df_cidade['Casos'].tail(1))
        num_de_mortes = int(df_cidade['Óbitos'].tail(1))

        #criando o objeto gráfico
        fig = go.Figure()

        if opcao == "Casos":
            #se a pessoa selecionar um estado ou o Brasil:
            if cidade == "":
                df_cidade_prim_caso = df_cidade.loc[df_cidade['Casos'] > 1000]
                num_inicial_de_casos = int(df_cidade_prim_caso['Casos'].head(1))
                casos_uma_semana = [round(num_inicial_de_casos * (2 ** (x/7)),0) for x in eixo_x]
                legendacasos1 = "Dobrando a cada semana (a partir do 1000º caso)"
                casos_dez_dias  = [round(num_inicial_de_casos * (2 ** (x/10)),0) for x in eixo_x]
                legendacasos2 = "Dobrando a cada dez dias (a partir do 1000º caso)"
                casos_duas_semanas  = [round(num_inicial_de_casos * (2 ** (x/14)),0) for x in eixo_x]
                legendacasos3 = "Dobrando a cada duas semanas (a partir do 1000º caso)"

            else:
                #capturando o número inicial de casos (referente à primeira data disponível) 
                #e criando as funções das retas auxiliares
                num_inicial_de_casos = int(df_cidade['Casos'].head(1))
                casos_uma_semana = [round(num_inicial_de_casos * (2 ** (x/7)),0) for x in eixo_x]
                legendacasos1 = "Dobrando a cada semana (a partir do 10º caso)"
                casos_dez_dias  = [round(num_inicial_de_casos * (2 ** (x/10)),0) for x in eixo_x]
                legendacasos2 = "Dobrando a cada dez dias (a partir do 10º caso)"
                casos_duas_semanas  = [round(num_inicial_de_casos * (2 ** (x/14)),0) for x in eixo_x]
                legendacasos3 = "Dobrando a cada duas semanas (a partir do 10º caso)"

            #gráfico de casos
            fig.add_trace(
                go.Scatter(x = df_cidade['Data'], y= df_cidade['Casos'], 
                name = "Casos", line = dict(color = 'rgb(0,0,143)',width = 5), 
                fill = 'tozeroy', fillcolor = 'rgba(0,0,143,0.1)')
            )
            ##criando as linhas de cenários
            #caso seja uma UF
            if cidade == "":
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_caso['Data'], y= casos_uma_semana, 
                    name = legendacasos1, 
                    line = dict(color = 'black',width = 3, dash = 'dot')) #formatando o nome e o estilo da linha
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_caso['Data'], y= casos_dez_dias, 
                    name = legendacasos2, 
                    line = dict(color = 'purple',width = 3, dash = 'dot')) 
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_caso['Data'], y= casos_duas_semanas, 
                    name = legendacasos3, 
                    line = dict(color = 'green',width = 3, dash = 'dot'))
                )
            else:
                fig.add_trace(
                    go.Scatter(x = df_cidade['Data'], y= casos_uma_semana, 
                    name = legendacasos1, 
                    line = dict(color = 'black',width = 3, dash = 'dot')) #formatando o nome e o estilo da linha
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade['Data'], y= casos_dez_dias, 
                    name = legendacasos2, 
                    line = dict(color = 'purple',width = 3, dash = 'dot')) 
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade['Data'], y= casos_duas_semanas, 
                    name = legendacasos3, 
                    line = dict(color = 'green',width = 3, dash = 'dot'))
                )
            #nomeando o eixo y e ajustando sua range
            fig.update_yaxes(title_text = "Casos", range = [0, 1.1*num_de_casos])

            ##ajustando a posição da legenda, dando título à figura e ajustando suas dimensões
            fig.update_layout(
                plot_bgcolor="#F9F9F9",
                paper_bgcolor="#F9F9F9",
                legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                title ={
                    'text': titulo_casos,
                    'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                },
                margin=dict(l=30, r=30, t=40, b=20)
            )

        else:
            #caso a pessoa selecione uma UF ou o Brasil:
            if cidade == "":
                if estado == "Brasil":
                    #se for o Brasil, calcular as linhas de cenário a partir da milésima morte
                    df_cidade_prim_morte = df_cidade.loc[df_cidade['Óbitos'] > 1000]
                    num_inicial_de_obitos = int(df_cidade_prim_morte['Óbitos'].head(1))
                    obitos_uma_semana = [round(num_inicial_de_obitos * (2 ** (x/7)),0) for x in eixo_x]
                    legendaobitos1 = "Dobrando a cada semana (a partir do 1000º óbito)"
                    obitos_dez_dias  = [round(num_inicial_de_obitos * (2 ** (x/10)),0) for x in eixo_x]
                    legendaobitos2 = "Dobrando a cada dez dias (a partir do 1000º óbito)"
                    obitos_duas_semanas  = [round(num_inicial_de_obitos * (2 ** (x/14)),0) for x in eixo_x]
                    legendaobitos3 = "Dobrando a cada duas semanas (a partir do 1000º óbito)"
                else:
                    #se for uma estado, a partir do 100º óbito
                    df_cidade_prim_morte = df_cidade.loc[df_cidade['Óbitos'] > 100]
                    num_inicial_de_obitos = int(df_cidade_prim_morte['Óbitos'].head(1))
                    obitos_uma_semana = [round(num_inicial_de_obitos * (2 ** (x/7)),0) for x in eixo_x]
                    legendaobitos1 = "Dobrando a cada semana (a partir do 100º óbito)"
                    obitos_dez_dias  = [round(num_inicial_de_obitos * (2 ** (x/10)),0) for x in eixo_x]
                    legendaobitos2 = "Dobrando a cada dez dias (a partir do 100º óbito)"
                    obitos_duas_semanas  = [round(num_inicial_de_obitos * (2 ** (x/14)),0) for x in eixo_x]
                    legendaobitos3 = "Dobrando a cada duas semanas (a partir do 100º óbito)"
                
            else:
                #se for um municipio, a partir do 1º óbito
                #capturando o número inicial de óbitos (referente à primeira data disponível) e criando as funções das retas auxiliares
                if num_de_mortes > 0:
                    df_cidade_prim_morte = df_cidade.loc[df_cidade['Óbitos'] > 0]
                    num_inicial_de_obitos = int(df_cidade_prim_morte['Óbitos'].head(1))
                    obitos_uma_semana = [round(num_inicial_de_obitos * (2 ** (x/7)),0) for x in eixo_x]
                    legendaobitos1 = "Dobrando a cada semana (a partir do 1º óbito)"
                    obitos_dez_dias  = [round(num_inicial_de_obitos * (2 ** (x/10)),0) for x in eixo_x]
                    legendaobitos2 = "Dobrando a cada dez dias (a partir do 1º óbito)"
                    obitos_duas_semanas  = [round(num_inicial_de_obitos * (2 ** (x/14)),0) for x in eixo_x]
                    legendaobitos3 = "Dobrando a cada duas semanas (a partir do 1º óbito)"
                
            #gráfico de óbitos
            fig.add_trace(
                go.Scatter(x = df_cidade['Data'], y= df_cidade['Óbitos'], 
                name = "Óbitos", line = dict(color = 'rgb(143,0,0)',width = 5), 
                fill = 'tozeroy', fillcolor = 'rgba(143,0,0,0.1)')
            )
            #criando as linhas de cenários
            if num_de_mortes > 0:
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_morte['Data'], y = obitos_uma_semana,  
                    name = legendaobitos1, 
                    line = dict(color = 'black', width = 3, dash = 'dot'))
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_morte['Data'], y= obitos_dez_dias, 
                    name = legendaobitos2, 
                    line = dict(color = 'purple',width = 3, dash = 'dot'))
                )
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_morte['Data'], y= obitos_duas_semanas, 
                    name = legendaobitos3, 
                    line = dict(color = 'green',width = 3, dash = 'dot'))
                )

            #nomeando e ajustando a altura dos eixos y
            fig.update_yaxes(title_text = "Mortes", range = [0, 1.1*num_de_mortes])

            ##ajustando a posição da legenda, dando título à figura e ajustando suas dimensões
            fig.update_layout(
                plot_bgcolor="#F9F9F9",
                paper_bgcolor="#F9F9F9",
                legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                title ={
                    'text': titulo_obitos,
                    'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                },
                margin=dict(l=30, r=30, t=40, b=20)
            )

        #ajustando a range do eixo x e criando + formatando os botões de seleção temporal
        fig.update_xaxes(
            range = [datas[0],datas[num_dias - 1]],
            showgrid = False,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="Uma Semana", step="day", stepmode="backward"),
                    dict(count=14, label="Duas Semanas", step="day", stepmode="backward"),
                    dict(count=1, label="Um Mês", step="month", stepmode="backward"),
                    dict(label = "1º Caso", step="all")
                ]),
                font = dict(
                    family='Courier New, monospace', 
                    size=7
                )
            )
        )
        
        #calculando os indicadores e formatando as numerações usando o módulo locale
        #como a formatação padrão é dos EUA, temos que substituir "," por "."
        novos_casos = f"{int(df_cidade['Casos'].tail(1)) - int(df_cidade['Casos'].tail(2).head(1)):n}"
        novos_casos = novos_casos.replace(",",".")

        novos_obitos = f"{int(df_cidade['Óbitos'].tail(1)) - int(df_cidade['Óbitos'].tail(2).head(1)):n}"
        novos_obitos = novos_obitos.replace(",",".")

        #para incidencia e mortalidade é mais complicado;
        #se eles forem maior que 1000, apenas usar o replace não dá certo
        #assim, temos que separar a parte inteira da parte decimal (nesses casos)
        #usar o replace na parte inteira e depois juntá-la novamente com a parte decimal
        incidencia = f"{np.around(num_de_casos*100000/int(df_cidade['populacao'].head(1)),2)}"
        if float(incidencia) > 1000:
            incidencia_int = math.floor(float(incidencia))
            resto = round(float(incidencia) - incidencia_int,2)
            incidencia_int = f"{incidencia_int:n}"
            incidencia_int = incidencia_int.replace(",",".")
            if incidencia_int[0] == ".":
                incidencia_int = incidencia_int[1]
            incidencia = f"{incidencia_int},{str(resto)[-2:]}"
        else:
            incidencia = incidencia.replace(".",",")

        mortalidade = f"{np.around(num_de_mortes*100000/int(df_cidade['populacao'].head(1)),2)}"
        if float(mortalidade) > 1000:
            mortalidade_int = math.floor(float(mortalidade))
            resto = round(float(mortalidade) - mortalidade_int,2)
            mortalidade_int = f"{mortalidade_int:n}"
            mortalidade_int = mortalidade_int.replace(",",".")
            if mortalidade_int[0] == ".":
                mortalidade_int = mortalidade_int[1]
            mortalidade = f"{mortalidade_int},{str(resto)[-2:]}"
        else:
            mortalidade = mortalidade.replace(".",",")

        letalidade = f"{np.around(num_de_mortes/num_de_casos*100,2):n}%"
        letalidade = letalidade.replace(".",",")

        num_de_casos = f"{num_de_casos:n}"
        num_de_casos = num_de_casos.replace(",",".")

        num_de_mortes = f"{num_de_mortes:n}"
        num_de_mortes = num_de_mortes.replace(",",".")

        return fig, erro, novos_casos, num_de_casos, incidencia, novos_obitos, num_de_mortes, mortalidade, letalidade

##criando a funcao pra atualizar os graficos de novos casos e óbitos
@app.callback(
    [Output('grafico_mm_casos','figure'),
    Output('grafico_mm_obitos','figure')],
    [Input('botao_verificar','n_clicks')],
    [State('cidade_input','value'),
    State('opcao_de_estados','value'),]
)
def Atualizar_Graficos_Secundarios(n_clicks,cidade,estado):
    #if para caso o Brasil ou um UF seja selecionada:
    if cidade == "":
        if estado == "Brasil":
            df_cidade = df.loc[df['regiao'] == estado]
            titulo_casos = "Número de Novos Casos no Brasil"
            titulo_obitos = "Número de Novos Óbitos no Brasil"
        else:
            df_cidade = df.loc[(df['Estado'] == estado) & (df['municipio'].isnull())]
            estado = lista_estados[lista_estados_sigla.index(estado)]
            titulo_casos = f"Número de Novos Casos em {estado}"
            titulo_obitos = f"Número de Novos Óbitos em {estado}"
    else:
        #coletando o nome da cidade e controlando para o nome ficar formatado da forma apropriada
        #temos que fazer um controle para "de","dos","das"
        lista_artigos = ["de","do","da","dos","das"]
        if " " in cidade:
            nomes_da_cidade = str(cidade).split()
            cidade_formatada = ""
            for nome in nomes_da_cidade:
                if nome not in lista_artigos:
                    cidade_formatada += f"{nome.capitalize()} "
                else:
                    cidade_formatada += f"{nome} "
            
            cidade = cidade_formatada[:-1]
        else:
            cidade = str(cidade).capitalize()
        #gerando o dataframe com os casos e óbitos só daquela cidade
        df_cidade = df.loc[(df['municipio'] == cidade) & (df['Estado'] == estado)]
        titulo_casos = f"Número de Novos Casos em {cidade}-{estado}"
        titulo_obitos = f"Número de Novos Óbitos em {cidade}-{estado}"

    #controle de erros
    if df_cidade.empty == True:
        fig_mm_casos = {}
        fig_mm_obitos = {}
        return fig_mm_casos, fig_mm_obitos
    else: #se está tudo certo
        #recalculando as medias moveis para ficarem certinhas no início da série
        df_cidade['mediamovelcasos'] = df_cidade['casosNovos'].rolling(7).mean()
        df_cidade['mediamovelobitos'] = df_cidade['obitosNovos'].rolling(7).mean()

        df_cidade.rename({'mediamovelcasos':'Média Móvel de Novos Casos','mediamovelobitos':'Média Móvel de Novos Óbitos',
        'casosNovos':'Novos Casos','obitosNovos':'Novos Óbitos'}, axis = 1, inplace = True)

        ##criando o objeto gráfico dos novos casos
        fig_mm_casos = go.Figure()
        #gráfico de novos casos
        fig_mm_casos.add_trace(
            go.Bar(x = df_cidade['Data'], y = df_cidade['Novos Casos'], 
            name = "Novos Casos"
            )
        ) 
        fig_mm_casos.update_traces(marker_color='rgb(143,180,225)')
        #adicionando a linha da média móvel
        fig_mm_casos.add_trace(
            go.Scatter(
                x = df_cidade['Data'], y = df_cidade['Média Móvel de Novos Casos'],
                name = "Média Móvel de Novos Casos", line = dict(color = 'rgb(0,0,143)',width = 4)
            )
        )
        fig_mm_casos.update_layout(
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            showlegend = False, 
            title ={
                'text': titulo_casos,
                'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
            },
            margin=dict(l=30, r=30, t=40, b=20)
        )
        
        ##criando o objetivo gráfico de novos óbitos
        fig_mm_obitos = go.Figure()
        #gráfico de novos casos
        fig_mm_obitos.add_trace(
            go.Bar(x = df_cidade['Data'], y = df_cidade['Novos Óbitos'], 
            name = "Novos Óbitos"
            )
        ) 
        fig_mm_obitos.update_traces(marker_color='rgb(225,180,143)')
        #adicionando a linha da média móvel
        fig_mm_obitos.add_trace(
            go.Scatter(
                x = df_cidade['Data'], y = df_cidade['Média Móvel de Novos Óbitos'],
                name = "Média Móvel de Novos Óbitos", line = dict(color = 'rgb(143,0,0)',width = 4)
            )
        )
        fig_mm_obitos.update_layout(
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            showlegend = False, 
            title ={
                'text': titulo_obitos,
                'y':0.96, 'x': 0.04, 'xanchor':'left', 'yanchor':'top'
            },
            margin=dict(l=30, r=30, t=40, b=20)
        )
        return fig_mm_casos, fig_mm_obitos
    
##rodando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)