import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("no controller found, plug it in over usb")
    exit(1)

js = pygame.joystick.Joystick(0)
js.init()
print(js.get_name(), "axes:", js.get_numaxes(), "buttons:", js.get_numbuttons())

# ds4 on mac reports the dpad as buttons 11-14, not a hat
start = time.time()
while time.time() - start < 10:
    for e in pygame.event.get():
        if e.type == pygame.JOYAXISMOTION and abs(e.value) > 0.1:
            print(f"axis {e.axis} {e.value:+.2f}")
        elif e.type == pygame.JOYBUTTONDOWN:
            print(f"button {e.button}")
    time.sleep(0.01)
