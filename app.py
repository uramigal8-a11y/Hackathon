import streamlit as st
import os
import pandas as pd
import subprocess
import time
import plotly.graph_objects as go
from Data_Parsing import process_uploaded_file, OUTPUT_FOLDER
from visualization3d import create_3d_plot 

st.set_page_config(page_title="Drone Analysis", layout="wide")
st.title("Drone Telemetry Analysis")

uploaded_file = st.file_uploader("Виберіть файл .BIN", type="bin")

if uploaded_file:
    with st.spinner('Обробка даних...'):
        success, message = process_uploaded_file(uploaded_file)
        
    if not success:
        st.error(message)
        st.stop()

    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Результати (C++)")
        if os.path.exists("metrics.exe"):
            try:
                process = subprocess.run(['metrics.exe'], capture_output=True, text=True, encoding='utf-8')
                st.code(process.stdout)
                
                clean_data_path = os.path.join(OUTPUT_FOLDER, "clean_data.csv")
                found = False
                for _ in range(10):
                    if os.path.exists(clean_data_path):
                        found = True
                        break
                    time.sleep(0.5)
                
                if found:
                    with col2:
                        st.subheader("3D Візуалізація")
                        # Передаємо тільки шлях, ніякого pandas тут
                        fig = create_3d_plot(clean_data_path)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Файл clean_data.csv не знайдено після роботи EXE.")
            except Exception as e:
                st.error(f"Помилка при запуску метрик: {e}")
        else:
            st.warning("Файл metrics.exe не знайдено в корені проекту.")