import streamlit as st
from djitellopy import Tello

drones_ip = ['192.168.0.120', '192.168.0.121',
             '192.168.0.122', '192.168.0.123', '192.168.0.124']
drones = list()


@st.cache_data
def connect(ip):
    drone = Tello(ip)
    drone.connect()
    drone.streamon()
    return drone


for ip in drones_ip:
    drones.append(connect(ip))


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
