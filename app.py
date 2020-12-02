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


df = pd.read_csv('data/finalstats.txt')
# sorting dfcols so I can merge the headers for total, 3person and 4person hearts.
dfcols=[{"name": i, "id": i} for i in df.columns]
hdrzt=[]
hdrz3=[]
hdrz4=[]
for i in dfcols:
    if i['name'] == "Unnamed: 0":
        i['name'] = ["","Player"]
    elif i['name'].endswith('3'):
        hdrz3.append(i['name'])
        i['name'] = ['3-player', i['name']]
    elif i['name'].endswith('4'):
        hdrz4.append(i['name'])
        i['name'] = ['4-player', i['name']]
    else:
        hdrzt.append(i['name'])
        i['name'] = ['Total', i['name']]


#### reading in score dictionary
scoredict = np.load("data/scoretable.npy",allow_pickle='TRUE').item()
scoredict = dict( sorted(scoredict.items(), key=lambda x: x[0].lower(), reverse = True) ) # sorting it so latest are at top (YYYY-MM-DDX.csv)
                                                                                          # X is letter if there are multiple on that day, first one does not have a letter.
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
server = app.server


app.layout = html.Div(children=[
   html.Img(src='/assets/UHL_logo.png', style={'height':'15%', 'width':'15%'}),

   html.Hr(style={'border-top': '5px solid rgb(183,21,53)'}),

    html.H1(children='December Championship - League Table', style={'color': 'black', 'fontSize': 28, 'fontFamily': 'Courier New'} ),

    # html.Div(children='''
    #     Dash: A web application framework for Python.
    # '''),

dash_table.DataTable(
    id='league-table',
    columns=dfcols,
    data=df.to_dict('records'),
    merge_duplicate_headers=True,
        sort_action="native",
        sort_mode="multi",

    style_header={'backgroundColor': 'rgb(222, 222, 222)', 
    'color': 'rgb(183,21,53)',
    'fontWeight': 'bold' },

    style_header_conditional=[{
        'if': {'column_id': ['GP3', 'GP4']},
        'borderLeft': '1.5px rgb(183,21,53) solid',
        }],

    style_data_conditional=[{
        'if': {'column_id': hdrz3},
        'backgroundColor': 'rgb(242  , 242, 242)',
        'color': 'black',
    }, {
    
       'if': {'column_id': ['GP3', 'GP4']},
        'borderLeft': '1.5px rgb(183,21,53) solid',
    }, {
    
       'if': {'column_id': ['Player']},
        'borderRight': '1.5px rgb(183,21,53) solid',
    },{
    
       'if': {'column_id': ['PPG']},
        'fontWeight': 'bold',
    }],
    


),


html.Div(
dcc.Dropdown(
    id="player-filter",
    options=[
        {'label': 'TK', 'value': 'TK'},
        {'label': 'AK', 'value': 'AK'},
        {'label': 'GB', 'value': 'GB'},
        {'label': 'BS', 'value': 'BS'},
        {'label': 'FC', 'value': 'FC'},
        {'label': 'OB', 'value': 'OB'},
        {'label': 'JK', 'value': 'JK'},
        {'label': 'PB', 'value': 'PB'},
        {'label': 'AB', 'value': 'AB'}
    ],
    value=[],
    multi=True,
    style=
                                    { 'width': '280px',
                                      'color': '#212121',
                                    #   'background-color': '#212121',
                                      'fontFamily': 'Courier New',
                                      'fontSize': 14
                                    },
                                        
),className="custom-dropdown", style = {'display': 'inline-block', 'verticalAlign' : "middle"},

), 

html.Div([
    # html.Div(dcc.Input(id='input-on-submit', type='text')),
    html.Button('Update', id='update-button', n_clicks=0, style={'fontFamily': 'Courier New',  }),

    # html.Div(id='output-container-button',
    #          children='Enter a value and press submit')
], style = {'display': 'inline-block', 'verticalAlign' : "middle"},),

html.P(["GPt, GP3, GP4 mean Games Played (total, 3-player and 4-player, respectively).", html.Br(), 
        "PTt, PT3, PT4 mean Points (total, 3-player and 4-player, respectively).", html.Br(),
        "ASt, AS3, AS4 mean Average score per game (total, 3-player and 4-player, respectively).", html.Br(),
        "Wt, W3, W4 mean number of Wins (total, 3-player and 4-player, respectively).", html.Br(),
        "Lt, L3, L4 mean number of Losses (total, 3-player and 4-player, respectively).", html.Br(),
        "S3, S4 mean number of Second place finishes (3-player and 4-player, respectively).", html.Br(),
        "T4 means number of Third place finishes (4-player).", html.Br(),
        "BP3, BP4 mean Bonus Points won (3-player and 4-player, respectively).", html.Br(),
        "SM3, SM4 mean number of successful Shoot the Moon (3-player and 4-player, respectively)."

        
], style={'fontFamily': 'Courier New', 'fontSize': 10}),

html.P(["4-player points are awarded; 1st place: 3, 2nd place: 1, 3rd place: 0, 4th place: -2, and a bonus point for finishing below 20." , html.Br(),
        "3-player points are awarded; 1st place: 2, 2nd place: 0, 3rd place: -1, and a bonus point for finishing below 10.", html.Br(),
        "In the event of a tie in scores in a game, both players are awarded points for the lower position (e.g. two people tied for first place, both get points for second place).", html.Br(),
        "Ordering on the table is done by PPG (and at least five games have to have been played).", html.Br(),
        "In the case of ties on the table, tie breakers are: (1) Lowest Average Score, (2) highest PT4, (3) lowest AS4, (4) highest PT3, (5) lowest AS3, (6) highest Gpt.",
        html.Br(),html.Br(),
        "AK is known for sweaty plays and constantly fishing."

        
], style={'fontFamily': 'Courier New', 'fontSize': 10, 'whiteSpace': 'pre-wrap'}),


    # html.Div(children='''

    #     ASt, AS3, AS4 mean Average score per game (total, 3person and 4person, respectively).
    #     Wt, W3, W4 mean number of Wins (total, 3person and 4person, respectively).
    #     Lt, L3, L4 mean number of Losses (total, 3person and 4person, respectively).
    #     S3, S4 mean number of Second place finishes (3person and 4person, respectively).
    #     T4 means number of Third place finishes (4person).
    #     BP3, BP4 mean Bonus Points won (3person and 4person, respectively).
    #     SM3, SM4 mean number of successful Shoot the Moon (3person and 4person, respectively).

    # '''),



# html.A(html.Button('Refresh Page'),href='/'),

   html.Hr(style={'border-top': '5px solid rgb(183,21,53)'}),

   html.H1(children='December Championship - Scores and Graph', style={'color': 'black', 'fontSize': 28, 'fontFamily': 'Courier New'} ),

html.Div([
    # html.Div(dcc.Input(id='input-on-submit', type='text')),
    html.Button('Update scores', id='updatescores-button', n_clicks=0, style={'fontFamily': 'Courier New', 'color' : 'rgba(0,0,0,0)', 'background-color': 'rgba(0,0,0,0)', 'border': '0px solid LightGray'   }),

    # html.Div(id='output-container-button',
    #          children='Enter a value and press submit')
], style = {},),

html.Div(
    dash_table.DataTable(
        id='score-table',
        columns=[{'name':'Game', 'id': "Game"},{'name':'Scores', 'id': "Scores"} ], #[x.split('.')[0] for x in list(scoredict)],
        data=sd_data,
        fixed_rows={'headers': True},

        style_header={'fontWeight': 'bold'},

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
                {'x': [1.5, 1.45, 1.32, 1.2, 1.08, 1.2, 1.4, 1.5, 1.6, 1.8, 1.92, 1.8, 1.68, 1.55, 1.5], 
                'y': [45, 60, 70, 65, 50, 30, 15, 10, 15, 30, 50, 65, 70, 60, 45], 
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

    
])

previous_value = 0

@app.callback(
    [Output("league-table", "data"), Output("updatescores-button", "style")],
    [Input('update-button', 'n_clicks'), Input('player-filter', 'value')])
def update_leaguetable(n_clicks, value):
        # Don't run unless the button has been pressed...
    if not n_clicks:
        raise PreventUpdate
    
    # print(str(value))
    if len(value) > 0:
        script_path = 'python3 code/exampleHearts.py' + " " + ' '.join(value)  
    else:
        script_path = 'python3 code/exampleHearts.py'
    # The output of a script is always done through a file dump.
    # Let's just say this call dumps some data into an `output_file`
    call(script_path, shell = True) # this updates the finalstats.txt

    # Load your output file with "some code"
    output_content = pd.read_csv('data/finalstats.txt')
    # dfcols=[{"name": i, "id": i} for i in df.columns]
    # hdrzt=[]
    # hdrz3=[]
    # hdrz4=[]
    # for i in dfcols:
    #     if i['name'] == "Unnamed: 0":
    #         i['name'] = ["","Player"]
    #     elif i['name'].endswith('3'):
    #         hdrz3.append(i['name'])
    #         i['name'] = ['3-player', i['name']]
    #     elif i['name'].endswith('4'):
    #         hdrz4.append(i['name'])
    #         i['name'] = ['4-player', i['name']]
    #     else:
    #         hdrzt.append(i['name'])
    #         i['name'] = ['Total', i['name']]

    print(value)


    return output_content.to_dict("records"), {'fontFamily': 'Courier New',}


@app.callback(
    [Output("score-table", "data")],
    [Input('updatescores-button', 'n_clicks')])
def update_scoretable(n_clicks):
        # Don't run unless the button has been pressed...
    if not n_clicks:
        raise PreventUpdate
    print("updating scores")
    thedict = np.load("data/scoretable.npy",allow_pickle='TRUE').item()
    thedict = dict( sorted(thedict.items(), key=lambda x: x[0].lower(), reverse = True) ) # sorting it so latest are at top (YYYY-MM-DDX.csv)
                                                                                          # X is letter if there are multiple on that day, first one does not have a letter.
    thedict_data = []
    
    for k in thedict:
        # thedict_data.append()
        sfd=[] #string for data  
        for i, name in enumerate(thedict[k]['Players']):
            sfd.append(name)
            sfd.append(str(thedict[k]['Scores'][0][i]))
            if i + 1 < len(thedict[k]['Players']):
                sfd.append(' | ')
    
        thedict_data.append({'Game': k.split('.')[0], 'Scores': ' '.join(sfd)})
        # print(thedict_data)

    return [thedict_data]




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
        # print(fig)
        return fig #active cell looks like this: {'row': 4, 'column': 1, 'column_id': 'Scores'} 



if __name__ == '__main__':
    app.run_server(debug=True)

# to make tabs
    

#  list2 =   ['GB', 'TK', 'BS']

#  list1 =    ['GB']
#  list1 =    ['AK']
#  list1 =    ['AK', 'GB']
#  list1 =    ['GB', 'TK']



#  all(item in list2 for item in list1)

# pip3 install heroku3