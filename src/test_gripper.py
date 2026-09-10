# r2 opens/closes the gripper, everything else held at rest
import time
import pygame
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"
WINDOW = 15.0
HZ = 30

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()

cfg = so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID, max_relative_target=10.0)
robot = so.SOFollower(cfg)
robot.connect(calibrate=False)

rest = {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}
g0 = rest["gripper.pos"]
print(f"gripper rest {g0:.1f}, options to quit")

try:
    while True:
        t0 = time.perf_counter()
        pygame.event.pump()
        if js.get_button(6):
            break
        r2 = (js.get_axis(5) + 1) / 2
        action = dict(rest)
        action["gripper.pos"] = g0 - WINDOW + r2 * 2 * WINDOW
        robot.send_action(action)
        actual = robot.get_observation()["gripper.pos"]
        print(f"\rr2 {r2:.2f} target {action['gripper.pos']:.1f} actual {actual:.1f}", end="")
        time.sleep(max(0, 1/HZ - (time.perf_counter() - t0)))
except KeyboardInterrupt:
    pass
finally:
    robot.send_action(rest)
    time.sleep(0.5)
    robot.disconnect()
