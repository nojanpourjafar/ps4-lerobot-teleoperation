#!/usr/bin/env python3
"""Measure resting stick drift. Don't touch the controller while this runs."""

import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found")
    exit(1)

js = pygame.joystick.Joystick(0)
js.init()

DURATION = 5
STICK_AXES = [0, 1, 2, 3]

print(f"Hands off the controller. Sampling for {DURATION}s...")
peak = {a: 0.0 for a in STICK_AXES}
samples = 0

start = time.time()
while time.time() - start < DURATION:
    pygame.event.pump()
    for a in STICK_AXES:
        v = abs(js.get_axis(a))
        if v > peak[a]:
            peak[a] = v
    samples += 1
    time.sleep(0.005)

names = {0: "Left X", 1: "Left Y", 2: "Right X", 3: "Right Y"}
print(f"\n{samples} samples\n")
for a in STICK_AXES:
    print(f"Axis {a} ({names[a]:8s}): peak drift = {peak[a]:.3f}")

worst = max(peak.values())
print(f"\nWorst-case drift: {worst:.3f}")
print(f"Suggested deadzone: {worst + 0.03:.2f}")
