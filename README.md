# ps4 lerobot teleop

driving a LeRobot SO-100 arm with a PS4 controller.

## what this is

The normal way to teleoperate one of these arms is with a second "leader" arm, you move the leader by hand and the follower copies it. That works but it's two arms worth of hardware and it's awkward for anything other than mirroring. I had a DualShock 4 lying around and figured a controller made more sense for a lot of stuff, so this is a python script that reads the sticks and triggers and turns them into servo positions on the follower arm.

- left stick moves the base and shoulder
- right stick moves the elbow and wrist
- L2 / R2 open and close the gripper, and the controller rumbles when it's gripping something
- square sends the arm back to a home position
- options quits

It runs at 50 Hz over a wired usb connection and the delay between moving a stick and the arm moving is around 30ms, which feels basically instant.

## how it works

There's three things talking to each other.

**the controller** is plugged into the mac over usb. I read it with pygame's joystick module. I originally tried evdev because every tutorial uses it, then found out evdev is linux only and won't even install on a mac. pygame works fine on everything.

**the python script** is the middle bit. Every 20ms it:

1. reads the stick and trigger values (-1 to 1)
2. adds a deadzone so the arm doesn't drift when you're not touching anything
3. turns each axis into a small change in the target position for that joint, so holding the stick moves the arm at a steady speed instead of jumping
4. clamps every joint to safe limits so you can't drive it into itself
5. sends the new positions to the arm
6. reads back the gripper load and rumbles the controller if it's high

**the arm** is a chain of six Feetech servos (ids 1 to 6) on one serial bus. LeRobot's `SO100Follower` class handles the actual serial protocol, I just give it a dict of joint names to positions. It shows up on the mac as `/dev/tty.usbmodem` something.

## setup

I'm on an M-series mac using conda (miniforge). Should work on linux too but I haven't tried.

```
conda create -n teleop python=3.13
conda activate teleop
pip install lerobot pygame numpy
```

Plug the controller in over usb, not bluetooth, and check it's seen:

```
python src/test_controller.py
```

It should print axis values as you move the sticks. If it says no joystick found, unplug and replug the controller and make sure it's actually a data cable, some charging cables don't do data.

Find the arm's port:

```
ls /dev/tty.usb*
```

Then calibrate it once (this is the standard lerobot step, it moves each joint to its limits and saves the ranges):

```
lerobot-calibrate --robot.type=so100_follower --robot.port=/dev/tty.usbmodemXXXX --robot.id=my_follower
```

And run it:

```
python src/teleop.py --port /dev/tty.usbmodemXXXX
```

## things that went wrong

Putting these here because they cost me hours and I didn't find good answers online.

**evdev doesn't exist on mac.** Covered above. Use pygame.

**`python` vs `python3`.** I had conda's python 3.13 and a separate system python 3.10, and pip was installing into one while `python3` ran the other, so everything said `ModuleNotFoundError` even though it was installed. Fix was to always use `python` (the conda one) and set VS Code's interpreter to the conda env.

**the lerobot class names.** The config class is `SOFollowerRobotConfig`, not `SO101FollowerRobotConfig` like some older examples say, and the robot class is `SO100Follower` from `lerobot.robots.so_follower.so_follower`. The library got reorganized at some point and half the tutorials are wrong now.

**`ConnectionError: Failed to sync read 'Present_Position'`.** The arm calibrates fine, then the second the control loop starts it loses contact. In my case it turned out to be a mix of a bad usb cable and the servos not getting enough power. The arm needs its own power supply, it can't run off usb. Reseating every servo connector in the chain also helped.

**servo 5 dropping off the bus.** Same idea, a loose connector on the daisy chain means everything after that servo disappears. If ids 1 to 4 respond and 5 and 6 don't, check the cable between 4 and 5.

**overload error on servo 2.** The shoulder servo carries the most weight. If the arm is holding a position that fights gravity for too long the servo overheats and shuts down. Home position should be somewhere the arm can rest.

## data

Every run logs the joint positions to a csv in `data/` with a timestamp in the name. A few sample runs are in the repo. The plan is to use these as training data for a lerobot policy eventually, or at least replay them.

## what I'd do next

- replay a recorded csv back onto the arm
- add a speed toggle on one of the bumpers, right now it's one fixed sensitivity
- the wrist roll isn't mapped to anything yet

## layout

```
src/teleop.py             the main loop, run this
src/test_controller.py    prints controller input, use this first
src/test_robot.py         checks the arm responds on serial
src/test_joints.py        moves each joint a little to check ids and direction
src/test_gripper.py       gripper open/close + load reading
src/servo_diag.py         pings each servo and reports what's alive
src/calibrate.py          my wrapper around lerobot-calibrate
src/pose_setup.py         set and save the home pose
src/measure_drift.py      logs how far the arm drifts when holding still
data/                     recorded runs (csv)
hardware/                 notes on the arm, wiring, power
docs/                     stuff I wrote while figuring this out
```
