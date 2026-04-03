import os
import time
import pandas as pd
from pymavlink import mavutil

# --- НАЛАШТУВАННЯ ---

SOURCE_FOLDER = "BIN_Files"
OUTPUT_FOLDER = "CVS_Files"
SIGNAL_FILE = "start.signal"
HISTORY_FILE = "processed_history.txt"

def get_unique_path(base_folder, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    unique_path = os.path.join(base_folder, filename)

    while os.path.exists(unique_path):
        unique_path = os.path.join(base_folder, f"{name}({counter}){ext}")
        counter += 1
    return unique_path



def get_first_bin_file(folder_path):
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.upper().endswith('.BIN')]

        if not files:
            return None

        files.sort(key=os.path.getmtime)
        return files[0]

    except Exception as e:
        print(f"Помилка пошуку: {e}")
        return None

def parse_telemetry(file_path):
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
    finally:
        mlog.close()  
        
    return pd.DataFrame(data)

def main_loop():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print(f"Очікую '0' у {SIGNAL_FILE}...")

    try:
        while True:
            if os.path.exists(SIGNAL_FILE):
                with open(SIGNAL_FILE, 'r') as f:
                    content = f.read().strip()

                if content == "0":
                    target_bin = get_first_bin_file(SOURCE_FOLDER)

                    if target_bin:
                        try:
                            time.sleep(0.5)
                            
                            df = parse_telemetry(target_bin)
                            bin_name = os.path.basename(target_bin)
                            csv_name = bin_name.replace('.BIN', '.csv').replace('.bin', '.csv')

                            final_output_path = get_unique_path(OUTPUT_FOLDER, csv_name)

                            df.to_csv(final_output_path, index=False)

                            # Записуємо в історію фінальну назву (з лічильником, якщо він був)
                            actual_name_only = os.path.splitext(os.path.basename(final_output_path))[0]
                            with open(HISTORY_FILE, 'a', encoding='utf-8') as history:
                                history.write(f"{actual_name_only}\n")

                            os.remove(target_bin)
                            
                            print(f"Оброблено: {bin_name} збережено як {actual_name_only}")

                        except Exception as e:
                            print(f"Помилка: {e}")
                    else:
                        print("Немає файлів для обробки.")

                    # Очищаємо сигнал
                    with open(SIGNAL_FILE, 'w') as f: f.write("")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Вихід.")

if __name__ == "__main__":
    main_loop()