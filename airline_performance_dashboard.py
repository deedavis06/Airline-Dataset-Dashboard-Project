"""The goal is to analyze the performance of the reporting airlines to improve flight reliability thereby 
improving customer reliability."""
from dash import Dash, dcc, html, Input, Output, State, no_update
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

#Create a Dash application
app = Dash(__name__)

#Clear the layout and do not display exception until callback gets executed
app.config.suppress_callback_exceptions = True

#Read the airline data into pandas dataframe
airline_data = pd.read_csv(r'C:\Users\JoeDe\Downloads\airline_data.csv',
                            encoding = "ISO-8859-1", 
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str}) 

#Create a list of years
years_list=list(map(str, range(2005, 2021)))

def compute_data_choice(airline_dataframe):
    #Number of flights under different cancellation categories using a bar chart
    bar_data= airline_dataframe.groupby(['Month', 'CancellationCode'])['Flights'].sum().reset_index()
    #Average flight time by reporting airline using a line chart
    line_data = airline_dataframe.groupby(['Month','Reporting_Airline'])['AirTime'].mean().reset_index()
    #Percentage of diverted airport landings per reporting airline using a pie chart (landings cannot equal 0)
    pie_data=airline_dataframe[airline_dataframe['DivAirportLandings'] != 0]
    #Number of flights flying from each state using choropleth map.
    choropleth_data=airline_dataframe.groupby(['OriginState'])['Flights'].sum().reset_index()
    #Number of flights flying to each state from each reporting airline using treemap chart.
    tree_data=airline_dataframe.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    return bar_data, line_data,pie_data, choropleth_data, tree_data

