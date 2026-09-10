#!/usr/bin/env python3
"""PS4 -> SO-100 teleoperation. Rate control on sticks, absolute gripper on R2."""

import time, csv, math
from datetime import datetime
import pygame
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"
LOOP_HZ = 30
DEADZONE = 0.09
WINDOW = 30.0                 # deg each side of rest, per joint
MAX_STEP = 10.0               # lerobot per-command cap
SPEED = {                     # deg/s at full stick
    "shoulder_pan.pos": 40, "shoulder_lift.pos": 30, "elbow_flex.pos": 30,
    "wrist_flex.pos": 40, "wrist_roll.pos": 60,
}
GRIP_WINDOW = 15.0

AX_LX, AX_LY, AX_RX, AX_RY, AX_R2 = 0, 1, 2, 3, 5
BTN_L1, BTN_R1, BTN_OPTIONS = 9, 10, 6

def shaped(v):
    """Deadzone + rescale so output is 0 inside DEADZONE and reaches ±1 at full deflection."""
    a = abs(v)
    if a < DEADZONE:
        return 0.0
    return math.copysign((a - DEADZONE) / (1 - DEADZONE), v)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

pygame.init(); pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("No controller"); exit(1)
js = pygame.joystick.Joystick(0); js.init()

cfg = so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID, max_relative_target=MAX_STEP)
robot = so.SOFollower(cfg)
robot.connect(calibrate=False)

rest = {k: v for k, v in robot.get_observation().items() if k.endswith(".pos")}
target = dict(rest)
lo = {k: v - WINDOW for k, v in rest.items()}
hi = {k: v + WINDOW for k, v in rest.items()}
g0 = rest["gripper.pos"]

print("Rest:", {k: round(v, 1) for k, v in rest.items()})
print("Sticks move joints, R2 = gripper, Options = quit\n")

log = []
dt = 1 / LOOP_HZ
try:
    while True:
        t0 = time.perf_counter()
        pygame.event.pump()
        if js.get_button(BTN_OPTIONS):
            break

        # rate control: target += stick * speed * dt
        cmd = {
            "shoulder_pan.pos":  shaped(js.get_axis(AX_LX)),
            "shoulder_lift.pos": shaped(js.get_axis(AX_LY)),
            "elbow_flex.pos":    shaped(js.get_axis(AX_RY)),
            "wrist_roll.pos":    shaped(js.get_axis(AX_RX)),
            "wrist_flex.pos":    float(js.get_button(BTN_R1)) - float(js.get_button(BTN_L1)),
        }
        for k, v in cmd.items():
            target[k] = clamp(target[k] + v * SPEED[k] * dt, lo[k], hi[k])

        r2 = (js.get_axis(AX_R2) + 1) / 2
        target["gripper.pos"] = g0 - GRIP_WINDOW + r2 * 2 * GRIP_WINDOW

        t_send = time.perf_counter()
        robot.send_action(target)
        t_sent = time.perf_counter()
        obs = robot.get_observation()
        t_read = time.perf_counter()

        err = max(abs(obs[k] - target[k]) for k in target)
        log.append([t0, (t_sent - t_send) * 1e3, (t_read - t_sent) * 1e3, err])
        print(f"\rsend {log[-1][1]:5.1f}ms  read {log[-1][2]:5.1f}ms  max err {err:5.1f}°", end="")

        time.sleep(max(0, dt - (time.perf_counter() - t0)))
except KeyboardInterrupt:
    pass
finally:
    print("\nReturning to rest...")
    for _ in range(int(2 * LOOP_HZ)):        # ease back over 2 s
        for k in target:
            target[k] += (rest[k] - target[k]) * 0.1
        robot.send_action(target); time.sleep(dt)
    robot.disconnect()
    fname = f"data/teleop_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(fname, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "send_ms", "read_ms", "max_err_deg"]); w.writerows(log)
    print(f"Logged {len(log)} loops to {fname}")
