import streamlit as st
import os
import subprocess
from Data_Parsing import process_uploaded_file, OUTPUT_FOLDER
from visualization3d import create_3d_plot 
from ai_assistant import analyze_flight_data

st.set_page_config(page_title="Drone Analysis System", layout="wide")
st.title("🛸 Drone Telemetry Analysis & AI")

# Створення папок при запуску
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

uploaded_file = st.file_uploader("Завантажте польотний файл .BIN", type="bin")

if uploaded_file:
    # 1. Парсинг файлу
    if 'file_parsed' not in st.session_state:
        with st.spinner('Розшифровка BIN файлу...'):
            success, message = process_uploaded_file(uploaded_file)
            st.session_state.file_parsed = success
            if success: st.success("Файл успішно розпарсено у CSV!")
            else: st.error(f"Помилка: {message}")

    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Метрики та ШІ")
        
        if st.button("🚀 Розрахувати фізику (metrics.exe)"):
            if os.path.exists("metrics.exe"):
                try:
                    with st.spinner('EXE обчислює дані...'):
                        # timeout=20 рятує від "вічної загрузки"
                        result = subprocess.run(
                            ["metrics.exe"], 
                            capture_output=True, 
                            text=True, 
                            timeout=20,
                            encoding='utf-8'
                        )
                        st.session_state.metrics_text = result.stdout
                        st.success("Обчислення завершено!")
                except subprocess.TimeoutExpired:
                    st.error("EXE працює занадто довго. Перевірте вхідні дані.")
                except Exception as e:
                    st.error(f"Критична помилка: {e}")
            else:
                st.error("Файл metrics.exe не знайдено в папці проекту!")

        if 'metrics_text' in st.session_state:
            st.text_area("Звіт аналізатора:", st.session_state.metrics_text, height=200)
            
            if st.button("🤖 Сформувати ШІ-висновок"):
                with st.spinner('ШІ аналізує політ...'):
                    ai_report = analyze_flight_data({"console_output": st.session_state.metrics_text})
                    st.info(ai_report)

    with col2:
        st.subheader("🌐 3D Візуалізація")
        path_3d = os.path.join(OUTPUT_FOLDER, "clean_data.csv")
        if os.path.exists(path_3d):
            fig = create_3d_plot(path_3d)
            if fig: st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Після натискання кнопки 'Розрахувати фізику' тут з'явиться 3D-трек.")