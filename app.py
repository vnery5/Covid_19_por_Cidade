#importando os módulos necessários
import plotly
import plotly.graph_objs as go

import pandas as pd 
import numpy as np
import string
import locale
#formatando os numeros
locale.setlocale(locale.LC_ALL, '')

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
        
#coletando a base de dados mais recente:
df = pd.read_csv("https://raw.githubusercontent.com/vnery5/Covid_19_por_Cidade/master/Dados/dataset_covid_19.csv")

##limpando a base de dados
#renomeando as colunas
df.rename({'populacaoTCU2019':'populacao','casosAcumulado':'Casos','obitosAcumulado':'Óbitos','data':'Data'}, axis = 1, inplace = True)
#transformando a coluna de data para o tipo apropriado
df['Data'] = pd.to_datetime(df['Data'])
df.dropna(subset = ['populacao'], axis = 0, inplace = True)



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
#fazendo o dashboard e criando o servidor do Flask
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

##criando o layout da página; para mais informações, veja o arquivo styles.css e s1.css
app.layout = html.Div(
    [
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.A(
                            html.Button("Sobre o Autor"), #botão superior esquerdo
                            href="https://www.linkedin.com/in/viniciusdealmeidaneryferreira/",
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
                            html.Button("Ir para o GitHub do Projeto"), #botão superior direito
                            href="https://github.com/vnery5/Covid_19_por_Cidade/",
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
                            "Selecione a UF do município escolhido ou a UF que deseja visualizar:",
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
                            "Para atualizar o gráfico com os casos/óbitos do município escolhido, aperte o botão abaixo:",
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
                                    """Criado com Python usando os dados mais recentes do Ministério da Saúde. 
                                    Atualizado em 06/06/2020."""
                                ),
                            ],
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div( #criando a divisão maior, na parte direita datela
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
                        html.Div(#divisão de baixo, com o gráfico
                            [dcc.Graph(id="grafico")],
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
        ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

##criando as funções de atualização dos gráficos e das informações usando o decorador app.callback
#usei o State pra só gerar o gráfico quando o usuário apertar o botão
@app.callback(
    [Output('grafico','figure'),
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
def Atualizar(n_clicks,cidade,estado,opcao):
    #if para caso o Brasil ou um UF seja selecionada:
    if cidade == "":
        if estado == "Brasil":
            df_cidade = df.loc[df['regiao'] == estado]
        else:
            df_cidade = df.loc[df['estado'] == estado]
            df_cidade = df_cidade.loc[df_cidade['municipio'].isnull()]
    else:
        #coletando o nome da cidade e controlando para o nome ficar formatado da forma apropriada
        if " " in cidade:
            cidade = string.capwords(str(cidade))
        else:
            cidade = str(cidade).capitalize()
        #gerando o dataframe com os casos e óbitos só daquela cidade
        df_cidade = df.loc[df['municipio'] == cidade]
        df_cidade =df_cidade.loc[df_cidade['estado'] == estado]

    #controle de erros
    if df_cidade.empty == True:
        erro = "Verifique se o nome da cidade está escrito corretamente e se você selecionou o estado correto!"
        fig = {}
        strzero = str(0)
        return fig, erro, strzero, strzero, strzero, strzero, strzero, strzero, strzero
    else:
        #se deu tudo certo, gerar o gráfico
        erro = ""
        uf = str(df_cidade['estado'].values.tolist()[0])

        #capturando e formatando todas as datas desde que a cidade registrou o 1º caso
        datas = df_cidade['Data'].dt.strftime('%d/%m/%Y').values.tolist()
        #capturando o número de dias que se passaram desde o 1º caso
        num_dias = len(datas)
        #fazendo uma array [1,2…,numero de dias]
        eixo_x = np.arange(num_dias)
        #capturando a data atual
        data_atual = datas[num_dias - 1]

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
                legendacasos1 = "Dobrando a cada semana (a partir do 1º caso)"
                casos_dez_dias  = [round(num_inicial_de_casos * (2 ** (x/10)),0) for x in eixo_x]
                legendacasos2 = "Dobrando a cada dez dias (a partir do 1º caso)"
                casos_duas_semanas  = [round(num_inicial_de_casos * (2 ** (x/14)),0) for x in eixo_x]
                legendacasos3 = "Dobrando a cada duas semanas (a partir do 1º caso)"

            #gráfico de casos
            fig.add_trace(
                go.Scatter(x = df_cidade['Data'], y= df_cidade['Casos'], 
                name = "Casos", line = dict(color = 'red',width = 3.5), 
                fill = 'tozeroy', fillcolor = 'rgba(255,0,0,0.1)')
            )
            ##criando as linhas de cenários
            #caso seja uma UF
            if cidade == "":
                fig.add_trace(
                    go.Scatter(x = df_cidade_prim_caso['Data'], y= casos_uma_semana, 
                    name = legendacasos1, 
                    line = dict(color = 'black',width = 3, dash = 'dot')) #formatando o nome da linha e o estilo da linha
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
                    line = dict(color = 'black',width = 3, dash = 'dot')) #formatando o nome da linha e o estilo da linha
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
            #caso a pessoa selecione uma UF ou o Brasil:
            if cidade == "":
                if estado == "Brasil":
                    fig.update_layout(
                        plot_bgcolor="#F9F9F9",
                        paper_bgcolor="#F9F9F9",
                        legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                        title ={
                            'text': f"Número de Casos no {estado} ({data_atual})",
                            'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                        },
                        margin=dict(l=30, r=30, t=40, b=20)
                    )
                else:
                    uf = lista_estados[lista_estados_sigla.index(estado)]
                    fig.update_layout(
                        plot_bgcolor="#F9F9F9",
                        paper_bgcolor="#F9F9F9",
                        legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                        title ={
                            'text': f"Número de Casos em {uf} ({data_atual})",
                            'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                        },
                        margin=dict(l=30, r=30, t=40, b=20)
                    )
            #caso seja um munícipio
            else:
                fig.update_layout(
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                    title ={
                        'text': f"Número de Casos em {cidade}-{uf} ({data_atual})",
                        'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                    },
                    margin=dict(l=30, r=30, t=40, b=20)
                )


        else:
            #caso a pessoa selecione uma UF ou o Brasil:
            if cidade == "":
                if estado == "Brasil":
                    df_cidade_prim_morte = df_cidade.loc[df_cidade['Óbitos'] > 1000]
                    num_inicial_de_obitos = int(df_cidade_prim_morte['Óbitos'].head(1))
                    obitos_uma_semana = [round(num_inicial_de_obitos * (2 ** (x/7)),0) for x in eixo_x]
                    legendaobitos1 = "Dobrando a cada semana (a partir do 1000º óbito)"
                    obitos_dez_dias  = [round(num_inicial_de_obitos * (2 ** (x/10)),0) for x in eixo_x]
                    legendaobitos2 = "Dobrando a cada dez dias (a partir do 1000º óbito)"
                    obitos_duas_semanas  = [round(num_inicial_de_obitos * (2 ** (x/14)),0) for x in eixo_x]
                    legendaobitos3 = "Dobrando a cada duas semanas (a partir do 1000º óbito)"
                else:
                    df_cidade_prim_morte = df_cidade.loc[df_cidade['Óbitos'] > 100]
                    num_inicial_de_obitos = int(df_cidade_prim_morte['Óbitos'].head(1))
                    obitos_uma_semana = [round(num_inicial_de_obitos * (2 ** (x/7)),0) for x in eixo_x]
                    legendaobitos1 = "Dobrando a cada semana (a partir do 100º óbito)"
                    obitos_dez_dias  = [round(num_inicial_de_obitos * (2 ** (x/10)),0) for x in eixo_x]
                    legendaobitos2 = "Dobrando a cada dez dias (a partir do 100º óbito)"
                    obitos_duas_semanas  = [round(num_inicial_de_obitos * (2 ** (x/14)),0) for x in eixo_x]
                    legendaobitos3 = "Dobrando a cada duas semanas (a partir do 100º óbito)"
                
            else:
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
                name = "Óbitos", line = dict(color = 'blue',width = 3.5), 
                fill = 'tozeroy', fillcolor = 'rgba(0,0,255,0.1)')
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
            #caso a pessoa esteja selecionando o Brasil ou uma UF:
            if cidade == "":
                if estado == "Brasil":
                    fig.update_layout(
                        plot_bgcolor="#F9F9F9",
                        paper_bgcolor="#F9F9F9",
                        legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                        title ={
                            'text': f"Número de Óbitos no {estado} ({data_atual})",
                            'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                        },
                        margin=dict(l=30, r=30, t=40, b=20)
                    )
                else:
                    uf = lista_estados[lista_estados_sigla.index(estado)]
                    fig.update_layout(
                        plot_bgcolor="#F9F9F9",
                        paper_bgcolor="#F9F9F9",
                        legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                        title ={
                            'text': f"Número de Óbitos em {uf} ({data_atual})",
                            'y':0.96, 'x': 0.96, 'xanchor':'right', 'yanchor':'top'
                        },
                        margin=dict(l=30, r=30, t=40, b=20)
                    )
            #no caso de um munícipio ter sido selecionado
            else:
                fig.update_layout(
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    legend_orientation = 'h', legend = dict(x = -0.1,y = -0.2), 
                    title ={
                        'text': f"Número de Óbitos em {cidade}-{uf} ({data_atual})",
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
        novos_casos = f"{int(df_cidade['Casos'].tail(1)) - int(df_cidade['Casos'].tail(2).head(1)):n}"
        incidencia = f"{np.around(num_de_casos*100000/int(df_cidade['populacao'].tail(1)),2):n}"
        novos_obitos = f"{int(df_cidade['Óbitos'].tail(1)) - int(df_cidade['Óbitos'].tail(2).head(1)):n}"
        mortalidade = f"{np.around(num_de_mortes*100000/int(df_cidade['populacao'].tail(1)),2):n}"
        letalidade = f"{np.around(num_de_mortes/num_de_casos*100,2):n}%"
        num_de_casos = f"{num_de_casos:n}"
        num_de_mortes = f"{num_de_mortes:n}"

        return fig, erro, novos_casos, num_de_casos, incidencia, novos_obitos, num_de_mortes, mortalidade, letalidade

#rodando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
