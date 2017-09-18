# Adapted from 
#   https://plot.ly/python/choropleth-maps/#united-states-choropleth-map
# Generates webpage viweable version.
#   Have to sign up for Plot.ly pro account to export to vector graphic format
#
# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

#import plotly.plotly as py
import plotly.offline as py
import pandas as pd

df = pd.read_csv('StateBuprenorphineNaloxone.csv')

for col in df.columns:
    df[col] = df[col].astype(str)

scl =   [   [0.0, 'rgb(242,242,202)'],
            [1.0, 'rgb(228,32,32)'],
        ]

data = [ dict(
        type='choropleth',
        colorscale = scl,
        autocolorscale = False,
        locations = df['nppes_provider_state'],
        z = df['ClaimsRatio'].astype(float) * 1000, # Scale up small decimal values for better readability
        locationmode = 'USA-states',
        text = df['State'],
        marker = dict(
            line = dict (
                color = 'rgb(100,100,100)',
                width = 1
            )
        ),
        colorbar = dict(
            title = "Claims Ratio<br>(per 1,000)",
            nticks=5
        )
    ) ]

layout = dict(
        
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showlakes = False,
            lakecolor = 'rgb(255, 255, 255)',
        ),
    )
    
fig = dict( data=data, layout=layout )

#url = py.plot( fig, filename='d3-cloropleth-map' )
url = py.plot( fig )
