import subprocess
import re
import os
from Xlib.display import Display
from typing import Tuple, Optional
from xdg.DesktopEntry import DesktopEntry

from fishy.osservices.os_services import IOSServices

class Linux(IOSServices):
    WINDOW_TITLE = 'Terminal'
    DESKTOP_FILE_PATH = os.path.expanduser("~/Desktop/Fishybot ESO.desktop")
    ESO_WINDOW_NAME = "Elder Scrolls Online"

    def hide_terminal(self):
        """Hide the terminal window."""
        command = f'wmctrl -r "{self.WINDOW_TITLE}" -b add,hidden'
        subprocess.run(command, shell=True, check=True)

    def create_shortcut(self, anti_ghosting=False):
        """Create a desktop shortcut for the application."""
        try:
            shortcut = DesktopEntry(self.DESKTOP_FILE_PATH)
            shortcut.set("Type", "Application")
            shortcut.set("Exec", "/usr/bin/python3 -m fishy")
            shortcut.set("Icon", "icon.png")  # TODO: Fix icon address
            shortcut.write()
            print("Shortcut created")
        except Exception as e:
            print(f"Couldn't create shortcut: {e}")

    def get_documents_path(self) -> str:
        """Return the path to the user's Documents directory."""
        return os.path.join(os.path.expanduser('~'), "Documents")

    def is_admin(self) -> bool:
        """Check if the current user has admin privileges."""
        return os.geteuid() == 0

    def get_eso_config_path(self) -> str:
        """Return the path to the ESO configuration directory."""
        return os.path.join(self.get_documents_path(), "Elder Scrolls Online")

    def is_eso_active(self) -> bool:
        """Check if the Elder Scrolls Online is the active window."""
        d = Display()
        root = d.screen().root
        window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), display.X.AnyPropertyType).value[0]
        window = d.create_resource_object('window', window_id)
        return window.get_wm_name() == self.ESO_WINDOW_NAME

    def get_monitor_rect(self):
        """Get the monitor's resolution and position."""
        try:
            output = subprocess.check_output(["xrandr"]).decode("utf-8")
            matches = re.findall(r"(\d+)x(\d+)\+(\d+)\+(\d+)", output)
            if matches:
                width, height, x, y = matches[0]
                return {
                    "width": int(width),
                    "height": int(height),
                    "x": int(x),
                    "y": int(y)
                }
            else:
                return None
        except subprocess.CalledProcessError:
            return None

    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Return the dimensions of the Elder Scrolls Online game window."""
        d = Display()
        root = d.screen().root
        window_id = None

        # Find the window with the specified name
        for window in root.query_tree().children:
            if window.get_wm_name() == self.ESO_WINDOW_NAME:
                window_id = window.id
                break

        if window_id is None:
            return None

        window_rect = window.get_geometry()
        return (
            window_rect.x,
            window_rect.y,
            window_rect.x + window_rect.width,
            window_rect.y + window_rect.height
        )
