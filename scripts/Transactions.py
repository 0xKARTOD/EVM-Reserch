import json
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from scripts.Data_API import *

from datetime import timedelta

def txs_distribution(data):
    last_date = (max(data['Date(UTC)']))

    last_month_data = (data[data['Date(UTC)'].between((last_date - timedelta(days = 180)), last_date)])

    A = (last_month_data.groupby(by = [last_month_data["Date(UTC)"].dt.day_name(), last_month_data["CHAIN"]])['Value'].mean()).to_frame()
    A['Day of Week'] = A.index.get_level_values(0)
    A['CHAIN'] = A.index.get_level_values(1)

    sorter = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sorterIndex = dict(zip(sorter,range(len(sorter))))
    A['Day_id'] = A['Day of Week']
    A['Day_id'] = A['Day_id'].map(sorterIndex)
    A.sort_values('Day_id', inplace=True)

    A['Value'] = round(A['Value'], 2)

    A = A.reset_index(drop=True)


    B = (last_month_data.groupby(by = last_month_data["CHAIN"])['Value'].mean()).to_frame()
    B['CHAIN'] = B.index.get_level_values(0)
    B = B.reset_index(drop=True)
    
    result = A.merge(B, on='CHAIN', how='inner', suffixes=('_1', '_2'))

    result['Percentage'] = round(result['Value_1']/result['Value_2']*100, 2)

    result = result.rename(columns = {"Value_1": "Value"})

    return result

def transactions(data):

    f = open('chains_config.json')
    chains_config = json.load(f)

    chains = data['CHAIN'].unique()

    res_distribution = (txs_distribution(data))

    data_sum = data.groupby('CHAIN').sum()
    data_sum['CHAIN'] = data_sum.index.get_level_values(0)
    data_sum['Color'] = [(list(filter(lambda x:x["chain_name"]==y,chains_config)))[0]['colors'] for y in data_sum.index]

    data_sum = data_sum.reset_index(drop=True)


    res_distribution['Color'] = [(list(filter(lambda x:x["chain_name"]==y, chains_config)))[0]['colors'] for y in res_distribution['CHAIN']]

    res_distribution = res_distribution.drop(columns=['Day_id'])

    # Plots

    fig = make_subplots(
        rows = 1, 
        cols = 2, 
        column_widths = [0.8, 0.2],
        specs=[[{'type':'xy'}, {'type':'domain'}]]
    )

    for chain in chains:
        data_chain = data[data["CHAIN"] == chain]
        fig.add_trace(go.Scatter(
            x = data_chain["Date(UTC)"], 
            y = data_chain["Value"],
            name = chain,
            showlegend = False,
            marker_color = ((list(filter(lambda x:x["chain_name"]==chain,chains_config)))[0]["colors"])
            ), 
            row = 1, col = 1)

    fig.add_trace(go.Pie(
        labels = data_sum['CHAIN'], 
        values = data_sum['Value'], 
        name = "Total transactions count", 
        marker_colors = data_sum['Color'], 
        showlegend=False, 
        textinfo = 'label+percent',
        marker_line = dict(color='#000000', width=2)
        ), row = 1, col = 2)
    fig.update_layout(
        title = "EVM Transactions over time<br><sup>Transactions count each day and pie chart - the total number of transactions for all time</sup>", 
        xaxis_title = "Date", 
        yaxis_title = "Transactions",
        height = 500,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white')
    )
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig.update_layout(xaxis=dict(rangeselector = dict(font = dict( color = "black"))))

    fig2 = px.scatter(
        res_distribution,
        x = 'Day of Week',
        y = 'CHAIN',
        size = 'Percentage',
        color = 'Percentage',
        height = 700,
        hover_data = ['Value'],
        color_continuous_scale = px.colors.sequential.Oryel,
        title = "Distribution by day of week (Last 6 months)<br><sup>The blue square is the most active day of the week, and the pink star is the most passive</sup><br><sup>Percentage = Average # of transactions for each day divided by Average # of transactions for each chain</sup>"
    )
    fig2.update_layout(
        xaxis_tickangle = 30,
        title = dict( x = 0.5),
        xaxis_tickfont = dict(size = 9),
        yaxis_tickfont = dict(size = 9),
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        yaxis_title = "Chain"
    )

    for chain in chains:
        row = res_distribution[res_distribution["CHAIN"] == chain]['Value'].idxmax()
        fig2.add_trace(go.Scatter(
            x = [res_distribution.loc[[row]]['Day of Week']], 
            y = [chain], 
            mode = 'markers',
            marker_symbol = 'diamond-x',
            marker_size = 20,
            marker_line=dict(width=2, color = '#FFFFFF'),
            showlegend = False,
            marker_color = '#4848F4',
            name = '<-- Maximum of the week'
            ))

    for chain in chains:
        row = res_distribution[res_distribution["CHAIN"] == chain]['Value'].idxmin()
        fig2.add_trace(go.Scatter(
            x = [res_distribution.loc[[row]]['Day of Week']], 
            y = [chain], 
            mode = 'markers',
            marker_symbol = 'hexagram',
            marker_size = 20,
            marker_line=dict(width=2, color = '#FFFFFF'),
            showlegend = False,
            marker_color = '#F700FF',
            name = 'Minimum of the week -->'
            ))

    f.close()

    return fig, fig2


def transactions_by_chain_by_time(data):

    last_date = (max(data['Date(UTC)']))
    _columns = ['Value_1M', 'Value_3M', 'Value_6M', 'Value_1Y']
    _days = [30, 90, 180, 365]
    _color = ['#FF0000', '#F7FF00', '#08FF00', '#00AAFF']

    fig = go.Figure()

    for i in range (len(_columns)):
        (globals()[_columns[i]]) = (data[data['Date(UTC)'].between((last_date - timedelta(days = _days[i])), last_date)]).groupby('CHAIN').mean()
        (globals()[_columns[i]])['CHAIN'] = (globals()[_columns[i]]).index.get_level_values(0)
        (globals()[_columns[i]]) = (globals()[_columns[i]]).reset_index(drop=True)

        fig.add_trace(go.Bar(
            x = (globals()[_columns[i]])['Value'],
            y = (globals()[_columns[i]])['CHAIN'],
            orientation='h',
            showlegend = False,
            name = 'Last ' + _columns[i][-2:],
            marker_color = _color[i],
            text = ['Last ' + _columns[i][-2:] + ' : ' + "%.2f" %(v/1e6) + 'M' for v in (globals()[_columns[i]])['Value']],
            textposition = 'inside'
        ))

    fig.update_layout(
        title = "Average daily transactions<br><sup>Comparison of the average number of transactions in different periods</sup>", 
        xaxis_title = "Average daily txs", 
        yaxis_title = "Chain",
        height = 700,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        barmode='group'
        #template = 'plotly_dark'
    )

    return fig