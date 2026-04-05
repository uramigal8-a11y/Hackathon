import requests
import json

def analyze_flight_data(data_input):
    API_KEY = "AIzaSyDYc6o8yeut0sxnsRY2VRBcu9gERo3AnMI"
    raw_text = data_input.get("console_output", "")
    
    if not raw_text or len(raw_text.strip()) < 10:
        return "⚠️ Дані відсутні. Спочатку натисніть 'Обробити дані (EXE)'."

    # Пробуємо v1beta, вона частіше пропускає нові ключі
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Ти аналітик БПЛА. Проаналізуй ці дані українською:\n{raw_text}"}]}]
    }

    # ЯКЩО У ТЕБЕ Є VPN - ПЕРЕКОНАЙСЯ, ЩО ВІН УВІМКНЕНИЙ (США/НІМЕЧЧИНА).
    # Якщо VPN на всьому комп'ютері, код нижче спрацює автоматично.

    try:
        response = requests.post(
            url, 
            headers={'Content-Type': 'application/json'}, 
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            error_data = response.json()
            msg = error_data.get("error", {}).get("message", "")
            if "location" in msg.lower():
                return "❌ Помилка: Google блокує запити з України. Будь ласка, увімкніть VPN (країна США або Європа) і перезапустіть програму."
            return f"❌ Помилка API {response.status_code}: {msg}"

    except Exception as e:
        return f"❌ Помилка зв'язку: {str(e)}"