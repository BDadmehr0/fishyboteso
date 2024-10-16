import logging
import time
from multiprocessing import Process, Queue
from threading import Thread
from typing import Dict, Optional, Callable
import requests
from playsound import playsound
import os

from fishy import helper
from fishy.helper.config import config
from fishy.helper.hotkey import process
from fishy.helper.hotkey.process import Key

class hotkey:
    instance: 'HotKey' = None

    @staticmethod
    def init():
        if not hotkey.instance:
            hotkey.instance = HotKey()

    @staticmethod
    def hook(key: Key, func: Callable):
        hotkey.instance.hook(key, func)

    @staticmethod
    def free(key: Key):
        hotkey.instance.free(key)

    @staticmethod
    def start():
        hotkey.instance.start()

    @staticmethod
    def stop():
        hotkey.instance.stop()


class HotKey:
    def __init__(self):
        self.inq = Queue()
        self.outq = Queue()

        self._hotkeys: Dict[Key, Optional[Callable]] = dict([(k, None) for k in Key])

        self.process = Thread(target=process.run, args=(self.inq, self.outq))
        self.event = Thread(target=self._event_loop)

    def hook(self, key: Key, func: Callable):
        self._hotkeys[key] = func

    def free(self, key: Key):
        self._hotkeys[key] = None

    def _event_loop(self):
        while True:
            key = self.outq.get()

            if key == "stop":
                break

            if key in Key:
                callback = self._hotkeys[key]
                if callback:
                    if config.get("sound_notification", False):
                        # Change here to use a web URL for the sound
                        sound_url = "https://raw.githubusercontent.com/fishyboteso/fishyboteso/main/fishy/beep.wav"
                        try:
                            self.play_sound_from_url(sound_url)
                        except Exception as e:
                            logging.error(f"Failed to play sound from URL: {e}")

                    callback()

            time.sleep(0.1)

    def play_sound_from_url(self, url: str):
        # Download sound file from the URL
        response = requests.get(url)
        if response.status_code == 200:
            with open("temp_sound.wav", "wb") as f:
                f.write(response.content)

            playsound("temp_sound.wav")

            # Clean up temporary file
            os.remove("temp_sound.wav")
        else:
            logging.error(f"Failed to download sound file, status code: {response.status_code}")

    def start(self):
        self.process.start()
        self.event.start()
        logging.debug("hotkey process started")

    def stop(self):
        self.inq.put("stop")
        self.outq.put("stop")
        logging.debug("hotkey process ended")
