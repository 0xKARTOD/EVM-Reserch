import json
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from scripts.Data_API import *


def evm_prices_load():

    name = "EVM Prices"

    f = open('requests_config.json')
    api_config = json.load(f)


    data = data_by_url(
        ((list(filter(lambda x:x["api_name"] == name ,api_config)))[0]["zettablock_api"]),
        ((list(filter(lambda x:x["api_name"] == name ,api_config)))[0]["api_name"])
    )

    f.close()

    return data


def evm_prices_chart(data, token):
    
    ethereum_price = data[data["TOKEN"] == "Ethereum (ETH)"]
    second_token_price = data[data["TOKEN"] == token]

    f = open('chains_config.json')
    tokens_config = json.load(f)

    for item in tokens_config:
        if item['token'] == token:
            token_color = item['colors']
        if item['token'] == "Ethereum (ETH)":
            eth_color = item['colors']

    fig = make_subplots(specs = [[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x = ethereum_price['Date(UTC)'],
            y = ethereum_price['PRICE'],
            name = "Ethereum (ETH) price",
            marker_color = eth_color
        ),
        secondary_y = False,
    )

    fig.add_trace(
        go.Scatter(
            x = second_token_price['Date(UTC)'],
            y = second_token_price['PRICE'],
            name = token + " price",
            marker_color = token_color
        ),
        secondary_y = True,
    )

    fig.update_layout(
        xaxis_tickangle = 30,
        title = dict( x = 0.5),
        xaxis_tickfont = dict(size = 9),
        yaxis_tickfont = dict(size = 9),
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )

    f.close()

    return fig