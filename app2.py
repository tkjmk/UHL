
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
from subprocess import call
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State




scoredict = np.load("data/scoretable.npy",allow_pickle='TRUE').item()

scoredict = dict( sorted(scoredict.items(), key=lambda x: x[0].lower(), reverse = True) )



sd_data = []

for k in scoredict:
    # sd_data.append()
    s4d=[] #string for data  
    for i, name in enumerate(scoredict[k]['Players']):
        s4d.append(name)
        s4d.append(str(scoredict[k]['Scores'][0][i]))
        if i + 1 < len(scoredict[k]['Players']):
            s4d.append(' | ')
    
    sd_data.append({'Game': k.split('.')[0], 'Scores': ' '.join(s4d)})

app = dash.Dash(__name__, title = "Ultimate Hearts League")


app.layout = html.Div(children=[

html.Div(
    dash_table.DataTable(
        id='score-table',
        columns=[{'name':'Game', 'id': "Game"},{'name':'Scores', 'id': "Scores"} ], #[x.split('.')[0] for x in list(scoredict)],
        data=sd_data,
        fixed_rows={'headers': True},

        style_header_conditional=[{'if': {'column_id': 'Scores'},
        'backgroundColor': 'rgb(222, 222, 222)', 
        'color': 'rgb(183,21,53)',
        'text-align': 'left'},

        {'if': {'column_id': 'Game'},
        'backgroundColor': 'rgb(222, 222, 222)', 
        'color': 'rgb(183,21,53)',
        'text-align': 'center'}
        
        ],

        style_data_conditional=[{'if': {'column_id': 'Scores'},
        'text-align': 'left'},
        
        {'if': {'column_id': 'Game'},
        'text-align': 'center'}
        ], 

        style_table={
            'height': 365,
            'overflowY': 'scroll',
            'width': 365
        }
    ), 
    style = {'display': 'inline-block', 'verticalAlign' : "middle", 'padding-left': '200px',}
),

# html.Div(id='selected-letter')
html.Div(
    dcc.Graph(id='score-graph', figure={
            'data': [
                {'x': [1.5, 1.45, 1.32, 1.2, 1.08, 1.2, 1.25, 1.5, 1.75, 1.8, 1.92, 1.8, 1.68, 1.55, 1.5], 
                'y': [45, 60, 70, 65, 50, 30, 20, 10, 20, 30, 50, 65, 70, 60, 45], 
                'mode': 'line', 
                'line': {'color': 'rgb(183,21,53)', 'dash': 'solid'},
                'name': 'Hearts',
                'orientation': 'v',
                'showlegend': True,
                'type': 'scatter',
                'xaxis': 'x',
                'yaxis': 'y'},
                {'x': [2.5, 2.45, 2.3, 2.2, 2.3, 2.45, 2.35, 2.5, 2.65, 2.55, 2.70, 2.80, 2.70, 2.55, 2.5], 
                'y': [80, 70, 60, 50, 40, 35, 15, 15, 15, 35, 40, 50, 60, 70, 80],
                'mode': 'line', 
                'line': {'color': 'rgb(33,33,33)', 'dash': 'solid'},
                'name': 'Spades',
                'orientation': 'v',
                'showlegend': True,
                'type': 'scatter',
                'xaxis': 'x',
                'yaxis': 'y'},
            ],
            'layout': {'font': {'family': 'Courier New'},
               'legend': {'title': {'text': 'Player'}, 'tracegroupgap': 0},
               'margin': {'t': 60},
               'shapes': [{'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'x domain', 'y0': 100, 'y1': 100, 'yref': 'y'}],
               'template': '...',
               'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'title': {'text': 'Round'}},
               'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], 'title': {'text': 'Score'}}}
        },
        style = {'font-family': 'Courier New'}), 
    style = {'display': 'inline-block', 'verticalAlign' : "middle",}
),

], style = {'horizontalAlign' : "center"})


@app.callback(Output('score-graph', 'figure'),
              [Input('score-table', 'active_cell'),
               Input('score-table', 'data')])
def get_graph_for_game(active_cell, data):
    if not active_cell:
        raise PreventUpdate # https://community.plotly.com/t/initializing-empty-graph/22793 from https://community.plotly.com/t/dash-upload-data-update-graph-with-callback-cannot-read-property-data-of-null/31146
    if active_cell:
        gamename=str(data[active_cell['row']]['Game'])
        thisgame = pd.read_csv('data/' + gamename + '.csv', header = None) 
        # print(gamename)
        thisgame = pd.melt(thisgame, id_vars = [0]) #going from wide to long
        thisgame.columns = ['Player', 'Round', 'Score']
        # print(thisgame) 
        fig = px.line(thisgame, x="Round", y="Score", color='Player', template = 'plotly_white')
        # print('making plot')
        fig.update_layout(font_family="Courier New", xaxis_title='Round', yaxis_title='Score',)
        fig.add_hline(y=100) #https://community.plotly.com/t/announcing-plotly-py-4-12-horizontal-and-vertical-lines-and-rectangles/46783
        print(fig)
        return fig #active cell looks like this: {'row': 4, 'column': 1, 'column_id': 'Scores'} 





if __name__ == '__main__':
    app.run_server(debug=True)

# name = 'gameO'
# thisgame = pd.read_csv('data/' + name + '.csv', header = None) 
# thisgame = thisgame.transpose()
# new_header = thisgame.iloc[0] #grab the first row for the header
# new_header = new_header.to_list()
# thisgame = thisgame[1:] #take the data less the header row
# thisgame.columns = new_header  #set the header row as the df header
# thisgame = pd.melt(thisgame, id_vars = [0]) 
# thisgame.columns = ['Player', 'Round', 'Score'] #going from wide to long
# fig = px.line(thisgame, x=np.arange(len(thisgame)), y='TK')
# 


# fig.update_layout(title='Hearts Game Point Graph',
#                    xaxis_title='Round',
#                    yaxis_title='Score',
#       )

# fig.show()