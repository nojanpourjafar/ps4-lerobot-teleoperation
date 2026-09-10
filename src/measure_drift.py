# leave the controller alone while this runs
import pygame
import time

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()

axes = [0, 1, 2, 3]  # triggers sit at -1 when released so skip them
peak = {a: 0.0 for a in axes}

start = time.time()
while time.time() - start < 5:
    pygame.event.pump()
    for a in axes:
        peak[a] = max(peak[a], abs(js.get_axis(a)))
    time.sleep(0.005)

for a in axes:
    print(f"axis {a}: {peak[a]:.3f}")
worst = max(peak.values())
print(f"worst {worst:.3f} -> deadzone {worst + 0.03:.2f}")
