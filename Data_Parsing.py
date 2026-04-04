import os
import time
import pandas as pd
from pymavlink import mavutil

# --- НАЛАШТУВАННЯ ---
SOURCE_FOLDER = "BIN_Files"
OUTPUT_FOLDER = "CVS_Files"
OUTPUT_FILENAME = "result.csv"  # Одне фіксоване ім'я для всіх результатів

def parse_telemetry(file_path):
    # Ігноруємо системні файли macOS
    if os.path.basename(file_path).startswith('._'):
        print("Пропущено системний файл macOS")
        return pd.DataFrame()

    mlog = mavutil.mavlink_connection(file_path)
    data = []
    try:
        while True:
            msg = mlog.recv_msg()
            if msg is None: 
                break
            if msg.get_type() in ['GPS', 'IMU']:
                msg_dict = msg.to_dict()
                msg_dict['Type'] = msg.get_type()
                data.append(msg_dict)
    except Exception as e:
        print(f"Помилка при читанні: {e}")
    finally:
        mlog.close()
    
    df = pd.DataFrame(data)
    print(f"Знайдено записів: {len(df)}") # Це допоможе вам у відладці
    return df

def main_watcher():
    # Створюємо папки, якщо їх немає
    if not os.path.exists(SOURCE_FOLDER): os.makedirs(SOURCE_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

    print(f"Моніторинг папки {SOURCE_FOLDER} розпочато...")

    try:
        while True:
            # Шукаємо всі .BIN файли
            files = [f for f in os.listdir(SOURCE_FOLDER) if f.upper().endswith('.BIN')]

            for filename in files:
                bin_path = os.path.join(SOURCE_FOLDER, filename)
                csv_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

                print(f"Обробка: {filename}...")

                try:
                    # Даємо системі трохи часу завершити запис файлу, якщо він ще копіюється
                    time.sleep(0.5)

                    # Конвертація
                    df = parse_telemetry(bin_path)
                    
                    if not df.empty:
                        df.to_csv(csv_path, index=False)
                        print(f"Готово: {OUTPUT_FILENAME}")
                    else:
                        print(f"Файл {filename} порожній або не містить GPS/IMU даних.")

                    # Видалення вхідного файлу
                    os.remove(bin_path)
                    print(f"Оригінал {filename} видалено.")

                except Exception as e:
                    print(f"Помилка при обробці {filename}: {e}")

            # Пауза перед наступною перевіркою папки
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nЗупинка моніторингу.")

if __name__ == "__main__":
    main_watcher()