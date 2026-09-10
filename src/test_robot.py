import time
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"

cfg = so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID)
robot = so.SOFollower(cfg)
robot.connect(calibrate=False)

for i in range(5):
    obs = robot.get_observation()
    print({k: round(v, 1) for k, v in obs.items() if k.endswith(".pos")})
    time.sleep(0.2)

robot.disconnect()
