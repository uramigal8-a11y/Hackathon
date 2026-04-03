#define _USE_MATH_DEFINES
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <windows.h>
#include <algorithm>

using namespace std;

// Структура для зберігання однієї точки даних
struct FlightPoint {
    double timestamp = 0.0;
    double lat = 0.0, lon = 0.0, alt = 0.0;
    double spd = 0.0; // Швидкість по GPS
    double ax = 0.0, ay = 0.0, az = 0.0;
    bool hasGPS = false;
    bool hasIMU = false;
};

class FlightMetrics {
private:
    vector<FlightPoint> points;

    double maxHorizontalSpeed = 0.0;
    double maxVerticalSpeed = 0.0;
    double maxAcceleration = 0.0;
    double maxAltitudeGain = 0.0;
    double totalDistance = 0.0;
    double flightDuration = 0.0;

    double biasX = 0.0, biasY = 0.0, biasZ = 0.0;

    // Структура для 3D візуалізації (координати в метрах)
    struct ENUPoint {
        double x; // East (Схід)
        double y; // North (Північ)
        double z; // Up (Висота)
        double speed;
        double timestamp;
    };
    vector<ENUPoint> enuTrack;

public:
    FlightMetrics(const vector<FlightPoint>& data) : points(data) {}

    // Калібрування акселерометра (пошук нуля)
    void calibrateBias() {
        int count = 0;
        double sumX = 0, sumY = 0, sumZ = 0;
        for (const auto& p : points) {
            if (p.hasIMU) {
                sumX += p.ax; sumY += p.ay; sumZ += p.az;
                if (++count >= 100) break;
            }
        }
        if (count > 0) {
            biasX = sumX / count;
            biasY = sumY / count;
            biasZ = sumZ / count;
        }
    }

    void calculateAllMetrics() {
        if (points.empty()) return;

        calibrateBias();

        flightDuration = points.back().timestamp - points.front().timestamp;

        double vx = 0.0, vy = 0.0, vz = 0.0;
        bool hasPrevIMU = false;
        double prevAx = 0.0, prevAy = 0.0, prevAz = 0.0, prevImuTime = 0.0;

        bool hasPrevGPS = false;
        double prevLat = 0.0, prevLon = 0.0;
        double minAlt = 1e9, maxAlt = -1e9;

        // Змінні для генерації 3D треку (x, y, z)
        bool firstGPS = true;
        double lat0 = 0.0, lon0 = 0.0, alt0 = 0.0, time0 = 0.0;
        const double M_PER_DEG = 111320.0;

        const double ACCEL_THRESHOLD = 0.15;

        for (const auto& p : points) {
            // --- ОБРОБКА GPS (Для 3D та загальних метрик) ---
            if (p.hasGPS) {
                minAlt = min(minAlt, p.alt);
                maxAlt = max(maxAlt, p.alt);
                if (hasPrevGPS) {
                    totalDistance += haversine(prevLat, prevLon, p.lat, p.lon);
                }
                prevLat = p.lat; prevLon = p.lon; hasPrevGPS = true;

                // Розрахунок x, y, z в метрах відносно точки старту
                if (firstGPS) {
                    lat0 = p.lat; lon0 = p.lon; alt0 = p.alt; time0 = p.timestamp;
                    firstGPS = false;
                }

                double t_sec = p.timestamp - time0;
                double y_coord = (p.lat - lat0) * M_PER_DEG; // North
                double x_coord = (p.lon - lon0) * M_PER_DEG * cos(lat0 * M_PI / 180.0); // East
                double z_coord = p.alt - alt0; // Up

                enuTrack.push_back({ x_coord, y_coord, z_coord, p.spd, t_sec });
            }

            // --- ОБРОБКА IMU (Для швидкості та прискорення) ---
            if (p.hasIMU) {
                double curAx = p.ax - biasX;
                double curAy = p.ay - biasY;
                double curAz = p.az - biasZ;

                if (abs(curAx) < ACCEL_THRESHOLD) curAx = 0;
                if (abs(curAy) < ACCEL_THRESHOLD) curAy = 0;
                if (abs(curAz) < ACCEL_THRESHOLD) curAz = 0;

                if (hasPrevIMU) {
                    double dt = p.timestamp - prevImuTime;
                    if (dt > 0.0) {
                        vx += (prevAx + curAx) / 2.0 * dt;
                        vy += (prevAy + curAy) / 2.0 * dt;
                        vz += (prevAz + curAz) / 2.0 * dt;

                        if (curAx == 0 && curAy == 0) { vx *= 0.92; vy *= 0.92; }

                        maxHorizontalSpeed = max(maxHorizontalSpeed, sqrt(vx * vx + vy * vy));
                        maxVerticalSpeed = max(maxVerticalSpeed, abs(vz));
                    }
                }

                double currentAccel = sqrt(curAx * curAx + curAy * curAy + curAz * curAz);
                maxAcceleration = max(maxAcceleration, currentAccel);

                prevAx = curAx; prevAy = curAy; prevAz = curAz;
                prevImuTime = p.timestamp;
                hasPrevIMU = true;
            }
        }

        if (minAlt < 1e9) maxAltitudeGain = maxAlt - minAlt;
    }

