
from enum import Enum 
from enum import IntEnum
import pigpio           # http://abyz.co.uk/rpi/pigpio/python.html
import time
import random
import math
import threading

class Direction(IntEnum):
    Forward = 1
    Backward = -1

class Pose(Enum):
    Asleep = 1
    Awake = 2
    Neutral = 3
    Excited = 4

class Movement(Enum):
    Talk = 1
    Dance = 2


class FurbyOutput:

    def __init__(self):

        global pi

        # TODO: if we have to exit here, how should the caller respond?
        # 
        # 

        pi = pigpio.pi()
        if not pi.connected:
            exit(0)

        self.__camhome_setup()
        self.__phototrans_setup()
        self.__led_setup()
        self.__motor_furby_setup()
        self.__motor_wings_setup()

        self.currentPulse = 999
        self.targetPulse = 0
        self.targetReached = False
        self.direction = Direction.Forward

        # note that we don't do anything with cbCamHome, cbPulse etc
        # do we actually need them?
        cbCamHome = pi.callback(26, pigpio.RISING_EDGE, self.pigpio_camhome_detected)
        cbPulse = pi.callback(16, pigpio.RISING_EDGE, self.pigpio_pulse_detected)

        self.led_on()
        self.init_pulse_counter()

        print('Furby output: init complete')

    def	init_pulse_counter(self):

        targetPulse = 0
  
        self.motor_furby_on()

        try:
            while not self.targetReached:
                pass
        except KeyboardInterrupt:
             print('init_pulse_counter interrupted')
    
        self.motor_furby_off()

    # -----------------------
    # setup functions
    # -----------------------

    def __camhome_setup(self):

        pi.set_mode(26, pigpio.INPUT)
        pi.set_pull_up_down(26, pigpio.PUD_UP)
        pi.set_glitch_filter(26, 300)

    def __phototrans_setup(self):

        pi.set_mode(16, pigpio.INPUT)
        pi.set_pull_up_down(16, pigpio.PUD_OFF)
        pi.set_glitch_filter(16, 2)

    def __led_setup(self):

        pi.set_mode(6, pigpio.OUTPUT)

    def __motor_furby_setup(self):

        pi.set_mode(17, pigpio.OUTPUT)
        pi.set_mode(27, pigpio.OUTPUT)
        pi.set_mode(22, pigpio.OUTPUT)

    def __motor_wings_setup(self):

        pi.set_mode(23, pigpio.OUTPUT)        # enable
        pi.set_mode(24, pigpio.OUTPUT)        # backward
        pi.set_mode(25, pigpio.OUTPUT)        # forward

    # -----------------------
    # motors on/off
    # -----------------------

    def motor_wings_on(self):

        # is this needed?
        # global pi

        pi.write(24,0)
        pi.write(25,1)
        pi.write(23,1)

    def motor_wings_off(self):
 
        # is this needed?
        # global pi

        pi.write(24,0)
        pi.write(25,0)
        pi.write(23,0)

    def motor_furby_on(self):
      
        if self.direction == Direction.Forward:
            pi.write(17,0)
            pi.write(27,1)

        if self.direction == Direction.Backward:
            pi.write(17,1)
            pi.write(27,0)

        # set this pin low to switch on motor
        pi.write(22,0)

    def motor_furby_off(self):
    
        pi.write(17,0)
        pi.write(27,0)
        pi.write(22,1)

    # ----------------
    # led on/off
    # ----------------

    def led_on(self):

        pi.write(6,1)

    def led_off(self):

        pi.write(6,0)

    # ----------------
    # callbacks
    # ----------------

    def pigpio_camhome_detected(self, gpio, level, tick):

        # print('-- cam home')

        if self.direction == Direction.Forward:
            self.currentPulse = 0
        else:
	        self.currentPulse = 208

        if self.currentPulse == self.targetPulse:
            self.targetReached = True

        # print '-- cam', currentPulse, targetPulse, targetReached 

    def pigpio_pulse_detected(self, gpio, level, tick):

        if self.currentPulse != 999:
            self.currentPulse += self.direction

        if self.currentPulse == self.targetPulse:
            self.targetReached = True

        # print('- pulse', currentPulse, targetPulse, targetReached)

    # ----------------
    # positioning
    # ----------------

    def go_to_pulse(self, pulse):   

        if self.currentPulse == 999:
           raise ValueError('Pulse counter has not been initialised. You must call initPulseCounter() before trying to move to a specific pulse')

        self.targetPulse = pulse
        self.targetReached = False

        # print('currentPulse = ', self.currentPulse, 'targetPulse = ', self.targetPulse )

        # which direction will get us there quickest?
        self.direction, overshoot = self.calculate_direction_and_overshoot(self.currentPulse, self.targetPulse)

        # print self.direction, 'expected overshoot', overshoot

	    # allow for overshoot, which will depend on the distance we're about to travel 
        if self.direction == Direction.Forward:
            self.targetPulse -= overshoot
            if self.targetPulse < 0:
                self.targetPulse += 208
        else:
            self.targetPulse += overshoot
            if self.targetPulse > 208:
                self.targetPulse -= 208	

        # print 'adjusted targetPulse', self.targetPulse

        self.motor_furby_on()
    
        try:
            while not self.targetReached:
                pass   
        except KeyboardInterrupt:
            print('go_to_pulse interrupted')

        self.motor_furby_off()

    def calculate_direction_and_overshoot(self, currentPulse, targetPulse):

        forwardPulses = 0
        backwardPulses = 0
        overshoot = 0
        directionToUse = Direction.Forward

        if targetPulse > currentPulse:
            backwardPulses = (208 - targetPulse) + currentPulse
            forwardPulses = targetPulse - currentPulse

        elif targetPulse < currentPulse:
            backwardPulses = currentPulse - targetPulse
            forwardPulses = (208 - currentPulse) + targetPulse

        # print 'current pulse ', currentPulse, 'targetPulse ', targetPulse, 'forwardPulses ', forwardPulses, 'backwardPulses ', backwardPulses

	    # I got the overshoot equation by creating sample data, plugging it into an Excel scatter chart, and creating a trend line

        if backwardPulses < forwardPulses:
            overshoot = int((math.log(backwardPulses) * 8.8) - 11.7)
            directionToUse = Direction.Backward

        elif forwardPulses < backwardPulses:
            overshoot = int((math.log(forwardPulses) * 8.8) - 11.7)
            directionToUse = Direction.Forward

        if overshoot < 0:
            overshoot = 0

        return directionToUse, overshoot

    def go_to_pose(self, pose):

        go_to_pulse(get_pose_start_pulse(pose))

    def get_pose_start_pulse(self, pose):

        switcher = {
	                Pose.Neutral : 0,
                    Pose.Excited : 26,
                    Pose.Asleep : 104, 
                    Pose.Awake : 182
        }
        return switcher.get(pose,"Invalid pose")

    # ----------------
    # movement
    # ----------------

    def get_movement_start_pulse(self, movement):
        switcher = {
                    Movement.Talk : 170, 
                    Movement.Dance : 60
        }
        return switcher.get(movement,"Invalid movement")

    def get_movement_end_pulse(self, movement):
        switcher = {
                    Movement.Talk : 35, 
                    Movement.Dance : 140
        }
        return switcher.get(movement,"Invalid movement")

    def do_movement(self, movement):   
    
        # get the movement definition
        startPulse = self.get_movement_start_pulse(movement)
        endPulse = self.get_movement_end_pulse(movement)

        # print 'pulsing between ', startPulse, ' and ', endPulse

        # connect to the main thread, which will tell us when to stop moving
        t = threading.currentThread()

        try:
            while getattr(t, "keep_moving", True):
                self.go_to_pulse(startPulse)
                self.go_to_pulse(endPulse)
        except KeyboardInterrupt:
            print('do_movement interrupted')

    # ----------------------------------------------------------------
    # functions for creating overshoot datapoints
    # not required for day-to-day Naomi use
    # ----------------------------------------------------------------

    def create_overshoot_data():

        # I used this output to create an Excel scatter chart of distance vs overshoot, 
        # then drew an average overshoot trend line on the graph
	    # I think this code is overcomplicated re: handling the break at 208 pulses, but it seems to work

        i = 1;
        self.go_to_pose(Pose.Neutral)
        time.sleep(2)
        print('start', 'target', 'end', 'direction', 'distance', 'overshoot')

        while i < 200:
          
		    # d only needs to be a max of 104 (half a cycle) because we always choose the shortest distance
            d = random.randint(1,104)
            t = self.currentPulse + d

            if t > 208:
                t -= 208
        
            self.test_overshoot(t)
            i += 1

    def test_overshoot(self, paramTarget):

        tStart = self.currentPulse
        tTarget = paramTarget

        self.go_to_pulse(paramTarget)
        time.sleep(2)
    
        tDirection = self.direction
        tEnd = self.currentPulse

        tDistance = tTarget-tStart
        tOvershoot =  tEnd-tTarget
        tActualDistance = tEnd-tStart

        if tDirection == Direction.Forward:
            if tDistance < 0:
                tDistance += 208	
            if tOvershoot < 0:
                tOvershoot += 208	
            if tActualDistance < 0:
                tActualDistance += 208			
        else:
            if tDistance > 208:
    	        tDistance -= 208
            if tOvershoot > 208:
                tOvershoot -= 208
            if tActualDistance > 208:
               tActualDistance -= 208

        print (tStart, tTarget, tEnd, tDirection, tActualDistance, tOvershoot)