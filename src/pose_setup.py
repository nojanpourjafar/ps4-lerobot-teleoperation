# torque off, move the arm by hand until every joint is inside its limits, then ctrl-c
import time
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"
MARGIN = 150  # ticks of clearance from each limit (~13 deg)

r = so.SOFollower(so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID))
r.connect(calibrate=False)
bus = r.bus
bus.disable_torque()
print("torque off, move the arm by hand. ctrl-c when everything says ok\n")

lims = {n: (bus.read("Min_Position_Limit", n, normalize=False),
            bus.read("Max_Position_Limit", n, normalize=False)) for n in bus.motors}
try:
    while True:
        line = []
        for n in bus.motors:
            p = bus.read("Present_Position", n, normalize=False)
            lo, hi = lims[n]
            ok = lo + MARGIN <= p <= hi - MARGIN
            line.append(f"{n[:9]:9s} {p:4d} {'ok ' if ok else 'BAD'}")
        print("\r" + "  ".join(line), end="")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\ntorque back on")
    bus.enable_torque()
    time.sleep(0.5)
    r.disconnect()
