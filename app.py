import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd

# Read in the USA counties shape files
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

########### Define a few variables ######

tabtitle = 'Census Counties'
sourceurl = 'https://www.kaggle.com/muonneutrino/us-census-demographic-data'
githublink = 'https://github.com/pratikadyalkar/305-virginia-census-data'
varlist= ['TotalPop', 'Men', 'Women', 'Hispanic',
       'White', 'Black', 'Native', 'Asian', 'Pacific', 'VotingAgeCitizen',
       'Income', 'IncomeErr', 'IncomePerCap', 'IncomePerCapErr', 'Poverty',
       'ChildPoverty', 'Professional', 'Service', 'Office', 'Construction',
       'Production', 'Drive', 'Carpool', 'Transit', 'Walk', 'OtherTransp',
       'WorkAtHome', 'MeanCommute', 'Employed', 'PrivateWork', 'PublicWork',
       'SelfEmployed', 'FamilyWork', 'Unemployment', 'RUCC_2013']

df = pd.read_pickle('resources/cou-stats.pkl')
states = pd.read_csv('resources/states.csv')
selectdf = pd.DataFrame()
lat=long=0
########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout

app.layout = html.Div(children=[
    html.H1('Census Data 2017'),
    # Dropdowns
    html.Div(children=[
        # left side
        html.Div([
                html.H6('Select census variable:'),
                dcc.Dropdown(
                    id='state-drop',
                    options=[{'label': i, 'value': i} for i in states.state],
                    placeholder = 'Select a State'
                ),
               
        ], className='six columns'),
        html.Div([
                dcc.Dropdown(
                    id='stats-drop',
                    options=[{'label': i, 'value': i} for i in varlist],
                    placeholder = 'Select a variable'
                ),
        ], className='six columns'),
        # right side
        html.Div([
            dcc.Graph(id='va-map')
        ], className='twelve columns'),
    ], className='twelve columns'),

    # Footer
    html.Br(),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A("Data Source", href=sourceurl),
    ]
)

############ Callbacks
@app.callback(Input('state-drop','value'))
def change_state(sel_state):
    lat = states[(states['state']==sel_state)]['lat'].values[0]
    long = states[(states['state']==sel_state)]['long'].values[0]
    selectdf =  df.loc[df['State_x']==sel_state]
    

@app.callback(Output('va-map', 'figure'),
              [Input('stats-drop', 'value')])
def display_results(selected_value):
    valmin=selectdf[selected_value].min()
    valmax=selectdf[selected_value].max()
    fig = go.Figure(go.Choroplethmapbox(geojson=counties,
                                    locations=selectdf['FIPS'],
                                    z=selectdf[selected_value],
                                    colorscale='Blues',
                                    text=selectdf['County'],
                                    zmin=valmin,
                                    zmax=valmax,
                                    marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5.8,
                      mapbox_center = {"lat": lat, "lon": long})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# https://community.plot.ly/t/what-colorscales-are-available-in-plotly-and-which-are-the-default/2079
    return fig


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
