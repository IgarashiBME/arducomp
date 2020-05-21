from pymavlink import mavutil
import schedule
import time
import maestro

# Threshold
ANGLE_THRE = 10

class companion():
    def __init__(self):
        self.conn = mavutil.mavlink_connection('tcp:localhost:5760')
        self.conn.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (self.conn.target_system, self.conn.target_system))

        self.s = maestro.Controller("/dev/serial/by-id/usb-Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_Controller_00297468-if00")

        schedule.every(0.01).seconds.do(self.job1)
        schedule.every(0.01).seconds.do(self.job2)
        
    def job1(self):
        msg = self.conn.recv_match(type='NAV_CONTROLLER_OUTPUT',blocking=True)
    
        try:
            self.bearing = msg.nav_bearing
            self.target_bearing = msg.target_bearing
            #print "nav:", self.bearing, self.target_bearing
        except Exception as e:
            pass

    def job2(self):
        vfr = self.conn.recv_match(type='VFR_HUD',blocking=True)

        try:
            self.heading = vfr.heading
            self.throttle = vfr.throttle
            #print "vfr:", self.heading, self.throttle
        except Exception as e:
            pass

    def loop(self):
        while True:
            schedule.run_pending()

            try:
                self.heading
                self.throttle
                self.bearing
                self.target_bearing
                #print "nav:", self.bearing, self.target_bearing
                #print "vfr:", self.heading
                #print "thr:", self.throttle

                diff = self.target_bearing -self.heading
                if diff < - ANGLE_THRE:
                    self.s.setTarget(0,6000)
                    self.s.setTarget(1,8000)
                elif diff > ANGLE_THRE:
                    self.s.setTarget(0,8000)
                    self.s.setTarget(1,6000)
                else:
                    self.s.setTarget(0,6000)
                    self.s.setTarget(1,6000)                    
                print diff
            except Exception as e:
                pass
            time.sleep(0.01)

if __name__ == '__main__':
    c = companion()
    c.loop()
