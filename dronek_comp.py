from dronekit import connect
import time
import maestro

# Threshold
ANGLE_THRE = 10

conn = connect('tcp:127.0.0.1:5760', wait_ready=True)
s = maestro.Controller("/dev/serial/by-id/usb-Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_Controller_00297468-if00")

class status:
    target_bearing = 0
    xtrack_error = 0
    heading = 0
    throttle = 0
    ch1 = 0
    ch3 = 0
    
def nav_callback(self, name, msg):
    status.target_bearing = msg.target_bearing
    status.xtrack_error = msg.xtrack_error

def vfr_callback(self, name, msg):
    status.heading = msg.heading
    status.throttle = msg.throttle

def rc_callback(self, name, msg):
    status.ch1 = msg.chan1_raw
    status.ch3 = msg.chan3_raw

conn.add_message_listener('NAV_CONTROLLER_OUTPUT', nav_callback)
conn.add_message_listener('VFR_HUD', vfr_callback)
conn.add_message_listener('RC_CHANNELS', rc_callback)

while True:
    #print "bea", status.target_bearing
    #print "xte", status.xtrack_error
    #print "hea", status.heading
    #print "thr", status.throttle
    #print status.ch1
    #print status.ch3

    #print conn.mode.name
    #print conn.armed
    diff = status.target_bearing -status.heading

    if conn.armed == False or status.throttle == 0:
        s.setTarget(0,8000)
        s.setTarget(1,8000)
        continue

    # manual
    if conn.mode.name == "MANUAL" and conn.armed == True:
        if status.ch3 < 1700:
            s.setTarget(0,8000)
            s.setTarget(1,8000)
        else:
            if status.ch1 < 1400:
                s.setTarget(0,6000)
                s.setTarget(1,8000)
            elif status.ch1 > 1600:
                s.setTarget(0,8000)
                s.setTarget(1,6000)

    # auto
    if diff > 180:
        diff = diff -360
    elif diff < -180:
        diff = diff +360 
    print "diff", diff

    if conn.mode.name == "AUTO" and conn.armed == True:
        if diff < - ANGLE_THRE:
            self.s.setTarget(0,6000)
            self.s.setTarget(1,8000)
        elif diff > ANGLE_THRE:
            self.s.setTarget(0,8000)
            self.s.setTarget(1,6000)
        else:
            self.s.setTarget(0,8000)
            self.s.setTarget(1,8000)                    

    time.sleep(0.01)
