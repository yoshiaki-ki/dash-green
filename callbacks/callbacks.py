import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_table
from apps.app_filter import *

from app import app


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


''' 

フィルタ検索ページのcallback

'''


def gen_filtered_min_df(big_occupations, small_occupations, big_industries, small_industries, technics):
    df_min_salary = pd.read_csv("./data/min_salary.csv")

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

    return df_min_salary[np.all(min_filter_list, axis=0)]


def gen_filtered_max_df(big_occupations, small_occupations, big_industries, small_industries, technics):
    df_max_salary = pd.read_csv("./data/max_salary.csv")

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

    return df_max_salary[np.all(max_filter_list, axis=0)]


@app.callback(
    Output(component_id='display-filter', component_property='children'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State('dropdown-big-occupations', 'value'),
     State('dropdown-small-occupations', 'value'),
     State('dropdown-big-industries', 'value'),
     State('dropdown-small-industries', 'value'),
     State('technics', 'value')
     ]
)
def display_filter(n_clicks, big_occupations, small_occupations, big_industries, small_industries, technics):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        techs = ",".join(technics)

        return html.Div([
            html.H3(children='検索条件'),
            html.Table(
                # Header
                [html.Tr([html.Th(col) for col in ["業種(大)", "業種(小)", "職種(大)", "職種(小)", "技術・言語"]])] +

                # Body
                [html.Tr([html.Td(col) for col in
                          [big_occupations, small_occupations, big_industries, small_industries, techs]])]
            )
        ])


@app.callback(
    Output(component_id='display-data-counts', component_property='children'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State('dropdown-big-occupations', 'value'),
     State('dropdown-small-occupations', 'value'),
     State('dropdown-big-industries', 'value'),
     State('dropdown-small-industries', 'value'),
     State('technics', 'value')
     ]
)
def display_data_counts(n_clicks, big_occupations, small_occupations, big_industries, small_industries, technics):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        filterd_min_df = gen_filtered_min_df(big_occupations, small_occupations, big_industries, small_industries,
                                             technics)
        filterd_max_df = gen_filtered_max_df(big_occupations, small_occupations, big_industries, small_industries,
                                             technics)

        data_count = "求人数：" + str(max(len(filterd_min_df), len(filterd_max_df))) + " 個"

        return html.H3(children=data_count)


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
        fig = go.Figure()

        filted_min_df = gen_filtered_min_df(big_occupations, small_occupations, big_industries, small_industries,
                                            technics)
        filted_max_df = gen_filtered_max_df(big_occupations, small_occupations, big_industries, small_industries,
                                            technics)

        # グラフ描画
        fig.add_trace(go.Violin(x=filted_min_df["IPO"],
                                y=filted_min_df['min_salary'],
                                legendgroup='min', scalegroup='min', name='各最低給与の分布',
                                line_color='blue')
                      )

        fig.add_trace(
            go.Violin(x=filted_max_df["IPO"],
                      y=filted_max_df['max_salary'],
                      legendgroup='max', scalegroup='max', name='各最大給与の分布',
                      line_color='orange')
        )

        fig.update_traces(meanline_visible=True, jitter=0.05)
        fig.update_layout(violingap=0, violinmode='group')

        return fig


@app.callback(
    Output('salary-graph-all', 'figure'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State('dropdown-big-occupations', 'value'),
     State('dropdown-small-occupations', 'value'),
     State('dropdown-big-industries', 'value'),
     State('dropdown-small-industries', 'value'),
     State('technics', 'value')
     ]
)
def update_graph_all(n_clicks, big_occupations, small_occupations, big_industries, small_industries, technics):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        fig = go.Figure()

        filted_min_df = gen_filtered_min_df(big_occupations, small_occupations, big_industries, small_industries,
                                            technics)
        filted_max_df = gen_filtered_max_df(big_occupations, small_occupations, big_industries, small_industries,
                                            technics)

        # グラフ描画
        ## 全体のmax, minを出力
        fig.add_trace(go.Violin(y=filted_min_df['min_salary'],
                                legendgroup='min', scalegroup='min', name='全体の最低給与',
                                line_color='lightseagreen', x0='全体'))

        fig.add_trace(go.Violin(y=filted_max_df['max_salary'],
                                legendgroup='max', scalegroup='max', name='全体の最大給与',
                                line_color='mediumpurple', x0='全体')
                      )

        fig.update_traces(meanline_visible=True, jitter=0.05)
        fig.update_layout(violingap=0, violinmode='group')

        return fig


