import cv2
from djitellopy import TelloSwarm

swarm = TelloSwarm.fromIps([
    "192.168.0.182"
])

def script(index, tello):
    tello.streamon()
    frame_read = tello.get_frame_read()
    
    cv2.imwrite(f"picture{index}.png", frame_read.frame)
    

swarm.connect()
warm.takeoff()

swarm.parallel(script)

swarm.land()
swarm.end()

