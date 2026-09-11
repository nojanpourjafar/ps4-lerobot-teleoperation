# rerun lerobot calibration, sweep every joint all the way to both stops
import lerobot.robots.so_follower as so

r = so.SOFollower(so.SOFollowerRobotConfig(port="/dev/tty.usbmodem5B3D0412591", id="my_awesome_follower_arm"))
r.connect(calibrate=False)
r.bus.disable_torque()
print("torque off, arm should move freely now")
r.calibrate()
r.disconnect()
