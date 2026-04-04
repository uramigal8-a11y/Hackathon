import pandas as pd
import plotly.graph_objects as go

def create_3d_plot(file_path):
    # Читання даних перенесено сюди, щоб не захаращувати app.py
    df = pd.read_csv(file_path)
    
    fig = go.Figure(data=[go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='lines',
        line=dict(
            width=6,
            color=df['speed'],
            colorscale='Viridis',
            showscale=True
        )
    )])

    fig.update_layout(
        paper_bgcolor='black',
        font_color='#00FF00',
        scene=dict(
            bgcolor='black',
            xaxis=dict(
                gridcolor='#003300',
                zerolinecolor='#00FF00',
                backgroundcolor='black',
                showbackground=True
            ),
            yaxis=dict(
                gridcolor='#003300',
                zerolinecolor='#00FF00',
                backgroundcolor='black',
                showbackground=True
            ),
            zaxis=dict(
                gridcolor='#003300',
                zerolinecolor='#00FF00',
                backgroundcolor='black',
                showbackground=True
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
    
    fig.update_traces(line=dict(colorscale=['#003300', '#00FF00']))
    
    return fig