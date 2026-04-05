import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "colab"

def create_3d_plot(file_path):
    """
    Створює 3D графік траєкторії БПЛА на основі CSV файлу.
    Стиль: Світлий професійний (White/Blue/YlOrRd)
    """
    # 1. Завантаження та підготовка даних
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()  # Очищення назв від пробілів
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return None

    # 2. Побудова траєкторії
    fig = go.Figure(data=[go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='lines',
        line=dict(
            width=6,
            color=df['speed'],
            colorscale='YlOrRd',  # Жовто-червона палітра (швидкість)
            showscale=True,
            colorbar=dict(title="v (м/с)", thickness=15)
        ),
        name='Траєкторія'
    )])

    # 3. Налаштування стилю (Layout)
    fig.update_layout(
        title=dict(
            text="Аналіз польотних даних БПЛА",
            x=0.5,
            font=dict(size=18)
        ),
        paper_bgcolor='white',    # Зовнішній фон
        font_color='#1c63e8',      # Твій фірмовий синій колір тексту
        
        scene=dict(
            bgcolor='white',       # Фон 3D сцени
            xaxis=dict(
                title='Схід (м)',
                gridcolor='#f0f0f0',
                zerolinecolor='#bdc3c7',
                backgroundcolor='#ecf0f1',
                showbackground=True
            ),
            yaxis=dict(
                title='Північ (м)',
                gridcolor='#f0f0f0',
                zerolinecolor='#bdc3c7',
                backgroundcolor='#ecf0f1',
                showbackground=True
            ),
            zaxis=dict(
                title='Висота (м)',
                gridcolor='#f0f0f0',
                zerolinecolor='#bdc3c7',
                backgroundcolor='#ecf0f1',
                showbackground=True
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5) # Висота трохи притиснута для зручності
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )

    return fig

# --- БЛОК ЗАПУСКУ ---
if __name__ == "__main__":
    # Вкажи шлях до свого файлу
    path = 'clean_data.csv' 
    
    chart = create_3d_plot(path)
    if chart:
        chart.show()
