import logging
import asyncio
import utils
import threading

import streamlit as st

from djitellopy import Tello, TelloException

state = st.session_state

if 'drone_ips' not in state:
    state.drone_ips = [
        '192.168.0.178'
        # '192.168.0.176',
        # '192.168.0.185',
        # '192.168.0.122',
        # '192.168.0.123',
        # '192.168.0.124'
    ]

if 'drones' not in state:
    state.drones: list[Tello]


async def connect_drone(drone_index, drone_ip):
    try:
        state_port, vs_port = utils.calculate_ports(drone_ip)
        drone = Tello(host=drone_ip, vs_udp=vs_port)
        drone.LOGGER.setLevel(logging.WARN)
        drone.connect()

        if drone.query_sdk_version() < "30":
            print(f"Tello on {drone_ip} is not updated!")
            raise TelloException()
        drone.set_network_ports(state_port, vs_port)
        drone.streamon()
        drone.set_video_bitrate(drone.BITRATE_2MBPS)
        drone.set_video_resolution(drone.RESOLUTION_720P)
        drone.set_video_fps(drone.FPS_15)
    except TelloException:
        drone = None
        print(f"{drone_ip}: Failed to connect to tello.")
    return drone


async def connect_all(ips):
    return list(
        await asyncio.gather(
            *(connect_drone(i, ip) for i, ip in enumerate(ips))
        )
    )


if 'connected' not in state:
    state.drones = asyncio.run(
        connect_all(state.drone_ips),
    )

state.connected = True


async def display_images(header_placeholder, video_placeholder):
    while True:
        await asyncio.sleep(1/30)
        try:
            header_placeholder.header(
                state.drone_ips[state.drone_camera_index])
            video_placeholder.image(
                state.drones[state.drone_camera_index].get_frame_read().frame)
        except AttributeError:
            pass
        except TelloException:
            pass
        except OSError:
            pass


async def main(header_placeholder, video_placeholder):
    _ = await asyncio.gather(
        display_images(header_placeholder, video_placeholder)
    )


def drone_script(state):
    for drone in state["drones"]:
        if not drone:
            continue
        drone.takeoff()
        drone.land()


def drone_script_runner():
    thread = threading.Thread(target=drone_script, args=(state,))
    st.runtime.scriptrunner.add_script_run_ctx(thread)
    thread.start()


header_placeholder = st.empty()
video_placeholder = st.empty()
st.button("Запустить сценарий",
          on_click=drone_script_runner)


with st.sidebar:
    a = st.header('Все дроны: ')

    for index, drone in enumerate(state.drones):

        with st.expander(f"Дрон №{index} ({state.drone_ips[index]})"):
            column_info, column_camera = st.columns([3, 2])

            info = f"| Статус | {'Подключен' if drone else 'Отсоединен'} |\n" \
                   f"|--------|------------------------------------------|\n" \
                   f"| IP     | {state.drone_ips[index]}                 |\n" \

            if drone:
                info += f"| 🔋 Батарея | {drone.get_battery()}% |\n"

            with column_info:
                st.write(info)

            with column_camera:
                if drone:
                    camera_drone_button = st.button(
                        "Отслеживать", key=f"drone-camera-{index}")
                    if camera_drone_button:
                        state.drone_camera_index = index

if state.connected:
    asyncio.run(
        main(header_placeholder, video_placeholder)
    )
