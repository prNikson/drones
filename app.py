import logging
import time

import streamlit as st

from multiprocessing.pool import ThreadPool

from djitellopy import Tello, TelloException

state = st.session_state

if 'drone_ips' not in state:
    state.drone_ips = [
    '192.168.0.176',
    '192.168.0.185',
    #'192.168.0.122',
    #'192.168.0.123',
    #'192.168.0.124'
]

if 'drones' not in state:
    state.drones: list[Tello]

def calculate_ports(ip):
    "Первый - для STATE_UDP_PORT, второй - VS_UDP_PORT"
    id = int(ip.split('.')[-1])
    return 9000 + id * 10, 11111 + id * 10

def reconnect_drone(index):
    try:
        state.drones[index].end()
    except AttributeError:
        pass
    except TelloException:
        pass
    state.drones[index] = connect_drone(index, state.drone_ips[index])


def connect_drone(drone_index, drone_ip):

    # возможно не нужно, по идее должно предотвратить конфликт на 8890 порте
    time.sleep(drone_index / 200)

    try:
        state_port, vs_port = calculate_ports(drone_ip)
        drone = Tello(host=drone_ip, vs_udp=vs_port)
        drone.LOGGER.setLevel(logging.WARN)
        drone.connect()
        if drone.query_sdk_version() < "30":
            print(f"Tello on {drone_ip} is not updated!")
            raise TelloException()
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


state.drones = connect_all(state.drone_ips)

def drone_script():
    for drone in state.drones:
        if drone:
            drone.takeoff()
            drone.land()

def page(index):
    st.header(state.drone_ips[index])
    frame_window = st.image([])
    st.button("Запустить сценарий", on_click=drone_script)
    while True:
        frame_window.image(state.drones[index].get_frame_read().frame)


with st.sidebar:
    st.header('Все дроны: ')

    for index, drone in enumerate(state.drones):

        with st.expander(f"Дрон №{index} ({state.drone_ips[index]})"):
            column_info, column_camera = st.columns(2)

            info = f"| Статус | {'Подключен' if drone else 'Отсоединен'} |\n" \
                   f"|--------|------------------------------------------|\n" \
                   f"| IP     | {state.drone_ips[index]}                 |\n" \

            if drone:
                info += f"| 🔋 Батарея | {drone.get_battery()}% |\n"

            with column_info:
                st.write(info)

            with column_camera:
                st.button("🔄 Обновить", key=f"drone-reconnect-{index}", on_click=reconnect_drone, args=(index,))
                
                if drone:
                    st.image(state.drones[index].get_frame_read().frame)

                    st.button("Отслеживать", key=f"drone-camera-{index}", on_click=page,
                              args=(index,))
                
