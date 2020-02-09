import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yaml

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app

with open('config.yaml') as file:
    config = yaml.safe_load(file.read())

df = pd.read_csv("./data/company_jobs_merged.csv")

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


# dataframeをテーブルに
def generate_table(dataframe, max_rows=10):
    columns = ["company", "job_tag", "job_title", "job_url", "max_salary", "min_salary"]
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


layout = html.Div([
    html.Div(className='container', children=[
        dcc.Link('職種・業種で検索', href='/apps/filter'),

        html.Div(className='row', children=[
            html.Div([
                html.Label('企業名'),
                dcc.Dropdown(
                    id='company-name',
                    options=[{'label': i, 'value': i} for i in df["company"].unique()],
                    value=[],
                    multi=True
                ),
            ]),

            html.Button(id='submit-button', n_clicks=0, children='Submit'),
        ]),

        html.Div(id='data-table')
    ])
])


@app.callback(
    Output(component_id='data-table', component_property='children'),
    [Input('submit-button', 'n_clicks')],
    [State('company-name', 'value'), ]
)
def update_output_div(n_clicks, input_value):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        selected_companies = input_value
        dfs = []
        for company in selected_companies:
            selected_df = df[df["company"] == company]
            dfs.append(selected_df)

        merged_dfs = pd.concat(dfs)

        return generate_table(merged_dfs)
