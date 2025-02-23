import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app_company, app_filter
from callbacks import callbacks


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return app_filter.layout
    elif pathname == '/company':
        return app_company.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)