    // Експорт у форматі x,y,z для 3D
    void exportFor3D(const string& filepath) {
        ofstream out(filepath);
        if (!out.is_open()) {
            cout << "Помилка: не вдалося створити файл для 3D!\n";
            return;
        }

        // Заголовки тепер x, y, z
        out << "x,y,z,speed,time_sec\n";
        out << fixed << setprecision(6);
        for (const auto& pt : enuTrack) {
            out << pt.x << ","
                << pt.y << ","
                << pt.z << ","
                << pt.speed << ","
                << pt.timestamp << "\n";
        }
        out.close();
        cout << "Файл для 3D (x,y,z) збережено: " << filepath << "\n";
        cout << "Записано GPS точок: " << enuTrack.size() << "\n\n";
    }

    double getMaxHorizontalSpeed() const { return maxHorizontalSpeed; }
    double getMaxVerticalSpeed()   const { return maxVerticalSpeed; }
    double getMaxAcceleration()    const { return maxAcceleration; }
    double getMaxAltitudeGain()    const { return maxAltitudeGain; }
    double getTotalDistance()      const { return totalDistance; }
    double getFlightDuration()     const { return flightDuration; }

private:
    double haversine(double lat1, double lon1, double lat2, double lon2) {
        const double R = 6371000.0;
        double phi1 = lat1 * M_PI / 180.0, phi2 = lat2 * M_PI / 180.0;
        double dPhi = (lat2 - lat1) * M_PI / 180.0;
        double dLambda = (lon2 - lon1) * M_PI / 180.0;
        double a = sin(dPhi / 2) * sin(dPhi / 2) +
            cos(phi1) * cos(phi2) *
            sin(dLambda / 2) * sin(dLambda / 2);
        return R * 2 * atan2(sqrt(a), sqrt(1 - a));
    }
};

int main() {
    SetConsoleOutputCP(65001);
    cout << "=== Обчислення метрик польоту БПЛА ===\n\n";

    // Шляхи до файлів
    string inputPath = "CVS_Files/result.csv";
    string out3DPath = "CVS_Files/clean_data.csv";

    ifstream file(inputPath);
    if (!file.is_open()) {
        cout << "Помилка: не вдалося відкрити файл result.csv!\n";
        return 1;
    }

    vector<FlightPoint> data;
    string line;
    getline(file, line); // Пропуск заголовка

    int imuCount = 0, gpsCount = 0, skipped = 0;

    while (getline(file, line)) {
        if (line.empty()) continue;
        try {
            stringstream ss(line);
            vector<string> cols;
            string token;
            while (getline(ss, token, ',')) cols.push_back(token);
            if (cols.empty()) continue;

            string type = cols[0];
            FlightPoint p;
            p.timestamp = stod(cols[1]) / 1000000.0; // перевід мікросекунд в секунди

            if (type == "IMU" && cols.size() >= 9) {
                p.ax = stod(cols[6]); p.ay = stod(cols[7]); p.az = stod(cols[8]);
                p.hasIMU = true; imuCount++;
                data.push_back(p);
            }
            else if (type == "GPS" && cols.size() >= 26) {
                p.lat = stod(cols[22]);
                p.lon = stod(cols[23]);
                p.alt = stod(cols[24]);
                p.spd = stod(cols[25]); // Швидкість по GPS (Spd)
                p.hasGPS = true; gpsCount++;
                data.push_back(p);
            }
            else skipped++;
        }
        catch (...) { skipped++; }
    }
    file.close();

    cout << "Зчитано IMU: " << imuCount << " | GPS: " << gpsCount << "\n\n";
    if (data.empty()) return 0;

    FlightMetrics fm(data);
    fm.calculateAllMetrics();

    cout << fixed << setprecision(3);
    cout << "=== РЕЗУЛЬТАТИ АНАЛІЗУ ===\n";
    cout << "Тривалість польоту            : " << fm.getFlightDuration() << " сек\n";
    cout << "Макс. горизонтальна швидкість : " << fm.getMaxHorizontalSpeed() << " м/с\n";
    cout << "Макс. вертикальна швидкість   : " << fm.getMaxVerticalSpeed() << " м/с\n";
    cout << "Макс. прискорення             : " << fm.getMaxAcceleration() << " м/с²\n";
    cout << "Макс. набір висоти (GPS)      : " << fm.getMaxAltitudeGain() << " м\n";
    cout << "Загальна дистанція (GPS)      : " << fm.getTotalDistance() << " м\n\n";

    // Зберігаємо файл для Python/Plotly
    fm.exportFor3D(out3DPath);

    return 0;
}