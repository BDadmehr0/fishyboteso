"""
config.py
Saves configuration in file as json file
"""
import json
import logging
import os
import platform
from typing import Optional
from event_scheduler import EventScheduler
from fishy.osservices.os_services import os_services

def filename():
    name = "fishy_config.json"
    _filename = os.path.join(os.environ.get("HOMEDRIVE", ""), os.environ.get("HOMEPATH", ""), "Documents", name)
    if os.path.exists(_filename):
        return _filename
        
    return os.path.join(os_services.get_documents_path(), name)

# Determine temp file location based on OS
if platform.system() == "Windows":
    temp_file = os.path.join(os.environ.get("TEMP", ""), "fishy_config.BAK")
else:
    temp_file = os.path.join(os.getenv("TMPDIR", "/tmp"), "fishy_config.BAK")

class Config:
    def __init__(self):
        self._config_dict: Optional[dict] = None
        self._scheduler: Optional[EventScheduler] = None

    def __getitem__(self, item):
        return self._config_dict.get(item)

    def __setitem__(self, key, value):
        self._config_dict[key] = value

    def __delitem__(self, key):
        del self._config_dict[key]

    def initialize(self):
        self._scheduler = EventScheduler()
        if os.path.exists(filename()):
            try:
                with open(filename()) as f:
                    self._config_dict = json.load(f)
            except json.JSONDecodeError:
                try:
                    logging.warning("Config file got corrupted, trying to restore backup")
                    with open(temp_file) as f:
                        self._config_dict = json.load(f)
                    self.save_config()
                except (FileNotFoundError, json.JSONDecodeError):
                    logging.warning("Couldn't restore, creating new")
                    os.remove(filename())
                    self._config_dict = dict()
        else:
            self._config_dict = dict()
        logging.debug("config initialized")

    def start_backup_scheduler(self):
        self._create_backup()
        self._scheduler.start()
        self._scheduler.enter_recurring(5 * 60, 1, self._create_backup)
        logging.debug("scheduler started")

    def stop(self):
        self._scheduler.stop(True)
        logging.debug("config stopped")

    def _create_backup(self):
        with open(temp_file, 'w') as f:
            f.write(json.dumps(self._config_dict))
        logging.debug("created backup")

    def _sort_dict(self):
        self._config_dict = dict(sorted(self._config_dict.items()))

    def save_config(self):
        self._sort_dict()
        with open(filename(), 'w') as f:
            f.write(json.dumps(self._config_dict))

class config:
    _instance = None

    @staticmethod
    def init():
        if not config._instance:
            config._instance = Config()
            config._instance.initialize()

    @staticmethod
    def start_backup_scheduler():
        config._instance.start_backup_scheduler()

    @staticmethod
    def stop():
        config._instance.stop()

    @staticmethod
    def get(key, default=None):
        return default if config._instance is None or config._instance[key] is None else config._instance[key]

    @staticmethod
    def set(key, value, save=True):
        if config._instance is None:
            return

        config._instance[key] = value
        if save:
            config.save_config()

    @staticmethod
    def delete(key):
        try:
            del config._instance[key]
            config.save_config()
        except KeyError:
            pass

    @staticmethod
    def save_config():
        if config._instance is None:
            return
        config._instance.save_config()
