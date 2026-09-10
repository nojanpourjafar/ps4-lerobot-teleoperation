#!/usr/bin/env python3
"""Detect PS4 controller and print live inputs."""

import pygame
import time

pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()
print(f"Controllers found: {count}")

if count == 0:
    print("❌ No controller detected. Plug it in via USB (or pair via Bluetooth) and rerun.")
    exit(1)

js = pygame.joystick.Joystick(0)
js.init()
print(f"✅ Using: {js.get_name()}")
print(f"   Axes: {js.get_numaxes()}  Buttons: {js.get_numbuttons()}  Hats: {js.get_numhats()}")
print("\nMove sticks / press buttons for 10 seconds...\n")

start = time.time()
while time.time() - start < 10:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.1:
            print(f"Axis {event.axis}: {event.value:+.2f}")
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Button {event.button} pressed")
        elif event.type == pygame.JOYHATMOTION:
            print(f"D-pad: {event.value}")
    time.sleep(0.01)

print("\n✅ Controller test done")