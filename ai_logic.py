import google.generativeai as genai

def generate_flight_analysis(metrics):
    # Налаштування API (рекомендується використовувати безкоштовні АРІ [cite: 26])
    genai.configure(api_key="ВАШ_КЛЮЧ_GEMINI")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Формування запиту для виявлення аномалій, як-от втрати висоти 
    prompt = f"""
    Проаналізуй дані польоту БПЛА Ardupilot:
    - Максимальна швидкість: {metrics['max_speed']} м/с
    - Пройдена дистанція: {metrics['total_dist']} м
    - Тривалість: {metrics['duration']} с
    
    Зроби короткий текстовий висновок про політ та вияви можливі проблеми.
    """
    
    response = model.generate_content(prompt)
    return response.text