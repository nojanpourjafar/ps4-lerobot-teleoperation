# dump servo registers to figure out why 2/3/4 won't move
import lerobot.robots.so_follower as so

PORT = "/dev/tty.usbmodem5B3D0412591"
ROBOT_ID = "my_awesome_follower_arm"

cfg = so.SOFollowerRobotConfig(port=PORT, id=ROBOT_ID)
robot = so.SOFollower(cfg)
robot.connect(calibrate=False)
bus = robot.bus

regs = ["Torque_Enable", "Present_Position", "Goal_Position", "Present_Load",
        "Present_Current", "Present_Temperature", "Present_Voltage",
        "Torque_Limit", "Max_Torque_Limit", "Protection_Current", "Status"]

for name in bus.motors:
    print(f"\n{name} (id {bus.motors[name].id})")
    for r in regs:
        try:
            v = bus.read(r, name, normalize=False)
            print(f"  {r:20s} {v}")
        except Exception as e:
            print(f"  {r:20s} -- {type(e).__name__}")

robot.disconnect()