def compute_info(airline_dataframe):
    avg_car = airline_dataframe.groupby(['Month','Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    avg_weather = airline_dataframe.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    avg_NAS = airline_dataframe.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
    avg_sec = airline_dataframe.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    avg_late = airline_dataframe.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return avg_car, avg_weather, avg_NAS, avg_sec, avg_late
#Layout Section of Dash
#TASK1: Add title to the dashboard
app.layout = html.Div(children=[html.H1('US Domestic Airline Flights Performance', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
             html.Br(),
            #Outer Division 1 
            html.Div([
                #Add a division
                html.Div([
                    #Create a division for heading and dropdown 
                    html.Div([
                        html.H2('Report Type', style={'margin-right':'2em'}),
                      ]),
                #TASK2:Add a dropdown
                    dcc.Dropdown(id='report-type', options=[
                    {'label': 'Yearly Airline Performance Report', 'value': 'OPT1'},
                    {'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}
                    ],
                    placeholder='Select a Report Type',
                    style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-align-last':'center'}),
                    #Place next to each other
                    ], style={'display':'flex'}),
                #Add a division
                html.Div([
                   #Create a division for adding heading and dropdown
                   html.Div([html.H2('Choose Year:', style={'margin-right': '2em'})      
                   ]),
                   dcc.Dropdown(id='input-year', options=[
                   #Iterate through years list
                   {'label': x, 'value': x} for x in years_list],
                   placeholder="Select a year",
                   style={'width':'80%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'}),  
                   ], style={'display':'flex'}),      
                   ]),
            #Add graphs
            #Add an empty division will be updated during callback when id is provided
            #Display graph 1
            html.Div([], id='plot1'),
            #Display graphs 2 and 3
            html.Div([
            html.Div([], id='plot2'),
            html.Div([], id='plot3')],
            style={'display':'flex'}),
            #Display graphs 4 and 5  
            html.Div([
            html.Div([], id='plot4'),
            html.Div([], id='plot5')],
            style={'display':'flex'}),
            ])
    #Outer division ends

#Layout ends
#TASK4: Add 5 output components

@app.callback([Output(component_id='plot1', component_property='children'),
               Output(component_id='plot2', component_property='children'),
               Output(component_id='plot3', component_property='children'),
               Output(component_id='plot4', component_property='children'),
               Output(component_id='plot5', component_property='children')],
               [Input(component_id='report-type', component_property='value'),
               Input(component_id='input-year', component_property='value')],    
               #REVIEW4: Holding output state until user enters all the form information
               #In this case, it will be chart type and year
                [State("plot1", 'children'), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")
               ]) 
def get_graph(report, entered_year, c1,c2,c3,c4,c5):
    # Compute required information for creating graph from the data
    df =  airline_data[airline_data['Year']==int(entered_year)]
    if report=='OPT1':
        bar_data, line_data,pie_data, choropleth_data, tree_data=compute_data_choice(df)
        #Number of flights under different cancellation categories
        bar_chart=px.bar(bar_data,x='Month', y='Flights', color='CancellationCode', title='Monthly Flight Cancellation')
        #TASK5:Average flight time by reporting airline
        line_chart = px.line(line_data, x='Month', y='AirTime', color='Reporting_Airline', title='Average Monthly Flight Time (minutes) by Airline')   
        #Percentage of diverted airport landings per reporting airline
        pie_chart=px.pie(pie_data, values='Flights', names='Reporting_Airline', title='Percentage of Flights by Reporting Airline')
        #Number of flights flying from each state
        choropleth_map=px.choropleth(choropleth_data, locations='OriginState', 
                    color='Flights',  
                    hover_data=['OriginState', 'Flights'], 
                    locationmode = 'USA-states', # Set to plot as US States
                    color_continuous_scale='Viridis',
                    range_color=[0, choropleth_data['Flights'].max()]) 
        choropleth_map.update_layout(
                    title_text = 'Number of Flights from Origin State', 
                    geo_scope='usa') # Plot only the USA instead of globe
        #TASK6:Number of flights flying to each state from each reporting airline
        treemap_chart=px.treemap(tree_data, path=['DestState', 'Reporting_Airline'], 
                                 values='Flights', color='Flights',color_continuous_scale='RdBu',
                                 title='Flight Count by Airline to Destination State')
        #Return dcc.Graph component to the empty division
        return[dcc.Graph(figure=bar_chart),
               dcc.Graph(figure=line_chart),
               dcc.Graph(figure= pie_chart),
               dcc.Graph(figure= choropleth_map),
               dcc.Graph(figure= treemap_chart)
               ]
            
    else:
        avg_car, avg_weather, avg_NAS, avg_sec, avg_late = compute_info(df)
            
        # Line plot for carrier delay
        carrier_fig = px.line(avg_car, x='Month', y='CarrierDelay', color='Reporting_Airline', title='Average Carrrier Delay Time (minutes) by Airline')
        # Line plot for weather delay
        weather_fig = px.line(avg_weather, x='Month', y='WeatherDelay', color='Reporting_Airline', title='Average Weather Delay Time (minutes) by Airline')
        # Line plot for nas delay
        nas_fig = px.line(avg_NAS, x='Month', y='NASDelay', color='Reporting_Airline', title='Average NAS Delay Time (minutes) by Airline')
        # Line plot for security delay
        sec_fig = px.line(avg_sec, x='Month', y='SecurityDelay', color='Reporting_Airline', title='Average Security Delay Time (minutes) by Airline')
        # Line plot for late aircraft delay
        late_fig = px.line(avg_late, x='Month', y='LateAircraftDelay', color='Reporting_Airline', title='Average Late Aircraft Delay Time (minutes) by Airline')
            
        return[dcc.Graph(figure=carrier_fig), 
               dcc.Graph(figure=weather_fig), 
               dcc.Graph(figure=nas_fig), 
               dcc.Graph(figure=sec_fig), 
               dcc.Graph(figure=late_fig)]
    
            
#Run the application
   
if __name__ == '__main__':
    app.run_server()

#This code was part of the final assignment for the IBM Data Science Certificate, Data Visualization course, from Coursera
