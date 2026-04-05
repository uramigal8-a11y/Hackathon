import os

def run():
    path = "CVS_Files/ai_summary.txt"
    if not os.path.exists(path):
        print("Pomylka: ai_summary.txt ne znaydeno!")
        return

    with open(path, 'r') as f:
        # Читаємо рядки і перетворюємо в числа
        d = [float(line.strip()) for line in f.readlines() if line.strip()]
    
    duration, speed, accel, dist, alt = d

    print("\n" + "="*40)
    print("🤖 AI FLIGHT INTERPRETER")
    print("="*40)

    if accel > 15.0:
        print("⚠️ KRITYCHNE PEREVANTAZHENNYA! Perevirte dron.")
    if alt > 120.0:
        print("📍 PORUSHENNYA VISOTY! Ponad 120m.")
    
    if accel <= 15.0 and alt <= 120.0:
        print("✅ Polit stabil'nyy. Anomaliy ne vyiavleno.")

    print(f"\nStats: {dist:.1f}m za {duration:.1f}s")
    print("="*40)

if __name__ == "__main__":
    run()