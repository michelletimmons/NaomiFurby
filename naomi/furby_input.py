
import pigpio           # http://abyz.co.uk/rpi/pigpio/python.html
import os
from . import furby_output

class FurbyInput:
    def __init__(self, mic):

        global pi

        self.mic = mic

        # TODO: if we have to exit here, how should the caller respond?
        # 
        # 

        pi = pigpio.pi()
        if not pi.connected:
            exit(0)

        self.__tilt_setup()
        self.__tummy_setup()
        self.__back_setup()
        self.__shutdown_setup()

	    # note that we don't do anything with cbTilt, cbTummy etc
        # do we actually need them?
        cbTilt = pi.callback(9, pigpio.EITHER_EDGE, self.pigpio_tilt_detected)
        cbTummy = pi.callback(5, pigpio.FALLING_EDGE, self.pigpio_tummy_detected)
        cbBack = pi.callback(10, pigpio.RISING_EDGE, self.pigpio_back_detected) 
        cbShutdown = pi.callback(3, pigpio.RISING_EDGE, self.pigpio_shutdown_detected)

        print('Furby input: init complete')

    # -----------------------
    # setup functions
    # -----------------------

    def __tilt_setup(self):

        pi.set_mode(9, pigpio.INPUT)
        pi.set_pull_up_down(9, pigpio.PUD_UP)
        pi.set_glitch_filter(9, 300)

    def __tummy_setup(self):

        pi.set_mode(5, pigpio.INPUT)
        pi.set_pull_up_down(5, pigpio.PUD_UP)
        pi.set_glitch_filter(5, 300)

    def __back_setup(self):

        pi.set_mode(10, pigpio.INPUT)
        pi.set_pull_up_down(10, pigpio.PUD_UP)
        pi.set_glitch_filter(10, 300)

    def __shutdown_setup(self):

        pi.set_mode(3, pigpio.INPUT)
        pi.set_pull_up_down(3, pigpio.PUD_UP)
        pi.set_glitch_filter(3, 300)

    # ----------------
    # callbacks
    # ----------------

    # TODO: need to be careful here as Naomi is picking up this speech as input
    # how does it normally filter this out?

    # TODO: Once one of these is triggered, it should not trigger again until the speech is finished

    def pigpio_tilt_detected(self, gpio, level, tick):

        print('Furby input: tilted')
        self.mic.say("Ooooh I'm feeling dizzy!")

    def pigpio_tummy_detected(self, gpio, level, tick):

        print('Furby input: tummy stroked')
        self.mic.say("Ooh, that's nice. Please can I have a cuddle?")

    def pigpio_back_detected(self, gpio, level, tick):

        print('Furby input: back stroked')
        self.mic.say("Aaaaaaaaah.... that makes me sleepy. I think I'll have a nap.")
        self.mic.furby_out.go_to_pose(furby_output.Pose.Asleep)

    def pigpio_shutdown_detected(self, gpio, level, tick):

        print('Furby input: shutdown triggered')
        self.mic.say("Daisy daisy, give me your answer do")
        self.mic.furby_out.go_to_pose(furby_output.Pose.Asleep)
        os.system("sudo shutdown -h now")
