import streamlit as st
import os
import pandas as pd
import subprocess
import plotly.graph_objects as go
import time
from Data_Parsing import parse_telemetry 

st.set_page_config(page_title="Drone Analysis", layout="wide")

# Створюємо папку CVS_Files, бо старий EXE колеги точно її хоче
if not os.path.exists("CVS_Files"):
    os.makedirs("CVS_Files")

st.title("🚁 Drone Telemetry Analysis")

uploaded_file = st.file_uploader("Виберіть файл .BIN", type="bin")

if uploaded_file is not None:
    bin_path = os.path.join("BIN_Files", uploaded_file.name)
    if not os.path.exists("BIN_Files"): os.makedirs("BIN_Files")
    
    with open(bin_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner('Парсинг...'):
        df_raw = parse_telemetry(bin_path)
        if not df_raw.empty:
            # Кладемо файл ОДНОЧАСНО в корінь і в папку CVS_Files
            # Це гарантує, що EXE його знайде, де б він не шукав
            df_raw.to_csv("result.csv", index=False)
            df_raw.to_csv("CVS_Files/result.csv", index=False)
        else:
            st.error("Дані порожні")
            st.stop()

    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Результати (C++)")
        if os.path.exists("metrics.exe"):
            try:
                # Запускаємо EXE
                process = subprocess.run(['metrics.exe'], capture_output=True, text=True, encoding='utf-8')
                st.code(process.stdout)
                
                # Чекаємо появи результату в обох можливих місцях
                found_path = None
                for _ in range(10):
                    if os.path.exists("CVS_Files/clean_data.csv"):
                        found_path = "CVS_Files/clean_data.csv"
                        break
                    if os.path.exists("clean_data.csv"):
                        found_path = "clean_data.csv"
                        break
                    time.sleep(0.5)
                
                if found_path:
                    df_enu = pd.read_csv(found_path)
                    with col2:
                        st.subheader("📍 3D Візуалізація")
                        # Малюємо графік (використовуємо x,y,z - це стандарт для вашого коду)
                        fig = go.Figure(data=[go.Scatter3d(
                            x=df_enu['x'], y=df_enu['y'], z=df_enu['z'],
                            mode='lines',
                            line=dict(width=5, color=df_enu['speed'], colorscale='Viridis')
                        )])
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("EXE відпрацював, але не створив файл clean_data.csv ні в корені, ні в CVS_Files")
            except Exception as e:
                st.error(f"Помилка EXE: {e}")