import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yaml

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

with open('config.yaml') as file:
    config = yaml.safe_load(file.read())

# appという箱作り①
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


app.layout = html.Div([
    dcc.Graph(
        id='salary-graph',
    ),

    html.Div(className='row', children=[
        html.Div([
            html.Label('企業の業種（大）'),
            dcc.Dropdown(
                id='dropdown-big-industries',
                options=[{'label': i, 'value': i} for i in config['industries'].keys()],
                value='IT/Web・通信・インターネット系',
            ),
        ]),
        html.Div([
            html.Label('企業の業種（小）'),
            dcc.Dropdown(id='dropdown-small-industries'),
        ]),

        html.Div([
            html.Label('職種（大）'),
            dcc.Dropdown(
                id='dropdown-big-occupations',
                options=[{'label': i, 'value': i} for i in config['occupations'].keys()],
                value='エンジニア・技術職（システム/ネットワーク）'
            ),

            html.Label('職種（小）'),
            dcc.Dropdown(id='dropdown-small-occupations'),
        ]),
        html.Div([
            html.Label('技術・言語'),
            dcc.Dropdown(
                id='technics',
                options=[{'label': i, 'value': i} for i in config['technics']],
                value=[],
                multi=True
            ),
        ]),
        html.Div([
            html.Button(id='submit-button', n_clicks=0, children='Submit')
        ]),
    ])
])

@app.callback(
    Output('dropdown-small-occupations', 'options'),
    [Input('dropdown-big-occupations', 'value')])
def set_small_occupations_options(selected_big_occupations):
    return [{'label': i, 'value': i} for i in config['occupations'][selected_big_occupations]]


@app.callback(
    Output('dropdown-small-occupations', 'value'),
    [Input('dropdown-small-occupations', 'options')])
def set_small_occupations_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('dropdown-small-industries', 'options'),
    [Input('dropdown-big-industries', 'value')])
def set_small_industries_options(selected_big_industries):
    return [{'label': i, 'value': i} for i in config['industries'][selected_big_industries]]


@app.callback(
    Output('dropdown-small-industries', 'value'),
    [Input('dropdown-small-industries', 'options')])
def set_small_industries_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('salary-graph', 'figure'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State('dropdown-big-occupations', 'value'),
     State('dropdown-small-occupations', 'value'),
     State('dropdown-big-industries', 'value'),
     State('dropdown-small-industries', 'value'),
     State('technics', 'value')
     ]
)
def update_graph(n_clicks, big_occupations, small_occupations, big_industries, small_industries, technics):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        df_min_salary = pd.read_csv("./data/min_salary.csv")
        df_max_salary = pd.read_csv("./data/max_salary.csv")

        fig = go.Figure()

        # min_salaryのフィルタ
        # 職種
        selected_big_occupations_min = np.array(df_min_salary[big_occupations] == 1)
        selected_small_occupations_min = np.array(df_min_salary[small_occupations] == 1)
        # 業種
        selected_big_industries_min = np.array(df_min_salary[big_industries] == 1)
        selected_small_industries_min = np.array(df_min_salary[small_industries] == 1)
        # 技術・言語
        selected_technics_list_min = []
        for tech in technics:
            selected_technics = np.array(df_min_salary[tech] == 1)
            selected_technics_list_min.append(selected_technics)

        min_filter_list = [selected_big_occupations_min, selected_small_occupations_min, selected_big_industries_min,
                           selected_small_industries_min]
        min_filter_list.extend(selected_technics_list_min)

        # max_salaryのフィルタ
        # 職種
        selected_big_occupations_max = np.array(df_max_salary[big_occupations] == 1)
        selected_small_occupations_max = np.array(df_max_salary[small_occupations] == 1)
        # 業種
        selected_big_industries_max = np.array(df_max_salary[big_industries] == 1)
        selected_small_industries_max = np.array(df_max_salary[small_industries] == 1)
        # 技術・言語
        selected_technics_list_max = []
        for tech in technics:
            selected_technics = np.array(df_max_salary[tech] == 1)
            selected_technics_list_max.append(selected_technics)

        max_filter_list = [selected_big_occupations_max, selected_small_occupations_max, selected_big_industries_max,
                           selected_small_industries_max]
        max_filter_list.extend(selected_technics_list_max)

        # グラフ描画
        fig.add_trace(go.Violin(x=df_min_salary[np.all(min_filter_list, axis=0)]["IPO"],
                                y=df_min_salary[np.all(min_filter_list, axis=0)]['min_salary'],
                                legendgroup='min', scalegroup='min', name='min',
                                line_color='blue')
                      )

        fig.add_trace(
            go.Violin(x=df_max_salary[np.all(max_filter_list, axis=0)]["IPO"],
                      y=df_max_salary[np.all(max_filter_list, axis=0)]['max_salary'],
                      legendgroup='max', scalegroup='max', name='max',
                      line_color='orange')
        )

        fig.update_traces(meanline_visible=True, points="all", jitter=0.05)
        fig.update_layout(violingap=0, violinmode='group')

        return fig


# 実行用③
if __name__ == '__main__':
    app.run_server(debug=True)
