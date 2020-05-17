# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_table

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

start_year = 2000
# df_apple = pd.read_csv(DATA_PATH.joinpath("df_apple.csv"), low_memory=False, index_col=0)
# df_google = pd.read_csv(DATA_PATH.joinpath("df_google.csv"), low_memory=False, index_col=0)
# TODO button to select
df_game = pd.read_csv(DATA_PATH.joinpath("df_mobile_games.csv"), low_memory=False, index_col=0)
df_game.loc[:, "Release date"] = pd.to_datetime(df_game["Release date"])
df_game = df_game[df_game["Release date"] > dt.datetime(start_year, 1, 1)]
df_game.loc[:, 'Release year'] = df_game['Release date'].map(lambda x: x.year)
end_year = max(df_game['Release year']) + 2

df_genre_index = pd.read_csv(DATA_PATH.joinpath("games_genre2.csv"), low_memory=False)
genres_dat = pickle.load(open(DATA_PATH.joinpath('genres.dat'), 'rb'))
genres_options = [{'label': genre, 'value': genre}  for genre in genres_dat]
companies_dat = pickle.load(open(DATA_PATH.joinpath('companies.dat'), 'rb'))
companies_options = [{'label': company, 'value': company}  for company in companies_dat]

columns_table = ['Game', 'Number of Vote', 'Mean Note', 'Release year']

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                # html.Div(
                #     [
                #         html.Img(
                #             src=app.get_asset_url("dash-logo.png"),
                #             id="plotly-image",
                #             style={
                #                 "height": "60px",
                #                 "width": "auto",
                #                 "margin-bottom": "25px",
                #             },
                #         )
                #     ],
                #     className="one-third column",
                # ),
                html.Div(
                    [
                        html.H5("Operating System:", className="control_label"),
                        dcc.RadioItems(
                            options=[
                                {'label': 'Android', 'value': 'google'},
                                {'label': 'iOS', 'value': 'apple'},
                                {'label': 'Both', 'value': 'both'},
                            ],
                            value='both',
                            id='stores_selected'
                        )  
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Mobile Game Market Dashboard",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Evolution Overview", style={"margin-top": "0px"}
                                ),
                            ],
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                
            ],
            className="row flex-display",
            style={"text-align": "center"}
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by release date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=start_year,
                            max=end_year,
                            value=[2010, 2015],
                            className="dcc_control",
                        ),
                        html.P("Genres:", className="control_label"),
                        dcc.RadioItems(
                            id="well_status_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_statuses",
                            options=genres_options,
                            multi=True,
                            value=genres_dat,
                            className="dcc_control",
                        ),
                        html.P("Big Companies:", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="custom",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_types",
                            options=companies_options,
                            multi=True,
                            value=companies_dat,
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("Games")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Votes")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Mean Note")],
                                    id="oil",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [
                        html.H3(
                            children='Data table',
                            style={'textAlign': 'center'}
                        ),
                        dash_table.DataTable(
                            id='data_table',
                            columns=[{'name': i, 'id': i} for i in columns_table],
                            style_table={'height': '350px', 'overflowY': 'auto'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                        )
                    ],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [

            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def filter_dataframe(df, genres, companies, year_slider, stores, df_genre_index=df_genre_index):
    index_genre = list(
        df_genre_index[
            df_genre_index['Genre'].isin(genres)
        ]['index genre']
    )
    dff = df[
        df.index.isin(index_genre)
        & (df["Release date"] > dt.datetime(year_slider[0], 1, 1))
        & (df["Release date"] < dt.datetime(year_slider[1], 1, 1))
    ]
    if companies != []:
        dff = dff[dff["Company"].isin(companies)]

    if stores=='both':
        dff.loc[:, 'index'] = dff.index
        dff.loc[:, 'Mean Note weighted'] = pd.Series.multiply(dff['Mean Note'], dff['Number of Vote'])
        col_gb = ['Game', 'Release date', 'Genres', 'Release year','index']
        col_calc = ['Mean Note weighted', 'Number of Vote']
        dff_gb = dff[col_gb + col_calc].groupby(col_gb)[col_calc].sum().reset_index()
        dff_gb.loc[:, 'Mean Note'] = pd.Series.divide(dff_gb['Mean Note weighted'], dff_gb['Number of Vote'])\
            .apply(lambda x: round(x,2))
        dff = dff_gb.set_index('index')
    else:
        dff = dff[dff['store'] == stores]
    return dff[['Game', 'Release date', 'Release year','Genres', 'Number of Vote', 'Mean Note']]

def produce_aggregate(df_selected, year_slider):
    index = list(range(max(year_slider[0], 1985), end_year))
    df_selected_year = df_selected[
        (df_selected['Release year']>= index[0]) & (df_selected['Release year']<= index[-1])
    ]
    df_selected_year.loc[:, 'number of games'] = 1
    df_selected_year.loc[:, 'Mean Note weighted'] = df_selected_year['Number of Vote'] * df_selected_year['Mean Note']
    df_groupby = df_selected_year.groupby('Release year')[['Number of Vote', 'Mean Note weighted', 'number of games']]\
        .sum().reset_index().sort_values('Release year')
    return index,\
        list(df_groupby['number of games']),\
            list(df_groupby['Number of Vote']),\
                list(df_groupby['Mean Note weighted'])


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)
@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("stores_selected", "value"),
    ],
)
def update_production_text2(genres, companies, year_slider, stores):
    dff = filter_dataframe(df_game, genres, companies, year_slider, stores)
    if dff.shape[0] == 0:
        return 0, 0, 0
    else: 
        index, n_games, n_rating, mean_rating = produce_aggregate(dff, year_slider)
    return f'{sum(n_games):,}', f'{sum(n_rating):,}', f'{sum(mean_rating)/sum(n_rating):.1f}'

