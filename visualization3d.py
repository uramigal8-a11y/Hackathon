import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

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
        title="Аналіз траєкторії БПЛА",
        scene=dict(
            bgcolor='white',
            xaxis=dict(
                gridcolor='#f0f0f0',
                zerolinecolor='white',
                backgroundcolor='#ecf0f1',
                showbackground=True,
                title='Схід (м)'
            ),
            yaxis=dict(
                gridcolor='#f0f0f0',
                zerolinecolor='white',
                backgroundcolor='#ecf0f1',
                showbackground=True,
                title='Північ (м)'
            ),
            zaxis=dict(
                gridcolor='#f0f0f0',
                zerolinecolor='white',
                backgroundcolor='#ecf0f1',
                showbackground=True,
                title='Висота (м)'
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)
        )
    )

    fig.show()


create_3d_plot('clean_data.csv')
