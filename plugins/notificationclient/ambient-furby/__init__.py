# -*- coding: utf-8 -*-
from datetime import datetime
from naomi import app_utils
from naomi import plugin
from naomi import furby_output
import random


# The Notification Client Plugin contains a method called
# "gather()" that runs every 30 seconds. If the plugin
# does not have a gather() method at the end of the __init__
# method, then it will not be added to the notifier and
# will not run again until Naomi is restarted.
# The base notification client has the following properties:
#   self._mic - the current microphone
#   self._brain - the current brain
#   self.gettext - the current translator
class MyNotificationClient(plugin.NotificationClientPlugin):
    # The gather function is fired every 30 seconds
    def gather(self, last_date):
               
        # get current time
        now = datetime.now(tz=app_utils.get_timezone())
        today_day_starts = now.replace(hour=8, minute=0, second=0, microsecond=0)
        today_day_ends = now.replace(hour=23, minute=0, second=0, microsecond=0)
       
        # if it's night-time, do nothing
        # TODO: or we've told Jasper to go to sleep
        # TODO: ask Jasper to change the time he goes to sleep and wakes up
        # TODO: create a speech handler plugin to control these settings
        # e.g. "Jasper go to sleep", "Jasper wake up", "Jasper go to sleep at 8pm", "Jasper wake up at 7am"

        if not(now > today_day_starts and now < today_day_ends):
            return

        # it's day-time, there is a 1 in 3 chance of some random bantz
        x = random.randint(1,3)
        print("Random number: ", x)

        if x != 1:            
            return   
        
        behaviour = random.randint(1,5)
        self.perform_behaviour(behaviour)

        return datetime.now(tz=app_utils.get_timezone())
        

    def perform_behaviour(self, behaviour):

            if behaviour == 1:
                self._mic.say("I need a wee")
                self._mic.furby_out.go_to_pose(furby_output.Pose.Excited)
            elif behaviour == 2:
                self._mic.say("Would anyone like some toast, or maybe a crumpet?")
                self._mic.furby_out.go_to_pose(furby_output.Pose.Awake)
            elif behaviour == 3:
                self._mic.say("Would anybody like to talk to me? I'm an excellent conversationalist.")
            elif behaviour == 4:
                self._mic.say("Shall we go to the pub? I could murder a beer. Maybe a bag of pretzels too.")
            elif behaviour == 5:
                self._mic.say("I just don't know what to do with myself")
            elif behaviour == 6:
                self._mic.say("Time for a quick forty winks")
                self._mic.furby_out.go_to_pose(furby_output.Pose.Asleep)