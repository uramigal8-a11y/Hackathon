import streamlit as st
import os
import pandas as pd
import subprocess
import plotly.graph_objects as go
from Data_Parsing import parse_telemetry 

# 1. Налаштування
st.set_page_config(page_title="Drone Hackathon Dashboard", layout="wide")

# Створюємо папку для вхідних BIN, якщо її нема
if not os.path.exists("BIN_Files"):
    os.makedirs("BIN_Files")

st.title("🚁 Drone Telemetry Analysis")

# Кнопка скидання в сайдбарі
if st.sidebar.button("🔄 Очистити і перезапустити"):
    st.rerun()

# 2. Завантаження файлу
uploaded_file = st.file_uploader("Виберіть файл .BIN", type="bin")

if uploaded_file is not None:
    # Зберігаємо BIN
    bin_path = os.path.join("BIN_Files", uploaded_file.name)
    with open(bin_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.success(f"Завантажено: {uploaded_file.name}")

    # 3. Етап Python: Парсинг
    with st.spinner('Парсинг BIN файлу...'):
        df_raw = parse_telemetry(bin_path)
        df_raw.to_csv("result.csv", index=False) # Готуємо файл для C++

    # 4. Етап C++: Розрахунок метрик
    st.divider()
    col1, col2 = st.columns([1, 2]) # Створюємо колонки ТУТ

    with col1:
        st.subheader("📊 Результати аналізу (C++)")
        try:
            # Запускаємо metrics.exe, який лежить поруч
            process = subprocess.run(['metrics.exe'], capture_output=True, text=True, encoding='cp1251')
            if process.stdout:
                st.code(process.stdout)
            else:
                st.error("C++ код не повернув даних. Перевірте консоль.")
        except Exception as e:
            st.error(f"Помилка запуску metrics.exe: {e}")

    with col2:
        st.subheader("📍 3D Візуалізація")
        # Чекаємо, поки C++ створить clean_data.csv
        if os.path.exists("clean_data.csv"):
            df_enu = pd.read_csv("clean_data.csv")
            
            # Будуємо графік на основі ENU координат (x, y, z), які порахував твій C++
            fig = go.Figure(data=[go.Scatter3d(
                x=df_enu['x'],
                y=df_enu['y'],
                z=df_enu['z'],
                mode='lines',
                line=dict(width=5, color=df_enu['speed'], colorscale='Viridis', showscale=True)
            )])
            
            fig.update_layout(
                template="plotly_dark",
                scene=dict(xaxis_title='East (m)', yaxis_title='North (m)', zaxis_title='Altitude (m)'),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Очікування даних від C++ для побудови графіка...")
else:
    st.info("Будь ласка, завантажте телеметрію для початку.")