# パイチャートの作成
@app.callback(
    Output('pie-chart', 'figure'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State('dropdown-big-occupations', 'value'),
     State('dropdown-small-occupations', 'value'),
     State('dropdown-big-industries', 'value'),
     State('dropdown-small-industries', 'value'),
     State('technics', 'value')
     ]
)
def update_pie_chart(n_clicks, big_occupations, small_occupations, big_industries, small_industries, technics):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        filterd_min_df = gen_filtered_min_df(big_occupations, small_occupations, big_industries, small_industries,
                                             technics)
        filterd_max_df = gen_filtered_max_df(big_occupations, small_occupations, big_industries, small_industries,
                                             technics)

        labels = ["0~300万", "300~349万円", "350~399万円", "400~449万円", "450~499万円", "500~549万円", "550~599万円", "600~649万円",
                  "650~699万円", "700~749万円", "750~799万円", "800~849万円", "850~899万円", "900~949万円", "950~999万円",
                  "1000~1099万円", "1100~1199万円", "1200~1299万円", "1300~万円"]

        values_min = [(filterd_min_df['min_salary'] < 300).sum(),
                      ((filterd_min_df['min_salary'] >= 300) & (filterd_min_df['min_salary'] < 350)).sum(),
                      ((filterd_min_df['min_salary'] >= 350) & (filterd_min_df['min_salary'] < 400)).sum(),
                      ((filterd_min_df['min_salary'] >= 450) & (filterd_min_df['min_salary'] < 500)).sum(),
                      ((filterd_min_df['min_salary'] >= 500) & (filterd_min_df['min_salary'] < 550)).sum(),
                      ((filterd_min_df['min_salary'] >= 550) & (filterd_min_df['min_salary'] < 600)).sum(),
                      ((filterd_min_df['min_salary'] >= 600) & (filterd_min_df['min_salary'] < 650)).sum(),
                      ((filterd_min_df['min_salary'] >= 650) & (filterd_min_df['min_salary'] < 700)).sum(),
                      ((filterd_min_df['min_salary'] >= 750) & (filterd_min_df['min_salary'] < 800)).sum(),
                      ((filterd_min_df['min_salary'] >= 800) & (filterd_min_df['min_salary'] < 850)).sum(),
                      ((filterd_min_df['min_salary'] >= 850) & (filterd_min_df['min_salary'] < 900)).sum(),
                      ((filterd_min_df['min_salary'] >= 900) & (filterd_min_df['min_salary'] < 950)).sum(),
                      ((filterd_min_df['min_salary'] >= 950) & (filterd_min_df['min_salary'] < 1000)).sum(),
                      ((filterd_min_df['min_salary'] >= 1000) & (filterd_min_df['min_salary'] < 1100)).sum(),
                      ((filterd_min_df['min_salary'] >= 1200) & (filterd_min_df['min_salary'] < 1300)).sum(),
                      (filterd_min_df['min_salary'] >= 1300).sum()
                      ]
        values_max = [(filterd_max_df['max_salary'] < 300).sum(),
                      ((filterd_max_df['max_salary'] >= 300) & (filterd_max_df['max_salary'] < 350)).sum(),
                      ((filterd_max_df['max_salary'] >= 350) & (filterd_max_df['max_salary'] < 400)).sum(),
                      ((filterd_max_df['max_salary'] >= 450) & (filterd_max_df['max_salary'] < 500)).sum(),
                      ((filterd_max_df['max_salary'] >= 500) & (filterd_max_df['max_salary'] < 550)).sum(),
                      ((filterd_max_df['max_salary'] >= 550) & (filterd_max_df['max_salary'] < 600)).sum(),
                      ((filterd_max_df['max_salary'] >= 600) & (filterd_max_df['max_salary'] < 650)).sum(),
                      ((filterd_max_df['max_salary'] >= 650) & (filterd_max_df['max_salary'] < 700)).sum(),
                      ((filterd_max_df['max_salary'] >= 750) & (filterd_max_df['max_salary'] < 800)).sum(),
                      ((filterd_max_df['max_salary'] >= 800) & (filterd_max_df['max_salary'] < 850)).sum(),
                      ((filterd_max_df['max_salary'] >= 850) & (filterd_max_df['max_salary'] < 900)).sum(),
                      ((filterd_max_df['max_salary'] >= 900) & (filterd_max_df['max_salary'] < 950)).sum(),
                      ((filterd_max_df['max_salary'] >= 950) & (filterd_max_df['max_salary'] < 1000)).sum(),
                      ((filterd_max_df['max_salary'] >= 1000) & (filterd_max_df['max_salary'] < 1100)).sum(),
                      ((filterd_max_df['max_salary'] >= 1200) & (filterd_max_df['max_salary'] < 1300)).sum(),
                      (filterd_max_df['max_salary'] >= 1300).sum()
                      ]

        # Create subplots: use 'domain' type for Pie subplot
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=['最小給与', '最大給与'])
        fig.add_trace(go.Pie(labels=labels, values=values_min, name="最小給与", sort=False, direction='clockwise',
                             textposition='inside'),
                      1, 1)
        fig.add_trace(go.Pie(labels=labels, values=values_max, name="最大給与", sort=False, direction='clockwise',
                             textposition='inside'),
                      1, 2)

        # Use `hole` to create a donut-like pie chart
        fig.update_traces(hole=.4, hoverinfo="label+value+percent")

        fig.update_layout(
            title_text="全体の最小・最大給与帯割合")

        return fig


