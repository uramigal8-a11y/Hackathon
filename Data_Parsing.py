import os
import pandas as pd
from pymavlink import mavutil

# Константи для шляхів
SOURCE_FOLDER = "BIN_Files"
OUTPUT_FOLDER = "CVS_Files"
RAW_CSV = os.path.join(OUTPUT_FOLDER, "result.csv")

def ensure_dirs():
    """Створює необхідні папки, якщо вони відсутні."""
    for folder in [SOURCE_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def parse_telemetry(file_path):
    """Основна функція парсингу .BIN файлу."""
    # Ігноруємо системні файли macOS
    if os.path.basename(file_path).startswith('._'):
        return pd.DataFrame()

    try:
        mlog = mavutil.mavlink_connection(file_path)
        data = []
        while True:
            msg = mlog.recv_msg()
            if msg is None: 
                break
            if msg.get_type() in ['GPS', 'IMU']: # Фільтрація повідомлень
                msg_dict = msg.to_dict()
                msg_dict['Type'] = msg.get_type()
                data.append(msg_dict)
        mlog.close()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Помилка парсингу: {e}")
        return pd.DataFrame()

def process_uploaded_file(uploaded_file):
    """
    Повний цикл обробки: Збереження -> Парсинг -> Видалення BIN -> Запис CSV
    """
    ensure_dirs()
    bin_path = os.path.join(SOURCE_FOLDER, uploaded_file.name)
    
    # 1. Тимчасово зберігаємо завантажений файл
    with open(bin_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 2. Парсимо дані в DataFrame
    df = parse_telemetry(bin_path)
    
    # 3. Видаляємо вхідний файл відразу після парсингу
    if os.path.exists(bin_path):
        os.remove(bin_path)
        print(f"Файл {uploaded_file.name} видалено після обробки.")
    
    # 4. Перевіряємо результат і зберігаємо CSV
    if not df.empty:
        df.to_csv(RAW_CSV, index=False)
        return True, "Дані успішно оброблені, BIN видалено."
    else:
        return False, "Помилка: файл не містить даних GPS/IMU."