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

// Структура для зберігання однієї точки даних (Твій оригінал)
struct FlightPoint {
    double timestamp = 0.0;
    double lat = 0.0, lon = 0.0, alt = 0.0;
    double spd = 0.0; 
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

    struct ENUPoint {
        double x; // East
        double y; // North
        double z; // Up
        double speed;
        double timestamp;
    };
    vector<ENUPoint> enuTrack;

public:
    FlightMetrics(const vector<FlightPoint>& data) : points(data) {}

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

        bool firstGPS = true;
        double lat0 = 0.0, lon0 = 0.0, alt0 = 0.0, time0 = 0.0;
        const double M_PER_DEG = 111320.0;
        const double ACCEL_THRESHOLD = 0.15;

        for (const auto& p : points) {
            if (p.hasGPS) {
                minAlt = min(minAlt, p.alt);
                maxAlt = max(maxAlt, p.alt);
                if (hasPrevGPS) {
                    totalDistance += haversine(prevLat, prevLon, p.lat, p.lon);
                }
                prevLat = p.lat; prevLon = p.lon; hasPrevGPS = true;

                if (firstGPS) {
                    lat0 = p.lat; lon0 = p.lon; alt0 = p.alt; time0 = p.timestamp;
                    firstGPS = false;
                }

                double t_sec = p.timestamp - time0;
                double y_coord = (p.lat - lat0) * M_PER_DEG;
                double x_coord = (p.lon - lon0) * M_PER_DEG * cos(lat0 * M_PI / 180.0);
                double z_coord = p.alt - alt0;

                enuTrack.push_back({ x_coord, y_coord, z_coord, p.spd, t_sec });
            }

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
                maxAcceleration = max(maxAcceleration, sqrt(curAx * curAx + curAy * curAy + curAz * curAz));
                prevAx = curAx; prevAy = curAy; prevAz = curAz;
                prevImuTime = p.timestamp;
                hasPrevIMU = true;
            }
        }
        if (minAlt < 1e9) maxAltitudeGain = maxAlt - minAlt;
    }

    void exportFor3D(const string& filepath) {
        ofstream out(filepath);
        if (!out.is_open()) return;
        out << "x,y,z,speed,time_sec\n" << fixed << setprecision(6);
        for (const auto& pt : enuTrack) {
            out << pt.x << "," << pt.y << "," << pt.z << "," << pt.speed << "," << pt.timestamp << "\n";
        }
        out.close();
    }

    // НОВА ФУНКЦІЯ (Додана до оригіналу для роботи ШІ)
    void saveReportForAI(const string& filepath) {
        ofstream out(filepath);
        if (!out.is_open()) return;
        out << fixed << setprecision(3);
        out << "РЕЗУЛЬТАТИ АНАЛІЗУ БПЛА\n";
        out << "Тривалість польоту            : " << flightDuration << " сек\n";
        out << "Макс. горизонтальна швидкість : " << maxHorizontalSpeed << " м/с\n";
        out << "Макс. вертикальна швидкість   : " << maxVerticalSpeed << " м/с\n";
        out << "Макс. прискорення             : " << maxAcceleration << " м/с²\n";
        out << "Макс. набір висоти (GPS)      : " << maxAltitudeGain << " м\n";
        out << "Загальна дистанція (GPS)      : " << totalDistance << " м\n";
        out.close();
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
        double a = sin(dPhi / 2) * sin(dPhi / 2) + cos(phi1) * cos(phi2) * sin(dLambda / 2) * sin(dLambda / 2);
        return R * 2 * atan2(sqrt(a), sqrt(1 - a));
    }
};

int main() {
    SetConsoleOutputCP(65001);

    string inputPath = "CVS_Files/result.csv";
    string out3DPath = "CVS_Files/clean_data.csv";
    string outAIPath = "CVS_Files/ai_input.txt"; // Шлях для ШІ

    ifstream file(inputPath);
    if (!file.is_open()) return 1;

    vector<FlightPoint> data;
    string line; getline(file, line);

    while (getline(file, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        vector<string> cols; string token;
        while (getline(ss, token, ',')) cols.push_back(token);

        if (cols.size() < 2) continue;
        FlightPoint p;
        p.timestamp = stod(cols[1]) / 1000000.0;

        if (cols[0] == "IMU" && cols.size() >= 9) {
            p.ax = stod(cols[6]); p.ay = stod(cols[7]); p.az = stod(col[8]);
            p.hasIMU = true; data.push_back(p);
        }
        else if (cols[0] == "GPS" && cols.size() >= 26) {
            p.lat = stod(cols[22]); p.lon = stod(cols[23]);
            p.alt = stod(cols[24]); p.spd = stod(cols[25]);
            p.hasGPS = true; data.push_back(p);
        }
    }
    file.close();

    FlightMetrics fm(data);
    fm.calculateAllMetrics();

    // ЗБЕРЕЖЕННЯ ФАЙЛІВ
    fm.exportFor3D(out3DPath);
    fm.saveReportForAI(outAIPath); // ТЕПЕР ФАЙЛ БУДЕ СТВОРЕНО

    return 0;
}