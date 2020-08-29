#!/usr/bin/env python3
import evdev
import ev3dev.auto as ev3
import threading
import sys

connection_done = 'False'
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    print(device)
    if device.name == 'Microsoft X-Box 360 pad':
        obj_of_gamep = device.fn
        print('Connection done!')
        connection_done = True
        break

if not connection_done:
    sys.exit('Gamepad was not found')

gamepad = evdev.InputDevice(obj_of_gamep)

def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(32767,-32767),(-100,100))


speed_a = 0
speed_d = 0
running = True

class MotorThread(threading.Thread):
    def __init__(self):
        self.motor_a = ev3.LargeMotor(ev3.OUTPUT_A)
        self.motor_d = ev3.LargeMotor(ev3.OUTPUT_D)
        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        while running:
            self.motor_a.run_direct(duty_cycle_sp=speed_a)
            self.motor_d.run_direct(duty_cycle_sp=speed_d)

        self.motor_a.stop()
        self.motor_d.stop()

motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()

for event in gamepad.read_loop():   
    if event.type == 3:             
        if event.code == 1:         
            speed_a = scale_stick(event.value)
    if event.type == 3:             
        if event.code == 4:         
            speed_d = scale_stick(event.value)

    if event.type == 1 and event.code == 307 and event.value == 1:
        print("X button is pressed. Stopping.")
        running = False
        break