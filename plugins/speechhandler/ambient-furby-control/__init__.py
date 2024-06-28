# -*- coding: utf-8 -*-
from naomi import plugin


# The speechhandler plugin represents something that Naomi does
# in response to a request from the user. This is often a spoken
# response, but can also be an action like turning on a light or
# sending an email. It is the functional equivalent of a skill on
# most other assistant platforms.
# For details about writing a speech handler, see:
# https://projectnaomi.com/dev/docs/developer/plugins/speechhandler_plugin.html
class AmbientFurbyControl(plugin.SpeechHandlerPlugin):
    # Intents describe how your plugin may be activated.
    # At the simplest level, just write all the things you think
    # someone might say if they wanted to activate your
    # plugin. Finally, supply a link to the handle method,
    # which Naomi will use when your intent is selected.
    def intents(self):
        return {
            'AmbientFurbyControlIntent': {
                'locale': {
                    'en-US': {
                        'keywords': {
                            'SleepKeyword': [
                                'sleep',
                                'forty winks',
                                'nap'
                            ],
                            'WakeKeyword': [
                                'wake',
                                'rise and shine'
                            ]
                        },
                        'templates': [                            
                            '{SleepKeyword}',
                            '{WakeKeyword}'
                        ]
                    }
                },
                'action': self.handle
            }
        }

    # The handle method is where you pick up after Naomi has
    # identified your intent as the one the user was attempting
    # to activate.
    def handle(self, intent, mic):
        # The intent parameter is a structure with information about
        # the user request. intent['input'] will hold the transcription
        # of the user's request.
        text = intent['input']
        # The mic parameter is a microphone object that you can
        # use to respond to the user.
        mic.say("You said, {}".format(text))