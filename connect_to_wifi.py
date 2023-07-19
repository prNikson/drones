from djitellopy import Tello

# Сначала нужно законнектиться к дрону, потом запустить этот скрипт и подключаться к wifi.

WIFI_SSID = "Tenda_2436F0"
WIFI_PASSWORD = "12345678"

tello = Tello()

tello.connect()
tello.connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
