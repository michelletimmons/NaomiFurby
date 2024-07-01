# -*- coding: utf-8 -*-
import pipes
from naomi import plugin
from naomi.run_command import run_command

class PiperTTSPlugin(plugin.TTSPlugin):
    # The only methods you have to define here are "get_voices" and "say"

    # The get_voices method takes no parameters and returns a list of voices.
    # Not really sure why/if we need this
    def get_voices(self):
        voices = [
            "English - Alan"
        ]
        return voices

    # The "say" method has two parameters:
    #   phrase (required) - a phrase to be spoken
    #   voice (optional) - a voice to be used. If None, then use the default.
    def say(self, phrase, voice=None):

        # cmd = [
        #     'espeak',
        #     '--stdin',
        #     '--stdout'
        # ]

        cmd = [
            'piper',
            '--model',
            '/home/pi/piper/en_GB-alan-low.onnx',
            '--output_file',
            '-'
        ]

        cmd = [str(x) for x in cmd]
        self._logger.debug(
            'Executing %s', ' '.join(
                [pipes.quote(arg) for arg in cmd]
            )
        )
        data = run_command(cmd, 4, phrase).stdout

        return data
