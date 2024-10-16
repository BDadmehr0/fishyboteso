import logging
import time
from threading import Thread
from typing import Dict, Optional, Callable

from playsound import playsound

from fishy import helper
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
        self._hotkeys: Dict[Key, Optional[Callable]] = dict([(k, None) for k in Key])
        self.running = True
        self.process = Thread(target=process.run, args=(self._hotkeys,))
        self.event = Thread(target=self._event_loop)

    def hook(self, key: Key, func: Callable):
        self._hotkeys[key] = func

    def free(self, key: Key):
        self._hotkeys[key] = None

    def _event_loop(self):
        while self.running:
            key = process.get_next_key()
            if key in Key:
                callback = self._hotkeys[key]
                if callback:
                    playsound(helper.manifest_file("beep.wav"), False)
                    callback()
            time.sleep(0.1)

    def start(self):
        self.process.start()
        self.event.start()
        logging.debug("hotkey process started")

    def stop(self):
        self.running = False
        self.process.join()
        self.event.join()
        logging.debug("hotkey process ended")