# Radio -> multi
@app.callback(
    Output("well_statuses", "value"), [Input("well_status_selector", "value")]
)
def display_status(selector):
    if selector == "all":
        return genres_dat
    return []


# Radio -> multi
@app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
def display_type(selector):
    if selector == "all":
        return companies_dat
    return []


# Slider -> count graph
@app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
def update_year_slider(count_graph_selected):
    if count_graph_selected is None:
        return [2010, 2015]
    
    nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
    print(count_graph_selected, nums)
    return [min(nums) + start_year, max(nums) + start_year + 1]


# Selectors -> well text
@app.callback(
    [
        Output("well_text", "children"),
        Output("gasText", "children"),
        Output("oilText", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return data[0], data[1], data[2]

# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("stores_selected", "value"),
    ]
)
def make_main_figure(genres, companies, year_slider, stores):
    dff = filter_dataframe(df_game, genres, companies, year_slider, stores)
    data = [
        dict(
            x=dff['Number of Vote'],
            y=dff['Mean Note'].map(lambda x: round(x,1)),
            text=dff['Game'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )
    ]
    layout = dict(
        xaxis={
            'title': 'Number of Vote (log scale)',
            'type': 'log'
        },
        yaxis={
            'title': 'Mean Note',
            'type': 'linear'
        },
        hovermode='closest'
    )
    layout["title"] = "Mean Note vs Number of Vote"
    layout["dragmode"] = "select"
    layout["showlegend"] = False
    layout["autosize"] = True
    figure = dict(data=data, layout=layout)
    return figure

# Selectors -> data_table
@app.callback(
    Output("data_table", "data"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("stores_selected", "value"),
    ]
)
def make_data_table(genres, companies, year_slider, stores):
    dff = filter_dataframe(df_game, genres, companies, year_slider, stores)
    dff = dff[columns_table].sort_values('Number of Vote', ascending=False)
    dff['Number of Vote'] = dff['Number of Vote'].map(lambda x:f'{x:,}')
    dff['Mean Note'] = dff['Mean Note'].map(lambda x:f'{x:.1f}')
    return dff.to_dict('records')


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("stores_selected", "value"),
    ],
)
def make_count_figure(genres, companies, year_slider, stores):
    layout_count = copy.deepcopy(layout)
    dff = filter_dataframe(df_game, genres, companies, [start_year, end_year], stores)
    g = dff[['Release date', 'Number of Vote']].set_index('Release date') 
    g = g.resample("A").sum()
    g.loc[:, 'Release date'] = g.index
    colors = []
    for i in range(2000, end_year + 1):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")
    data = [
        dict(
            type="scatter",
            mode="markers",
            x=g.index,
            y=g["Number of Vote"] / 2,
            name="reviews",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=g.index,
            y=g["Number of Vote"],
            name="reviews",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Number of Vote per Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure

# Main
if __name__ == "__main__":
    app.run_server(debug=True)
