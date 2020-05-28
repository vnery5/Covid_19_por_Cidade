# Covid-19 por Cidade

## Sobre o aplicativo
Esse dashboard foi construído usando o *Dash*, um framework interativo desenvolvido pelo [*Plotly*](https://plot.ly/). 

Os dados utilizados são os do [Ministério da Saúde](https://covid.saude.gov.br), coletados a partir das Secretarias Estaduais de Saúde.

A grande inspiração para o design foi [este projeto](https://dash-gallery.plotly.host/dash-oil-and-gas/), cuja documentação está disponível [aqui](https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-oil-and-gas).

### Rodando o dashboard localmente

Antes de tudo, o computador precisa ter o Python instalado.
Crie um ambiente virtual no Terminal/Prompt de Comando e ative-o:
```
virtualenv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

```

Clone o repositório do Git e instale os pacotes necessários com *pip*:

```

git clone https://github.com/Vnery5/Covid_19_por_Cidade
cd Covid_19_por_Cidade
pip install -r requirements.txt

```

Rode o aplicativo. Para acessar o dashboard, espere cerca de um minuto e clique no link http://127.0.0.1:8050.

```

python app.py

```

## Prints

![screenshot](Prints/FotoDashCovid.png)
