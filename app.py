import logging
import time

import streamlit as st

from multiprocessing.pool import ThreadPool

from djitellopy import Tello, TelloException


drones_ip = [
    '192.168.0.120',
    '192.168.0.121',
    '192.168.0.122',
    '192.168.0.123',
    '192.168.0.124'
]

drones: list[Tello]


def calculate_ports(ip):
    "Первый - для STATE_UDP_PORT, второй - VS_UDP_PORT"
    id = int(ip.split('.')[-1])
    return str(9000 + id * 10), str(11111 + id * 10)


def connect_drone(drone_index, drone_ip):

    # возможно не нужно, по идее должно предотвратить конфликт на 8890 порте
    time.sleep(drone_index / 200)

    try:
        state_port, vs_port = calculate_ports(drone_ip)
        drone = Tello(host=drone_ip, vs_udp=vs_port)
        drone.LOGGER.setLevel(logging.WARN)
        drone.connect()
        drone.set_network_ports(state_port, vs_port)
        drone.streamon()
    except TelloException:
        drone = None
        print(f"{drone_ip}: Failed to connect to tello.")
    return drone


@st.cache_data
def connect_all(ips):
    with ThreadPool(len(ips)) as pool:
        return list(pool.starmap(connect_drone, enumerate(ips)))


drones = connect_all(drones_ip)


def page(index):
    st.header(drones_ip[index])
    frame_window = st.image([])
    while True:
        frame_window.image(drones[index].get_frame_read().frame)


with st.sidebar:
    st.header('Все дроны: ')

    for index, drone in enumerate(drones):

        with st.expander(f"Дрон №{index} ({drones_ip[index]})"):
            column_info, column_camera = st.columns(2)

            info = f"| Статус | {'Подключен' if drone else 'Отсоединен'} |\n" \
                   f"|--------|------------------------------------------|\n" \
                   f"| IP     | {drones_ip[index]}                       |\n" \

            if drone:
                info += f"| 🔋 Батарея | {drone.get_battery()}% |\n"

            with column_info:
                st.write(info)

            with column_camera:
                if drone:
                    st.image(drones[index].get_frame_read().frame())

                    st.button("Отслеживать", key=f"drone-camera-{index}", on_click=page,
                              args=(index,), disabled=(drone is None))
