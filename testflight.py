from djitellopy import Tello, TelloSwarm
import cv2, math, time, sys
from multiprocessing.pool import ThreadPool

droneIps = [
    #"192.168.0.118",
    #"192.168.0.5",
    #"192.168.0.170"
]
tellos = []

for ip in droneIps:
    try:
        tello = Tello(ip)
        tello.connect()
        tellos.append(tello)
    except Exception:
        print(f"failed to connect to {ip}")

swarm = TelloSwarm(tellos)

def connect(index, tello):
    try:
        tello.connect()
    except Exception:
        swarm.tellos.pop(index)

swarm.parallel(connect)

def setup_video(index, tello):
    if tello.query_sdk_version() < "30":
        print(f"Drone #{index} doesn't support SDK 3 !!!")
        sys.exit()
    
    print(f"drone {index} battery: {tello.get_battery()}")

    tello.change_vs_udp(12000 + index * 10)

    tello.set_video_bitrate(Tello.BITRATE_1MBPS)
    tello.set_video_fps(tello.FPS_15)
    tello.set_video_resolution(Tello.RESOLUTION_480P)

    tello.streamon()

    tello.get_frame_read()

def close_video(index, tello):
    tello.streamoff()

def script1(index, tello):
    running = True
    def camera():
        while running:
            frame = tello.get_frame_read()
            cv2.imshow(f"drone {index}", cv2.cvtColor(frame.frame, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) == 27:
                running = False

    def logic():
        for i in range(5):
            tello.move_forward(30)
            tello.move_back(30)
    
    def keepalive():
        while running:
            time.sleep(10)
            tello.send_keepalive()
    
    with ThreadPool(3) as pool:
        pool.map(lambda func: func(), [
            camera,
            logic,
            #keepalive
        ])

swarm.parallel(setup_video)

time.sleep(1)

swarm.takeoff()

swarm.parallel(script1)

swarm.parallel(close_video)

swarm.land()
