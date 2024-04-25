from dash import Dash, html, dcc, callback, Output, Input
import dash_draggable
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)

style_dashboard = {
    "height": '100%',
    "width": '100%',
    "display": "flex",
    "flex-grow": "0",
    "flex-direction": "column"
}

style_controls = {
    "display": "grid",
    "grid-template-columns": "auto 1fr",
    "align-items": "center",
    "gap": "1rem"
}

def create_measurement_year_figure(countries, measure="pop"):
    linechart_countries = df[df.country.isin(countries)]
    return px.line(linechart_countries, color="country", x="year", y=measure, title="Линейный график по годам")


def create_line_graph(countries):
    return html.Div([
        html.Table([
            html.Tr([
                html.Td([
                    html.Span("Выбранные страны")
                ], style={"white-space": "nowrap"}),
                html.Td([
                    dcc.Dropdown(df.country.unique(), countries, multi=True, id='dropdown-active-countries'),
                ], style={"width": "100%"}),
            ]),
            html.Tr([
                html.Td([
                    html.Span("Мера по оси y")
                ]),
                html.Td([
                    dcc.Dropdown(["lifeExp", "pop", "gdpPercap"], id='dropdown-measure', clearable=False, value="pop")
                ]),
            ])
        ], style={"margin": "0rem 1rem"}),
        dcc.Graph(id='meas-vs-year', figure=create_measurement_year_figure(countries),
                  style=style_dashboard, responsive=True)
    ], style=style_dashboard, id="meas-vs-year-dash")



def create_bubble_fig(x="gdpPercap", y="lifeExp", size="pop", year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values(["continent", "year"], ascending=False).drop_duplicates("country")

    if size == "lifeExp":
        size = latest_data.lifeExp
        size = size / size.max()
        size = size ** 6

    return px.scatter(latest_data, x=x, y=y, size=size, color="continent", hover_name="country", size_max=60,
                      hover_data=["year"], title="Пузырьковая диаграмма")


def create_buble_dash():
    return html.Div([
        html.Table([
            html.Tr([
                html.Td([
                    html.Span("Ось X")
                ], style={"white-space": "nowrap"}),
                html.Td([
                    dcc.Dropdown(["lifeExp", "pop", "gdpPercap"], value="pop", id='bubble-x', clearable=False)
                ], style={"width": "100%"})
            ]),
            html.Tr([
                html.Td([
                    html.Span("Ось Y")
                ]),
                html.Td([
                    dcc.Dropdown(["lifeExp", "pop", "gdpPercap"], value="lifeExp", id='bubble-y', clearable=False),
                ])
            ]),
            html.Tr([
                html.Td([
                    html.Span("Размер")
                ]),
                html.Td([
                    dcc.Dropdown(["lifeExp", "pop", "gdpPercap"], "pop", id='bubble-size', clearable=False),
                ])
            ]),
        ], style={"margin": "0rem 1rem"}),
        dcc.Graph(id='bubble', figure=create_bubble_fig(), style=style_dashboard, responsive=True)
    ], style=style_dashboard, id="bubble-dash")


def create_top_pop_fig(year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values("year", ascending=False).drop_duplicates("country")
    top = latest_data.sort_values("pop", ascending=False)[:15][::-1]

    return px.bar(top, x="pop", y="country", title="Топ 15 стран по популяции", hover_data=["year"])


def create_top_pop_dash():
    return html.Div([
        dcc.Graph(id='top-pop', figure=create_top_pop_fig(), style=style_dashboard, responsive=True)
    ], style=style_dashboard, id="top-pop-dash")


def create_pop_pie_fig(year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values("year", ascending=False).drop_duplicates("country")

    return px.pie(latest_data, values="pop", names="continent", title="Популяции на континентах", hole=.3)


def create_pop_pie_dash():
    return html.Div([
        dcc.Graph(id='pop-pie', figure=create_pop_pie_fig(), style=style_dashboard, responsive=True)
    ], style=style_dashboard, id="pop-pie-dash")


def create_dash(dash, dash1, dash2, dash3):
    return  html.Div([
        html.H1(children='Сравнение стран', style={'textAlign': 'center'}),
        dash_draggable.ResponsiveGridLayout([
            dash, dash1,
            dash2, dash3
        ], clearSavedLayout=True, layouts={
            "lg": [
                {
                    "i": "meas-vs-year-dash",
                    "x": 0, "y": 0, "w": 8, "h": 14
                },
                {
                    "i": "pop-pie-dash",
                    "x": 8, "y": 0, "w": 4, "h": 14
                },
                {
                    "i": "top-pop-dash",
                    "x": 8, "y": 14, "w": 4, "h": 14
                },
                {
                    "i": "bubble-dash",
                    "x": 0, "y": 14, "w": 8, "h": 14
                }
            ]
        })
    ])


@callback(
    Output('meas-vs-year', 'figure'),
    Input('dropdown-active-countries', 'value'),
    Input('dropdown-measure', 'value')
)
def update_meas_vs_year_dash(active_countries, measure):
    return create_measurement_year_figure(active_countries, measure)


def extract_from_to(arg):
    year_from = None
    year_to = None
    if arg:
        if 'xaxis.range[0]' in arg:
            year_from = arg['xaxis.range[0]']
        if 'xaxis.range[1]' in arg:
            year_to = arg['xaxis.range[1]']

    return year_from, year_to


@callback(
    Output('bubble', 'figure'),
    Input('bubble-x', 'value'),
    Input('bubble-y', 'value'),
    Input('bubble-size', 'value'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_bubble_dash(x, y, size, meas_vs_year_zoom):
    return create_bubble_fig(x, y, size, *extract_from_to(meas_vs_year_zoom))


@callback(
    Output('top-pop', 'figure'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_top_pop_dash(meas_vs_year_zoom):
    return create_top_pop_fig(*extract_from_to(meas_vs_year_zoom))


@callback(
    Output('pop-pie', 'figure'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_pop_pie_dash(meas_vs_year_zoom):
    return create_pop_pie_fig(*extract_from_to(meas_vs_year_zoom))


countries = ["Russia", "China", "United States"]
meas_vs_year_dash = create_line_graph(countries)
bubble_dash = create_buble_dash()
top_pop_dash = create_top_pop_dash()
pop_pie_dash = create_pop_pie_dash()

app.layout = create_dash(meas_vs_year_dash, pop_pie_dash,
                         bubble_dash, top_pop_dash)


app = app.server
#
# if __name__ == '__main__':
#     app.run()
