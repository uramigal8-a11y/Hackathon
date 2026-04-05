import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


pio.renderers.default = "colab"

def create_3d_plot(file_path):
    
    df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()
fig = go.Figure(data=[go.Scatter3d(
    x=df['x'],
    y=df['y'],
    z=df['z'],
    mode='lines',
    line=dict(
        width=6,
        color=df['speed'],
        colorscale='YlOrRd',
        showscale=True
    )
)])
fig.update_layout(

    paper_bgcolor='white',
    font_color='#1c63e8',

    scene=dict(

        bgcolor='white',


        xaxis=dict(
            gridcolor='white',
            zerolinecolor='white',
            backgroundcolor='#ecf0f1',
            showbackground=True,
            title='Схід'
        ),
        yaxis=dict(
            gridcolor='white',
            zerolinecolor='white',
            backgroundcolor='#ecf0f1',
            showbackground=True,
            title='Північ'
        ),
        zaxis=dict(
            gridcolor='white',
            zerolinecolor='white',
            backgroundcolor='#ecf0f1',
            showbackground=True,
            title='Висота'
        ),
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=0.5)
    )
)

fig.update_scenes(
    xaxis_showgrid=True,
    yaxis_showgrid=True,
    zaxis_showgrid=True,
    xaxis_zeroline=True,
    yaxis_zeroline=True
)
fig.show()
