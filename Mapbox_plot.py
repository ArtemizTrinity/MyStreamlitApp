import pandas as pd
import plotly.express as px

df = pd.read_csv('us-cities-top-1k.csv')

plot = px.scatter_mapbox(data_frame=df,
                         lat='lat', 
                         lon='lon', 
                         size='Population', 
                         zoom=3.5, 
                         title='Top 1000 US Cities by Population',
                         mapbox_style='open-street-map',
    
                         color_discrete_sequence=['blue'],)

plot.show() 



                         