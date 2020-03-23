import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import yaml

with open('config.yaml') as file:
    config = yaml.safe_load(file.read())

df = pd.read_csv("./data/company_jobs_merged.csv")

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    },
    'card': {
        'padding': '0.5em 1em',
        'margin': '2em 0',
        'background': 'white',
        'color': '#5d627b',
        'border-top': 'solid 5px #5d627b',
        'box-shadow': '0 3px 5px rgba(0, 0, 0, 0.22)'
    }
}

layout = html.Div([
    html.Div([
        dcc.Link('各条件で検索', href='/'),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H1(children='企業別 求人'),

        html.Div(className='row', children=[
            html.Div([
                html.Label('企業名'),
                dcc.Dropdown(
                    id='company-name',
                    options=[{'label': i, 'value': i} for i in df["company"].unique()],
                    value=[],
                    multi=True
                ),
            ], style={'margin-bottom': '20px'}),

            html.Button(id='submit-button', n_clicks=0, children='Submit'),
        ]),
        dcc.Loading(id="loading-2", children=[html.Div(id="loading-output-2")],
                    type="graph"),

        html.Div(className='row', children=[
            html.Div([
                dcc.Graph(
                    id='all-mean-graph',
                ),
            ], style={'display': 'inline-block', 'width': '30%'}),
            html.Div([
                dcc.Graph(
                    id='mean-graph',
                ),
            ], style={'display': 'inline-block', 'width': '70%'}),
        ]),

        html.Div(id='data-table'),

    ])
], style={'margin': '3%'})
