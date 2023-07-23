import logging
import streamlit as st
from djitellopy import Tello, TelloException
from multiprocessing.pool import ThreadPool

drones_ip = ['192.168.0.120', '192.168.0.121',
             '192.168.0.122', '192.168.0.123', '192.168.0.124']
drones = list()


def calculate_ports(ip):
    "Первый - для STATE_UDP_PORT, второй - VS_UDP_PORT"
    id = int(ip.split('.')[-1])
    return str(9000 + id * 10), str(11111 + id * 10)


def connect_drone(ip):
    try:
        state, vs = calculate_ports(ip)
        drone = Tello(host=ip, vs_udp=vs)
        drone.LOGGER.setLevel(logging.WARN)
        drone.connect()
        drone.set_network_ports(state, vs)
        drone.streamon()
    except TelloException:
        drone = None
        print(f"{ip}: Failed to connect to tello.")
    return drone


@st.cache_data
def connect_all(ips):
    with ThreadPool(len(ips)) as pool:
        return list(pool.map(connect_drone, ips))


drones = connect_all(drones_ip)


def page(index):
    st.header(drones_ip[index])
    frame_window = st.image([])
    while True:
        frame_window.image(drones[index].get_frame_read().frame)


with st.sidebar:
    st.header('Все дроны: ')
    for index in range(len(drones_ip)):
        st.button(f"Drone {index+1}", on_click=page,
                  args=(index,), disabled=True)
