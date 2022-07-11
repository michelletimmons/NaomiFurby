# ----------------------------------------------------------------
# import libraries
# ----------------------------------------------------------------

import pigpio           # http://abyz.co.uk/rpi/pigpio/python.html
import os

class FurbyInput:
    def __init__(self):

        global pi

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

    def pigpio_tilt_detected(self, gpio, level, tick):

        print('Furby input: tilted')

    def pigpio_tummy_detected(self, gpio, level, tick):

        print('Furby input: tummy stroked')

    def pigpio_back_detected(self, gpio, level, tick):

        print('Furby input: back stroked')

    def pigpio_shutdown_detected(self, gpio, level, tick):

        print('Furby input: shutdown triggered')
        os.system("sudo shutdown -h now")
