import dash
import dash_core_components as dcc
import dash_html_components as html
import yaml

with open('config.yaml') as file:
    config = yaml.safe_load(file.read())

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

layout = html.Div([
    html.Div([
        dcc.Link('企業名で検索', href='/company'),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H1(children='給与帯 分布図'),

        html.Div(id='display-data-counts'),
        html.Div(id='display-filter'),

        html.Div([
            dcc.Graph(
                id='salary-graph-all',
            ),
        ], style={'display': 'inline-block', 'width': '30%'}),
        html.Div([
            dcc.Graph(
                id='salary-graph',
            ),
        ], style={'display': 'inline-block', 'width': '70%'}),
    ]),

    dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")],
                type="graph"),

    html.Div([
        html.Div([
            dcc.Graph(
                id='pie-chart',
            ),
        ], style={'display': 'inline-block', 'width': '100%'}),
    ]),

    html.Div(className='row', children=[
        html.H5(children='業種の選択'),
        html.Div([
            html.Label('企業の業種（大）'),
            dcc.Dropdown(
                id='dropdown-big-industries',
                options=[{'label': i, 'value': i} for i in config['industries'].keys()],
                value='IT/Web・通信・インターネット系',
            ),
        ], style={'display': 'inline-block', 'width': '49%', 'margin-right': '1%'}),
        html.Div([
            html.Label('企業の業種（小）'),
            dcc.Dropdown(id='dropdown-small-industries'),
        ], style={'display': 'inline-block', 'width': '49%'})
    ], style={'margin-bottom': '20px'}),

    html.Div(className='row', children=[
        html.H5(children='職種の選択'),
        html.Div([
            html.Label('職種（大）'),
            dcc.Dropdown(
                id='dropdown-big-occupations',
                options=[{'label': i, 'value': i} for i in config['occupations'].keys()],
                value='エンジニア・技術職（システム/ネットワーク）'
            ),
        ], style={'display': 'inline-block', 'width': '49%', 'margin-right': '1%'}),
        html.Div([
            html.Label('職種（小）'),
            dcc.Dropdown(id='dropdown-small-occupations'),
        ], style={'display': 'inline-block', 'width': '49%'}),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.H5(children='技術・言語の選択'),
        html.Label('技術・言語'),
        dcc.Dropdown(
            id='technics',
            options=[{'label': i, 'value': i} for i in config['technics']],
            value=[],
            multi=True
        ),
    ], style={'display': 'inline-block', 'width': '70%', 'margin-bottom': '20px'}),
    html.Div([
        html.Button(id='submit-button', n_clicks=0, children='Submit')
    ]),
], style={'margin': '3%'})
