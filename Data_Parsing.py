import pandas as pd
from pymavlink import mavutil

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
file_name = "00000001.BIN" # Заміни на назву свого файлу
try:
    telemetry_df = parse_telemetry(file_name)
    
    # Зберігаємо результат у CSV для подальшого аналізу
    telemetry_df.to_csv("processed_telemetry.csv", index=False)

except FileNotFoundError:
    print(f"Помилка: Файл {file_name} не знайдено. Переконайся, що він у тій же папці.")
except Exception as e:
    print(f"Сталася помилка: {e}")