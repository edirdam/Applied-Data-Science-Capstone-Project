# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get the list of unique launch site names
launch_sites = spacex_df['Launch Site'].unique()

# Create the options list for next dropdown
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdown_options,
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        #marks={0: '0',100: '100'},
                                        value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Create the pie chart for all launch sites
        success_df = spacex_df[spacex_df['class'] == 1]
        pie_data = success_df.groupby('Launch Site').size().reset_index(name='Count')
        #pie_data['Percentage'] = pie_data['Count'] / len(success_df) * 100
        fig = px.pie(pie_data, values='Count', names='Launch Site', title='All Sites Successful Launches Distribution')
    else:
        # Create the pie chart for the selected test site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_data = site_df.groupby('class').size().reset_index(name='Count')
        fig = px.pie(pie_data, values='Count', names='class', title=f'Successful vs. Failed Launches for {entered_site}')
    return fig

   
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(site_value, payload_value):
    if site_value == 'ALL':
        # Show all launch sites
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_value[0]) & (spacex_df['Payload Mass (kg)'] <= payload_value[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    else:
        # Show selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == site_value]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    fig.update_layout(title='Correlation between Payload and Outcome', xaxis_title='Payload Mass (kg)', yaxis_title='Outcome')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
