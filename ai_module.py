import google.generativeai as genai

def get_ai_analysis(max_speed, max_alt, total_dist, duration):
    # Замініть на свій ключ (згідно з порадою використовувати безкоштовні API) [cite: 26]
    genai.configure(api_key="ВАШ_GEMINI_API_KEY") 
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Ти — експерт з аналізу телеметрії БПЛА Ardupilot. 
    Проаналізуй наступні показники польоту:
    - Максимальна швидкість: {max_speed} м/с
    - Максимальна висота: {max_alt} м
    - Загальна дистанція: {total_dist} м
    - Тривалість польоту: {duration} с
    
    Сформуй короткий висновок. Зверни увагу на можливі аномалії (наприклад, занадто велика швидкість або різка зміна висоти)[cite: 25].
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Помилка AI аналізу: {e}"