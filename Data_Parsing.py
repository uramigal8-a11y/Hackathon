import os
import pandas as pd
from pymavlink import mavutil

def get_latest_bin_file(folder_path):
    # 1. Отримуємо список усіх файлів у папці
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    except FileNotFoundError:
        print(f"Помилка: Папка {folder_path} не існує.")
        return None

    # 2. Фільтруємо лише .BIN файли
    bin_files = [f for f in files if f.upper().endswith('.BIN')]

    if not bin_files:
        print("У папці немає .BIN файлів.")
        return None

    # 3. Сортуємо файли за часом останньої зміни (найновіший буде першим)
    bin_files.sort(key=os.path.getmtime, reverse=True)

    return bin_files[0] # Повертаємо шлях до найсвіжішого файлу

def parse_telemetry(file_path):
    mlog = mavutil.mavlink_connection(file_path)
    
    data = []
    
    # Словники для збереження міток часу (щоб вирахувати частоту)
    last_times = {"GPS": [], "IMU": []}

    while True:
        # Отримуємо наступне повідомлення з файлу
        msg = mlog.recv_msg()
        if msg is None:
            break # Файл закінчився

        msg_type = msg.get_type()

        # 2. Витягуємо дані GPS та IMU
        # В Ardupilot IMU зазвичай записується як 'IMU', 'IMU2' або 'ATT'
        # GPS зазвичай як 'GPS' або 'GPA'
        if msg_type in ['GPS', 'IMU']:
            msg_dict = msg.to_dict()
            msg_dict['Type'] = msg_type
            
            # Додаємо в загальний список
            data.append(msg_dict)
            
            # Зберігаємо час повідомлення для аналізу частоти (TimeUS - мікросекунди)
            if 'TimeUS' in msg_dict:
                last_times[msg_type].append(msg_dict['TimeUS'])

    # 3. Формуємо структурований масив даних (pandas DataFrame)
    df = pd.DataFrame(data)

    # 4. Визначаємо частоти семплювання (Sampling Frequency)
    for sensor in ["GPS", "IMU"]:
        times = last_times[sensor]
        if len(times) > 1:
            # Обчислюємо різницю між сусідніми записами в секундах
            time_diffs = pd.Series(times).diff().dropna() / 1_000_000
            avg_freq = 1 / time_diffs.mean()

    return df

# --- ВИКОРИСТАННЯ ---
# Визначаємо назву папки для результатів
output_folder = "CVS_Files"
# Вкажи назву папки, куди дашборд буде завантажувати файли
folder_to_watch = "BIN_Files"
# Додати ім'я файлу
file_name = get_latest_bin_file(folder_to_watch) 
try:
    telemetry_df = parse_telemetry(file_name)
    
    # Використовуємо оригінальну назву файлу, щоб не плутатися
    file_base_name = os.path.basename(file_name).split('.')[0]
    output_path = os.path.join(output_folder, f"{file_base_name}.csv")

    telemetry_df.to_csv(output_path, index=False)

except FileNotFoundError:
    print(f"Помилка: Файл {file_name} не знайдено. Переконайся, що він у тій же папці.")
except Exception as e:
    print(f"Сталася помилка: {e}")