#!/usr/bin/env python3
"""Connect to the SO-100 follower arm and read joint positions."""

import time
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"

# Find config + robot classes in this lerobot version
cfg_cls = getattr(so, "SO100FollowerConfig", None) or getattr(so, "SOFollowerRobotConfig", None)
bot_cls = getattr(so, "SO100Follower", None) or getattr(so, "SOFollower", None)

if cfg_cls is None or bot_cls is None:
    print("Couldn't find classes. Available in so_follower:")
    print([n for n in dir(so) if not n.startswith("_")])
    exit(1)

print(f"Using {cfg_cls.__name__} / {bot_cls.__name__}")
print(f"Port: {PORT}   ID: {ROBOT_ID}\n")

config = cfg_cls(port=PORT, id=ROBOT_ID)
robot = bot_cls(config)

print("Connecting (calibrate=False, using saved calibration)...")
robot.connect(calibrate=False)
print("✅ Connected\n")

for i in range(5):
    obs = robot.get_observation()
    pos = {k: round(v, 1) for k, v in obs.items() if k.endswith(".pos")}
    print(f"Read {i+1}: {pos}")
    time.sleep(0.2)

robot.disconnect()
print("\n✅ Disconnected cleanly")
