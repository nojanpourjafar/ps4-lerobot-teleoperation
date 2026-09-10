# step shoulder_lift / elbow_flex / wrist_flex +-8 deg and see if they actually go
import time
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"
STEP = 8.0

cfg = so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID, max_relative_target=10.0)
robot = so.SOFollower(cfg)
robot.connect(calibrate=False)
rest = {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}

def hold(action, secs=1.0):
    for _ in range(int(secs * 30)):
        robot.send_action(action)
        time.sleep(1/30)

for joint in ["shoulder_lift.pos", "elbow_flex.pos", "wrist_flex.pos"]:
    for sign in (1, -1):
        target = dict(rest)
        target[joint] += sign * STEP
        hold(target)
        moved = robot.get_observation()[joint] - rest[joint]
        status = "ok" if abs(moved - sign * STEP) < 3 else "FAIL"
        print(f"{status:4s} {joint:18s} cmd {sign*STEP:+.0f}  got {moved:+.1f}")
        hold(rest)

robot.disconnect()