@app.callback(Output("loading-output-1", "children"),
              [Input(component_id='submit-button', component_property='n_clicks')])
def input_triggers_spinner(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        time.sleep(3)


@app.callback(Output("loading-output-2", "children"),
              [Input(component_id='submit-button', component_property='n_clicks')])
def input_triggers_spinner(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        time.sleep(1)


''' 

企業名検索ページのcallback

'''
df = pd.read_csv("./data/company_jobs_merged.csv")


# dataframeをテーブルに
def generate_table(dataframe, max_rows=10):
    columns = ["company", "job_tag", "job_url", "max_salary", "min_salary"]

    return dash_table.DataTable(
        data=dataframe.to_dict('records'),
        columns=[
            {'name': i, 'id': i} for i in columns
        ],
        fixed_rows={'headers': True, 'data': 0},
        style_header={
            'backgroundColor': '#def9ff',
            'fontWeight': 'bold'
        },
        style_cell={
            'whiteSpace': 'normal',
            'textAlign': 'left'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'company'},
             'width': '25%'},
            {'if': {'column_id': 'job_tag'},
             'width': '25%'},
            {'if': {'column_id': 'max_salary'},
             'width': '10%'},
            {'if': {'column_id': 'min_salary'},
             'width': '10%'},
        ],
        virtualization=True,
        page_action='none',
        filter_action="native",
    )


# 企業別の平均給与を表示
@app.callback(
    Output('mean-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('company-name', 'value'), ]
)
def generate_mean_graph(n_clicks, input_value):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        try:
            selected_companies = input_value
            dfs = []
            for company in selected_companies:
                selected_df = df[df["company"] == company]
                dfs.append(selected_df)
            merged_dfs = pd.concat(dfs)

            # 企業ごとの平均を算出
            grouped_dfs = merged_dfs.groupby("company").mean()
            mean_dfs = grouped_dfs.loc[:, ["max_salary", "min_salary"]]

            # グラフの描画
            fig = go.Figure(data=[
                go.Bar(name='最低給与', x=mean_dfs.index, y=mean_dfs["min_salary"]),
                go.Bar(name='最大給与', x=mean_dfs.index, y=mean_dfs["max_salary"])
            ])
            fig.update_layout(barmode='group', title_text='企業ごとの平均給与')

            return fig

        except:
            return go.Figure()


# 選択した企業をマージした平均給与を表示
@app.callback(
    Output('all-mean-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('company-name', 'value'), ]
)
def generate_all_mean_graph(n_clicks, input_value):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        try:
            selected_companies = input_value
            dfs = []
            for company in selected_companies:
                selected_df = df[df["company"] == company]
                dfs.append(selected_df)
            merged_dfs = pd.concat(dfs)

            # グラフの描画
            fig = go.Figure(data=[
                go.Bar(name='最低給与', x=["全体", ], y=[merged_dfs.mean()["min_salary"], ],
                       marker=dict(color=['#0032CB', ])),
                go.Bar(name='最大給与', x=["全体", ], y=[merged_dfs.mean()["max_salary"], ],
                       marker=dict(color=['#CB0000', ])),
            ])
            fig.update_layout(barmode='group', title_text='選択した企業の平均給与')

            return fig

        except:
            return go.Figure()


@app.callback(
    Output(component_id='data-table', component_property='children'),
    [Input('submit-button', 'n_clicks')],
    [State('company-name', 'value'), ]
)
def update_output_div(n_clicks, input_value):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        try:
            selected_companies = input_value
            dfs = []
            for company in selected_companies:
                selected_df = df[df["company"] == company]
                dfs.append(selected_df)

            merged_dfs = pd.concat(dfs)

            return generate_table(merged_dfs)
        except:
            return html.H5(children='企業名を入力してください。')
